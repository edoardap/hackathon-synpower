import fcntl
import io
import json
import os
import tempfile
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from unittest import mock
from urllib.error import HTTPError

from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

from observability.adapters import hook
from observability.tracing import envio
from observability.tracing.redacao import MARCA_TRUNCADO, redigir, sanear, valores_secretos
from observability.tracing.turno import Span

FIXTURE = Path(__file__).parent / "fixtures" / "claude-code.jsonl"
SEGREDO = "tok-ABCDEF123456"
MORTO = "http://127.0.0.1:9/v1/traces"
CONTEUDO = {"input.value", "output.value", "gen_ai.prompt", "gen_ai.completion", "opik.metadata.artifact.code"}


class RedacaoTest(unittest.TestCase):
    def test_valores_do_ambiente_so_com_sufixo_secreto_e_8_ou_mais_caracteres(self):
        env = {"API_TOKEN": SEGREDO, "DB_PASSWORD": "curta", "DISCORD_ATTACH": "12345678", "X_KEY": "chave-longa"}
        self.assertEqual(valores_secretos(env), {SEGREDO, "chave-longa"})

    def test_redige_valor_do_env_e_padrao_de_token(self):
        texto = f"a {SEGREDO} b ghp_{'a' * 36} c"
        self.assertEqual(redigir(texto, {SEGREDO}), "a [REDIGIDO] b [REDIGIDO] c")

    def test_bloco_de_chave_privada_e_redigido_inteiro_em_texto_puro_e_em_json(self):
        pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA\nabc123\n-----END RSA PRIVATE KEY-----"
        for texto in (f"antes\n{pem}\ndepois", json.dumps({"saida": f"antes\n{pem}\ndepois"})):
            r = redigir(texto, set())
            self.assertNotIn("MIIEow", r)
            self.assertIn("[REDIGIDO]", r)
            self.assertIn("depois", r)

    def test_chave_privada_sem_fim_e_redigida_ate_o_fim_do_texto(self):
        self.assertEqual(redigir("a -----BEGIN PRIVATE KEY-----\nMIIE\nabc", set()), "a [REDIGIDO]")

    def test_valor_do_env_com_aspas_e_barra_e_redigido_na_forma_serializada_em_json(self):
        valor = 'se"gre\\do-123'
        r = redigir(json.dumps({"saida": f"x {valor} y"}), {valor})
        self.assertNotIn("gre", r)

    def test_valor_curto_nao_e_redigido(self):
        env = {"API_TOKEN": "abc", "DISCORD_ATTACH": "1"}
        self.assertEqual(redigir("abc 1 abc", valores_secretos(env)), "abc 1 abc")

    def test_sanear_redige_conteudo_e_preserva_estrutura(self):
        raiz = Span("turno", 1, 2, entrada=f"use {SEGREDO}", filhos=[Span("Bash", 1, 2, saida=SEGREDO, codigo=SEGREDO)])
        s = sanear(raiz, {SEGREDO}, metadado=False)
        self.assertEqual((s.entrada, s.filhos[0].saida, s.filhos[0].codigo), ("use [REDIGIDO]", "[REDIGIDO]", "[REDIGIDO]"))
        self.assertEqual(raiz.entrada, f"use {SEGREDO}")

    def test_modo_metadado_corta_todo_o_texto_e_mantem_nome_e_status(self):
        leitura = Span("Read", 3, 4, entrada="x", saida="y", codigo="z", erro=True)
        s = sanear(Span("turno", 1, 2, entrada="pedido", saida="resposta", filhos=[leitura]), [], metadado=True)
        r = s.filhos[0]
        self.assertEqual((s.entrada, s.saida, r.entrada, r.saida, r.codigo), (None,) * 5)
        self.assertEqual((r.nome, r.fim - r.inicio, r.erro), ("Read", 1, True))


class TruncamentoTest(unittest.TestCase):
    def test_codigo_acima_do_limite_vira_o_inicio_com_marcador(self):
        s = sanear(Span("turno", 1, 2, codigo="abcdefghij"), [], metadado=False, limite=4)
        self.assertEqual(s.codigo, "abcd" + MARCA_TRUNCADO)

    def test_limite_em_bytes_nao_parte_caractere_multibyte(self):
        s = sanear(Span("turno", 1, 2, codigo="ééé"), [], metadado=False, limite=3)
        self.assertEqual(s.codigo, "é" + MARCA_TRUNCADO)

    def test_surrogate_solto_nao_levanta_no_corte(self):
        s = sanear(Span("turno", 1, 2, codigo="a\ud800bcdef"), [], metadado=False, limite=4)
        self.assertEqual(s.codigo, "a?bc" + MARCA_TRUNCADO)

    def test_codigo_no_limite_ou_abaixo_fica_inteiro(self):
        self.assertEqual(sanear(Span("t", 1, 2, codigo="abcd"), [], False, limite=4).codigo, "abcd")

    def test_conteudo_do_chat_e_cortado_depois_da_redacao_e_o_da_ferramenta_nao(self):
        chat = Span("chat", 1, 2, entrada="abcdefghij", saida=f"x {SEGREDO}")
        ferramenta = Span("Bash", 1, 2, entrada="abcdefghij", saida="abcdefghij")
        s = sanear(Span("turno", 1, 2, filhos=[chat, ferramenta]), {SEGREDO}, metadado=False, limite=4)
        self.assertEqual((s.filhos[0].entrada, s.filhos[0].saida), ("abcd" + MARCA_TRUNCADO, "x [R" + MARCA_TRUNCADO))
        self.assertEqual((s.filhos[1].entrada, s.filhos[1].saida), ("abcdefghij",) * 2)

    def test_segredo_e_redigido_antes_do_corte(self):
        s = sanear(Span("turno", 1, 2, codigo=f"x = '{SEGREDO}'"), {SEGREDO}, metadado=False, limite=12)
        self.assertEqual(s.codigo, "x = '[REDIGI" + MARCA_TRUNCADO)

    def test_limite_vem_de_obs_artifact_max_com_padrao_de_20000_bytes(self):
        base = {"OBS_OTLP_ENDPOINT": "http://x"}
        self.assertEqual(envio.configuracao(base, Path("/c")).artefato_max, 20000)
        self.assertEqual(envio.configuracao({**base, "OBS_ARTIFACT_MAX": "50"}, Path("/c")).artefato_max, 50)
        self.assertEqual(envio.configuracao({**base, "OBS_ARTIFACT_MAX": "muito"}, Path("/c")).artefato_max, 20000)


def enviar(turno, config):
    envio.enfileirar(turno, config)
    return envio.reenviar(config)


class Receptor:
    """Servidor OTLP/HTTP local: guarda cada requisição e responde com o próximo de `fila`, ou com `status`."""

    def __init__(self):
        self.status, self.recebidos, self.fila = 200, [], []
        receptor = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                req = ExportTraceServiceRequest()
                req.ParseFromString(self.rfile.read(int(self.headers["Content-Length"])))
                receptor.recebidos.append((self.path, dict(self.headers), req))
                self.send_response(receptor.fila.pop(0) if receptor.fila else receptor.status)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, *a):
                pass

        self.servidor = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.servidor.server_port}/v1/traces"
        Thread(target=self.servidor.serve_forever, args=(0.01,), daemon=True).start()

    def spans(self, i=0):
        return [s for rs in self.recebidos[i][2].resource_spans for ss in rs.scope_spans for s in ss.spans]

    def fechar(self):
        self.servidor.shutdown()
        self.servidor.server_close()


def atributos(span):
    return {a.key: a.value for a in span.attributes}


def turno(n=0):
    uso = {"gen_ai.request.model": "m", "gen_ai.usage.input_tokens": 10, "gen_ai.usage.output_tokens": 4}
    sub = Span("Agent", 4, 9, filhos=[Span("Read", 5, 6, entrada="a.txt", saida="conteudo")])
    return Span("turno", 1, 10, {"thread_id": "sessao-1", "opik.tags": ["code_written"], "n": n}, entrada="pedido",
                saida="resposta", codigo="print(1)", filhos=[Span("chat", 2, 3, uso), Span("Bash", 3, 4, erro=True), sub])


def config(url, spool, headers=None, valores=(), metadado=False):
    return envio.Config(url=url, headers=headers or {}, valores=set(valores), metadado=metadado, spool=Path(spool))


class EnvioTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.spool = Path(self.tmp.name) / "spool"
        self.rec = Receptor()
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(self.rec.fechar)

    def cfg(self, **kw):
        return config(self.rec.url, self.spool, **kw)

    def arquivos(self):
        return sorted(self.spool.glob("*"))

    def test_exporta_a_arvore_com_atributos_e_cabecalhos(self):
        cabecalhos = {"Authorization": "chave", "Comet-Workspace": "ws", "projectName": "ras"}
        self.assertTrue(enviar(turno(), self.cfg(headers=cabecalhos)))
        caminho, headers, _ = self.rec.recebidos[0]
        self.assertEqual(caminho, "/v1/traces")
        headers = {k.lower(): v for k, v in headers.items()}
        self.assertEqual({k: headers[k.lower()] for k in cabecalhos}, cabecalhos)
        spans = {s.name: s for s in self.rec.spans()}
        self.assertEqual(set(spans), {"turno", "chat", "Bash", "Agent", "Read"})
        self.assertEqual(spans["Agent"].parent_span_id, spans["turno"].span_id)
        self.assertEqual(spans["Read"].parent_span_id, spans["Agent"].span_id)
        self.assertEqual(spans["turno"].parent_span_id, b"")
        raiz = atributos(spans["turno"])
        self.assertEqual(raiz["thread_id"].string_value, "sessao-1")
        self.assertEqual(raiz["opik.tags"].array_value.values[0].string_value, "code_written")
        self.assertEqual(raiz["opik.metadata.artifact.code"].string_value, "print(1)")
        self.assertEqual(raiz["gen_ai.prompt"].string_value, "pedido")
        self.assertEqual(atributos(spans["chat"])["gen_ai.usage.input_tokens"].int_value, 10)
        self.assertEqual(atributos(spans["Read"])["input.value"].string_value, "a.txt")
        self.assertEqual(spans["Bash"].status.code, 2)
        self.assertEqual((spans["turno"].start_time_unix_nano, spans["turno"].end_time_unix_nano), (1, 10))
        self.assertEqual(self.arquivos(), [])

    def test_destino_recusado_guarda_no_spool_e_o_proximo_turno_reenvia(self):
        self.assertFalse(enviar(turno(1), config(MORTO, self.spool)))
        self.assertEqual(len(self.arquivos()), 1)
        self.assertTrue(enviar(turno(2), self.cfg()))
        enviados = [atributos(s)["n"].int_value for i in range(2) for s in self.rec.spans(i) if s.name == "turno"]
        self.assertEqual(enviados, [1, 2])
        self.assertEqual(self.arquivos(), [])

    def test_resposta_de_erro_tambem_vai_para_o_spool(self):
        self.rec.status = 500
        self.assertFalse(enviar(turno(), self.cfg()))
        self.assertEqual(len(self.arquivos()), 1)

    def test_recusa_fica_em_erros_log_com_o_status_e_a_conexao_recusada_tambem(self):
        self.rec.status = 500
        enviar(turno(), self.cfg())
        enviar(turno(), config(MORTO, self.spool))
        log = (self.spool.parent / "erros.log").read_text()
        self.assertIn("HTTP 500", log)
        self.assertIn("Connection refused", log)
        self.assertIn("sessao-1", log)

    def test_recusa_do_corpo_sai_do_spool_e_nao_trava_o_proximo(self):
        for status in (400, 413, 422):  # 400: janela de 24 h do Opik, "too_old"
            with self.subTest(status=status):
                self.rec.fila = [status]
                envio.guardar(turno(1), self.cfg())
                envio.guardar(turno(2), self.cfg())
                self.assertTrue(envio.reenviar(self.cfg()))
                self.assertEqual(self.arquivos(), [])
                self.assertIn(f"HTTP {status}", (self.spool.parent / "erros.log").read_text())
        self.assertEqual(len(self.rec.recebidos), 6)

    def test_recusa_que_pode_passar_depois_fica_no_spool_e_para_o_reenvio(self):
        envio.guardar(turno(), self.cfg())
        for status in (401, 403, 404, 408, 429, 500):
            self.rec.status = status
            with self.subTest(status=status):
                self.assertFalse(envio.reenviar(self.cfg()))
                self.assertEqual(len(self.arquivos()), 1)

    def test_corpo_ilegivel_da_recusa_nao_vira_excecao(self):
        recusa = HTTPError(self.rec.url, 500, "x", {}, mock.Mock(read=mock.Mock(side_effect=TimeoutError)))
        with mock.patch.object(envio, "urlopen", side_effect=recusa):
            self.assertFalse(enviar(turno(), self.cfg()))
        self.assertIn("HTTP 500 x", (self.spool.parent / "erros.log").read_text())

    def test_valor_do_env_no_corpo_da_recusa_vai_redigido_ao_log(self):
        recusa = HTTPError(self.rec.url, 400, "x", {}, io.BytesIO(f"token={SEGREDO}".encode()))
        with mock.patch.object(envio, "urlopen", side_effect=recusa):
            enviar(turno(), self.cfg(valores={SEGREDO}))
        log = (self.spool.parent / "erros.log").read_text()
        self.assertIn("HTTP 400 x", log)
        self.assertNotIn(SEGREDO, log)

    def test_reenviar_so_do_spool_no_fim_da_sessao(self):
        envio.guardar(turno(), self.cfg())
        self.assertTrue(envio.reenviar(self.cfg()))
        self.assertEqual((len(self.rec.recebidos), self.arquivos()), (1, []))

    def test_reenviar_para_no_primeiro_recuso_e_mantem_o_resto(self):
        envio.guardar(turno(1), self.cfg())
        envio.guardar(turno(2), self.cfg())
        self.assertFalse(envio.reenviar(config(MORTO, self.spool)))
        self.assertEqual(len(self.arquivos()), 2)

    def test_arquivo_ilegivel_do_spool_e_descartado(self):
        self.spool.mkdir()
        (self.spool / "0-x.json").write_text("{corrompido")
        self.assertTrue(envio.reenviar(self.cfg()))
        self.assertEqual(self.arquivos(), [])

    def test_spool_grava_com_os_replace_e_nao_deixa_arquivo_parcial(self):
        with mock.patch.object(envio.os, "replace", wraps=os.replace) as troca:
            envio.guardar(turno(), self.cfg())
        origem, destino = map(Path, troca.call_args.args)
        self.assertEqual((destino.parent, destino.suffix, origem.suffix), (self.spool, ".json", ".tmp"))
        with mock.patch.object(envio.os, "replace", side_effect=OSError):
            with self.assertRaises(OSError):
                envio.guardar(turno(), self.cfg())
        self.assertEqual(len(self.arquivos()), 1)

    def test_spool_descarta_os_mais_antigos_acima_do_limite(self):
        with mock.patch.object(envio, "LIMITE_SPOOL", 3):
            for n in range(5):
                envio.guardar(turno(n), self.cfg())
        ns = [json.loads(f.read_text())["atributos"]["n"] for f in self.arquivos()]
        self.assertEqual(ns, [2, 3, 4])

    def test_valor_do_env_na_saida_da_ferramenta_vai_redigido_ao_destino_e_ao_spool(self):
        raiz = Span("turno", 1, 2, filhos=[Span("Bash", 1, 2, saida=f"token={SEGREDO}")])
        enviar(raiz, self.cfg(valores={SEGREDO}))
        self.assertEqual(atributos(self.rec.spans()[0])["output.value"].string_value, "token=[REDIGIDO]")
        self.rec.status = 500
        enviar(raiz, self.cfg(valores={SEGREDO}))
        self.assertNotIn(SEGREDO, self.arquivos()[0].read_text())

    def test_modo_metadado_exporta_nome_status_e_duracao_sem_conteudo(self):
        enviar(turno(), self.cfg(metadado=True))
        for s in self.rec.spans():
            self.assertFalse(CONTEUDO & atributos(s).keys(), s.name)
        self.assertEqual({s.name for s in self.rec.spans()}, {"turno", "chat", "Bash", "Agent", "Read"})


class ConfiguracaoTest(unittest.TestCase):
    def test_sem_endpoint_nao_ha_configuracao_nem_arquivo(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(envio.configuracao({"OPIK_API_KEY": "x"}, Path(d)))
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_cabecalhos_do_opik_so_com_chave(self):
        env = {"OBS_OTLP_ENDPOINT": "https://outro:4318/", "OPIK_API_KEY": "k", "OPIK_WORKSPACE": "w", "OBS_PROJECT": "p"}
        c = envio.configuracao(env, Path("/c"))
        self.assertEqual(c.url, "https://outro:4318/v1/traces")
        self.assertEqual(c.headers, {"Authorization": "k", "Comet-Workspace": "w", "projectName": "p"})
        self.assertEqual(envio.configuracao({"OBS_OTLP_ENDPOINT": "http://x"}, Path("/c")).headers, {})

    def test_chave_nao_sai_em_http_para_host_remoto_mas_sai_em_https_e_em_loopback(self):
        ambiente = {"OPIK_API_KEY": "k"}
        for url, com_chave in (("http://remoto:4318", False), ("https://remoto", True),
                               ("http://127.0.0.1:4318", True), ("http://localhost:4318", True)):
            c = envio.configuracao({**ambiente, "OBS_OTLP_ENDPOINT": url}, Path("/c"))
            self.assertEqual(bool(c.headers), com_chave, url)

    def test_modo_metadado_e_valores_secretos_vem_do_ambiente(self):
        env = {"OBS_OTLP_ENDPOINT": "http://x", "OBS_CONTENT": "metadata", "A_TOKEN": SEGREDO}
        c = envio.configuracao(env, Path("/c"))
        self.assertEqual((c.metadado, c.valores, c.spool), (True, {SEGREDO}, Path("/c/spool")))


class HookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = Path(self.tmp.name) / "observability"
        self.rec = Receptor()
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(self.rec.fechar)
        self.endpoint = self.rec.url.removesuffix("/v1/traces")

    def rodar(self, evento, transcript=FIXTURE, **env):
        payload = json.dumps({"session_id": "s1", "transcript_path": str(transcript), "hook_event_name": evento})
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(hook, "CACHE", self.cache):
            with mock.patch("sys.stdin", io.StringIO(payload)):
                hook.main("claude-code")

    def raizes(self):
        return [next(s for s in self.rec.spans(i) if s.name == "turno") for i in range(len(self.rec.recebidos))]

    def spool(self):
        return sorted((self.cache / "spool").glob("*.json"))

    def test_sem_endpoint_nao_envia_nem_grava(self):
        self.rodar("Stop")
        self.assertEqual((self.rec.recebidos, self.cache.exists()), ([], False))

    def test_stop_exporta_um_trace_por_turno_com_o_mesmo_thread_id(self):
        self.rodar("Stop", OBS_OTLP_ENDPOINT=self.endpoint)
        primeiro, segundo = self.raizes()
        for raiz in (primeiro, segundo):
            self.assertEqual(atributos(raiz)["thread_id"].string_value, "s1")
            self.assertEqual(atributos(raiz)["ras.executor"].string_value, "claude-code")
        self.assertEqual(atributos(primeiro)["gen_ai.prompt"].string_value, "Crie o script de exemplo e leia a chave.")
        self.assertEqual(atributos(segundo)["gen_ai.completion"].string_value, "ok")

    def test_disparos_seguintes_da_sessao_nao_repetem_turnos(self):
        self.rodar("Stop", OBS_OTLP_ENDPOINT=self.endpoint)
        self.rodar("Stop", OBS_OTLP_ENDPOINT=self.endpoint)
        self.rodar("SessionEnd", OBS_OTLP_ENDPOINT=self.endpoint)
        self.assertEqual(len(self.rec.recebidos), 2)
        self.assertEqual((self.cache / "offsets" / "s1").read_text(), "17")

    def test_session_end_le_a_partir_do_offset_quando_o_stop_foi_cancelado(self):
        self.rodar("SessionEnd", OBS_OTLP_ENDPOINT=self.endpoint)
        self.assertEqual(len(self.raizes()), 2)
        self.rodar("SessionEnd", OBS_OTLP_ENDPOINT=self.endpoint)
        self.assertEqual(len(self.rec.recebidos), 2)

    def test_destino_fora_do_ar_guarda_e_o_session_end_reenvia(self):
        self.rodar("Stop", OBS_OTLP_ENDPOINT="http://127.0.0.1:9")
        self.assertEqual(len(self.spool()), 2)
        self.rodar("SessionEnd", OBS_OTLP_ENDPOINT=self.endpoint)
        self.assertEqual((len(self.rec.recebidos), self.spool()), (2, []))

    def test_tag_e_codigo_so_no_turno_que_escreveu_e_codigo_truncado_no_limite(self):
        self.rodar("Stop", OBS_OTLP_ENDPOINT=self.endpoint, OBS_ARTIFACT_MAX="10")
        escreveu, leu = map(atributos, self.raizes())
        self.assertEqual(escreveu["opik.tags"].array_value.values[0].string_value, "code_written")
        self.assertEqual(escreveu["opik.metadata.artifact.code"].string_value, "# /ws/exem\n[TRUNCADO]")
        self.assertNotIn("opik.tags", leu)
        self.assertNotIn("opik.metadata.artifact.code", leu)

    def test_modo_metadado_mantem_a_tag_e_omite_pedido_resposta_e_codigo(self):
        self.rodar("Stop", OBS_OTLP_ENDPOINT=self.endpoint, OBS_CONTENT="metadata")
        escreveu = atributos(self.raizes()[0])
        self.assertIn("opik.tags", escreveu)
        self.assertFalse(CONTEUDO & escreveu.keys())

    def test_corte_no_meio_do_envio_ja_deixou_offset_e_spool_e_o_proximo_disparo_entrega_uma_vez(self):
        with mock.patch.object(envio, "exportar", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.rodar("SessionEnd", OBS_OTLP_ENDPOINT=self.endpoint)
        self.assertEqual(((self.cache / "offsets" / "s1").read_text(), len(self.spool())), ("17", 2))
        self.rodar("SessionEnd", OBS_OTLP_ENDPOINT=self.endpoint)
        self.assertEqual((len(self.raizes()), self.spool()), (2, []))

    def test_a_trava_da_sessao_impede_outro_disparo_ao_mesmo_tempo(self):
        with mock.patch.object(hook, "CACHE", self.cache), hook.travada("s1"):
            with open(self.cache / "locks" / "s1.lock", "w") as outro:
                with self.assertRaises(BlockingIOError):
                    fcntl.flock(outro, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with open(self.cache / "locks" / "s1.lock", "w") as livre:
            fcntl.flock(livre, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def test_offset_e_gravado_com_os_replace(self):
        with mock.patch.object(hook, "CACHE", self.cache), mock.patch.object(hook.os, "replace", wraps=os.replace) as troca:
            hook.gravar_offset("s1", 5)
        origem, destino = map(Path, troca.call_args.args)
        self.assertEqual((destino, origem.suffix, destino.read_text()), (self.cache / "offsets" / "s1", ".tmp", "5"))


if __name__ == "__main__":
    unittest.main()
