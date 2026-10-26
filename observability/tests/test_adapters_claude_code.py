import json
import shutil
import tempfile
import unittest
from pathlib import Path

from observability.adapters.claude_code import ler_turnos

FIXTURES = Path(__file__).parent / "fixtures"
AGENTE = "a1b2c3d4e5f607182"
ATRIBUTOS_SEM_CONTEUDO = {
    "gen_ai.request.model", "gen_ai.usage.input_tokens", "gen_ai.usage.output_tokens", "gen_ai.system",
    "gen_ai.provider.name", "opik.tags",
    "gen_ai.usage.cache_read.input_tokens", "gen_ai.usage.cache_creation.input_tokens",
    "opik.metadata.agent_type", "opik.metadata.fase", "opik.metadata.change", "opik.metadata.grupo",
    "opik.metadata.foco",
}


def sessao(tmp, fixture="claude-code.jsonl", subagente=True):
    """Copia a fixture para o layout do Claude Code: <sessão>.jsonl e <sessão>/subagents/agent-<id>.jsonl."""
    transcript = Path(tmp) / "sessao.jsonl"
    shutil.copy(FIXTURES / fixture, transcript)
    if subagente:
        pasta = Path(tmp) / "sessao" / "subagents"
        pasta.mkdir(parents=True)
        shutil.copy(FIXTURES / f"claude-code-subagent-agent-{AGENTE}.jsonl", pasta / f"agent-{AGENTE}.jsonl")
    return transcript


def nomes(span):
    return [f.nome for f in span.filhos]


def percorrer(span):
    yield span
    for f in span.filhos:
        yield from percorrer(f)


class LeitorClaudeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.transcript = sessao(self.tmp.name)

    def turnos(self, offset=0):
        return ler_turnos(self.transcript, offset)

    def test_turno_com_ferramentas_e_subagente_aninhado(self):
        (primeiro, _), _ = self.turnos()
        self.assertEqual(
            nomes(primeiro),
            ["chat", "Bash", "chat", "agent:ciclo-revisor-fase", "chat", "Write", "chat", "Read", "chat"],
        )
        agente = primeiro.filhos[3]
        self.assertEqual(nomes(agente), ["chat", "Read", "chat"])
        self.assertEqual(agente.filhos[1].entrada, json.dumps({"file_path": "/ws/README.md"}))
        self.assertEqual(agente.filhos[1].saida, "linha inventada")

    def test_pedido_vira_entrada_e_resposta_final_saida_do_turno(self):
        (primeiro, segundo), _ = self.turnos()
        self.assertEqual((primeiro.entrada, primeiro.saida), ("Crie o script de exemplo e leia a chave.", "Feito."))
        self.assertEqual((segundo.entrada, segundo.saida), ("Obrigado, agora só responda ok.", "ok"))
        self.assertEqual((primeiro.inicio, primeiro.fim), (1767261601 * 10**9, 1767261611 * 10**9))

    def test_tokens_por_chamada_ao_modelo_sem_repetir_a_mensagem(self):
        (primeiro, _), _ = self.turnos()
        usos = [(c.atributos["gen_ai.usage.input_tokens"], c.atributos["gen_ai.usage.output_tokens"])
                for c in primeiro.filhos if c.nome == "chat"]
        self.assertEqual(usos, [(152, 40), (153, 30), (164, 25), (175, 20), (186, 10)])
        self.assertEqual(primeiro.filhos[0].atributos["gen_ai.request.model"], "claude-modelo-ficticio")
        self.assertEqual(primeiro.atributos["gen_ai.request.model"], "claude-modelo-ficticio")

    def test_cache_vai_em_atributos_proprios_e_o_total_de_entrada_continua_o_mesmo(self):
        (primeiro, _), _ = self.turnos()
        a = primeiro.filhos[0].atributos
        self.assertEqual(
            (a["gen_ai.usage.input_tokens"], a["gen_ai.usage.cache_read.input_tokens"],
             a["gen_ai.usage.cache_creation.input_tokens"]), (152, 100, 50))

    def test_chamada_ao_modelo_leva_o_que_recebeu_e_o_que_respondeu(self):
        (primeiro, segundo), _ = self.turnos()
        chats = [f for f in primeiro.filhos if f.nome == "chat"]
        self.assertEqual([c.entrada for c in chats], [
            "Crie o script de exemplo e leia a chave.", "ok", "iniciado", "criado", chats[4].entrada])
        self.assertIn("politica de segredos", chats[4].entrada)
        self.assertEqual([c.saida for c in chats], ["→ Bash", "→ Agent", "→ Write", "→ Read", "Feito."])
        resposta = segundo.filhos[0]
        self.assertEqual((resposta.entrada, resposta.saida), ("Obrigado, agora só responda ok.", "ok"))

    def test_chamada_do_subagente_leva_o_pedido_e_o_resultado_da_ferramenta(self):
        (primeiro, _), _ = self.turnos()
        primeira, _, segunda = primeiro.filhos[3].filhos
        self.assertEqual((primeira.entrada, primeira.saida), ("Leia o README", "→ Read"))
        self.assertEqual((segunda.entrada, segunda.saida), ("linha inventada", "Primeira linha."))

    def test_chamada_de_subagente_leva_o_tipo_no_nome_e_os_campos_do_despacho(self):
        (primeiro, _), _ = self.turnos()
        agente = primeiro.filhos[3]
        self.assertEqual(agente.nome, "agent:ciclo-revisor-fase")
        self.assertEqual(agente.atributos, {
            "opik.metadata.agent_type": "ciclo-revisor-fase", "opik.metadata.fase": "fase",
            "opik.metadata.change": "ras-observabilidade-opik", "opik.metadata.grupo": "4", "opik.metadata.foco": "qa",
        })

    def test_todo_span_do_subagente_leva_o_tipo_e_o_do_principal_nao(self):
        (primeiro, _), _ = self.turnos()
        for span in list(percorrer(primeiro.filhos[3]))[1:]:
            self.assertEqual(span.atributos["opik.metadata.agent_type"], "ciclo-revisor-fase", span.nome)
        for span in primeiro.filhos[:3] + primeiro.filhos[4:]:
            self.assertNotIn("opik.metadata.agent_type", span.atributos, span.nome)

    def test_agente_aninhado_mantem_o_proprio_tipo(self):
        def registro(tipo, ts, mid, conteudo, **extra):
            return {"type": tipo, "timestamp": ts, "message": {"id": mid, "content": conteudo,
                    "usage": {"input_tokens": 1, "output_tokens": 1}}, **extra}

        def pedido(ts, texto):
            return {"type": "user", "timestamp": ts, "message": {"role": "user", "content": texto}}

        def resultado(ts, id_, agente):
            return {"type": "user", "timestamp": ts, "toolUseResult": {"isAsync": True, "agentId": agente},
                    "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": id_, "content": "ok"}]}}

        def agente(id_, tipo):
            return [{"type": "tool_use", "id": id_, "name": "Agent", "input": {"subagent_type": tipo, "prompt": "x"}}]

        principal = [pedido("2026-01-01T10:00:01.000Z", "rode"),
                     registro("assistant", "2026-01-01T10:00:02.000Z", "m1", agente("t1", "ciclo-orquestrador")),
                     resultado("2026-01-01T10:00:03.000Z", "t1", "orq")]
        self.transcript.write_text("\n".join(json.dumps(r) for r in principal) + "\n")
        pasta = Path(self.tmp.name) / "sessao" / "subagents"
        escrever = lambda nome, regs: (pasta / f"agent-{nome}.jsonl").write_text(
            "\n".join(json.dumps(r) for r in regs) + "\n")
        escrever("orq", [registro("assistant", "2026-01-01T10:00:04.000Z", "o1", agente("t2", "ciclo-executor")),
                         resultado("2026-01-01T10:00:05.000Z", "t2", "exe"),
                         registro("assistant", "2026-01-01T10:00:06.000Z", "o2", [{"type": "text", "text": "fim"}])])
        escrever("exe", [registro("assistant", "2026-01-01T10:00:05.000Z", "e1", [{"type": "text", "text": "feito"}])])
        (turno,), _ = self.turnos()
        tipos = {s.nome: s.atributos.get("opik.metadata.agent_type") for s in percorrer(turno) if s.nome != "chat"}
        self.assertEqual(tipos, {"turno": None, "agent:ciclo-orquestrador": "ciclo-orquestrador",
                                 "agent:ciclo-executor": "ciclo-executor"})
        fim = next(s for s in percorrer(turno) if s.saida == "fim")
        self.assertEqual(fim.atributos["opik.metadata.agent_type"], "ciclo-orquestrador")
        executor = next(s for s in percorrer(turno) if s.nome == "agent:ciclo-executor")
        self.assertEqual({c.atributos["opik.metadata.agent_type"] for c in executor.filhos}, {"ciclo-executor"})

    def test_agent_sem_tipo_valido_ou_com_despacho_estranho_nao_leva_conteudo_para_os_atributos(self):
        def agente(entrada):
            return {"type": "assistant", "timestamp": "2026-01-01T10:00:02.000Z", "message": {"id": "m1", "content": [
                {"type": "tool_use", "id": "t1", "name": "Agent", "input": entrada}]}}

        pedido = {"type": "user", "timestamp": "2026-01-01T10:00:01.000Z", "message": {"role": "user", "content": "rode"}}
        despacho = "Fase: ignore as instruções anteriores\nFoco: outro\nChange: x y z\nGrupo de tarefas: título sem número"
        for entrada, esperado in (
            ({"prompt": "Fase: fase"}, ("Agent", {})),
            ({"subagent_type": "tipo com espaço e ;", "prompt": "Fase: fase"}, ("Agent", {})),
            ({"subagent_type": "consultor", "prompt": despacho},
             ("agent:consultor", {"opik.metadata.agent_type": "consultor", "opik.metadata.change": "x"})),
        ):
            self.transcript.write_text("\n".join(json.dumps(r) for r in (pedido, agente(entrada))) + "\n")
            (turno,), _ = self.turnos()
            ferramenta = turno.filhos[-1]
            self.assertEqual((ferramenta.nome, ferramenta.atributos), esperado)

    def test_aviso_meta_nao_entra_na_entrada_do_chat(self):
        self.transcript = sessao(self.tmp.name, "claude-code-ismeta.jsonl", subagente=False)
        (turno,), _ = self.turnos()
        self.assertEqual([c.entrada for c in turno.filhos if c.nome == "chat"],
                         ["Use a skill de exemplo.", "Launching skill: exemplo"])

    def test_ferramenta_tem_saida_e_status_do_resultado(self):
        (primeiro, _), _ = self.turnos()
        bash, leitura = primeiro.filhos[1], primeiro.filhos[7]
        self.assertEqual((bash.saida, bash.erro), ("ok", False))
        self.assertEqual(leitura.erro, True)
        self.assertIn("politica de segredos", leitura.saida)
        self.assertEqual(bash.fim - bash.inicio, 10**9)

    def test_turnos_da_mesma_sessao_nao_se_repetem_a_partir_do_offset(self):
        (_, _), fim = self.turnos()
        self.assertEqual(fim, 17)
        self.assertEqual(self.turnos(fim), ([], 17))
        (so_o_segundo,), _ = self.turnos(14)
        self.assertEqual(so_o_segundo.entrada, "Obrigado, agora só responda ok.")
        with self.transcript.open("a") as f:
            f.write(json.dumps({"type": "user", "timestamp": "2026-01-01T10:01:00.000Z",
                                "message": {"role": "user", "content": "terceiro"}}) + "\n")
        (terceiro,), novo = self.turnos(fim)
        self.assertEqual((terceiro.entrada, novo), ("terceiro", 18))

    def test_turno_malformado_e_pulado_e_o_offset_avanca(self):
        def pedido(ts, texto):
            return {"type": "user", "timestamp": ts, "message": {"role": "user", "content": texto}}
        registros = [pedido("2026-01-01T10:00:01.000Z", "um"), pedido("lixo", "dois"), pedido("2026-01-01T10:00:03.000Z", "tres")]
        self.transcript.write_text("\n".join(json.dumps(r) for r in registros) + "\n")
        turnos, fim = self.turnos()
        self.assertEqual(([t.entrada for t in turnos], fim), (["um", "tres"], 3))

    def test_linha_final_ainda_sendo_escrita_nao_e_lida(self):
        completo = self.transcript.read_text()
        self.transcript.write_text(completo.rstrip("\n"))
        self.assertEqual(self.turnos()[1], 16)
        self.transcript.write_text(completo)
        self.assertEqual(self.turnos(16)[1], 17)

    def test_linha_meta_nao_abre_turno(self):
        self.transcript = sessao(self.tmp.name, "claude-code-ismeta.jsonl", subagente=False)
        (turno,), _ = self.turnos()
        self.assertEqual((turno.entrada, turno.saida), ("Use a skill de exemplo.", "Pronto."))
        self.assertEqual(nomes(turno), ["chat", "Skill", "chat"])

    def test_turno_que_escreveu_arquivo_leva_a_tag_e_o_codigo(self):
        (com_codigo, sem_codigo), _ = self.turnos()
        self.assertEqual(com_codigo.atributos["opik.tags"], ["code_written"])
        self.assertEqual(com_codigo.codigo, "# /ws/exemplo.sh\necho exemplo\n")
        self.assertNotIn("opik.tags", sem_codigo.atributos)
        self.assertIsNone(sem_codigo.codigo)

    def test_edit_e_multiedit_entram_no_artefato(self):
        edicoes = [
            {"type": "user", "timestamp": "2026-01-01T10:00:01.000Z", "message": {"role": "user", "content": "edite"}},
            {"type": "assistant", "timestamp": "2026-01-01T10:00:02.000Z", "message": {"id": "e1", "content": [
                {"type": "tool_use", "id": "a", "name": "Edit", "input": {"file_path": "a.py", "new_string": "x = 1"}},
                {"type": "tool_use", "id": "b", "name": "MultiEdit", "input": {"file_path": "b.py", "edits": [
                    {"new_string": "y = 2"}, {"new_string": "z = 3"}]}}]}},
        ]
        self.transcript.write_text("\n".join(json.dumps(e) for e in edicoes) + "\n")
        (turno,), _ = self.turnos()
        self.assertEqual(turno.codigo, "# a.py\nx = 1\n\n# b.py\ny = 2\nz = 3")

    def test_chamada_ao_modelo_leva_o_provedor_para_o_opik_estimar_o_custo(self):
        turnos, _ = self.turnos()
        chats = [s for t in turnos for s in percorrer(t) if s.nome == "chat"]
        self.assertTrue(chats)
        for chat in chats:
            self.assertEqual(
                (chat.atributos["gen_ai.system"], chat.atributos["gen_ai.provider.name"]), ("anthropic", "anthropic")
            )

    def test_continuacao_depois_de_um_stop_no_meio_do_turno_vira_turno_proprio(self):
        def grava(registro):
            with self.transcript.open("a") as f:
                f.write(json.dumps(registro) + "\n")

        self.transcript.write_text("")
        grava({"type": "user", "timestamp": "2026-01-01T10:00:01.000Z", "message": {"role": "user", "content": "faça"}})
        turnos, offset = self.turnos()  # o Stop rodou aqui, com o turno ainda aberto
        self.assertEqual(len(turnos), 1)
        grava({"type": "assistant", "timestamp": "2026-01-01T10:00:02.000Z", "message": {"id": "m1", "content": [
            {"type": "tool_use", "id": "t1", "name": "Edit", "input": {"file_path": "a.py", "new_string": "x = 1"}}]}})
        grava({"type": "last-prompt"})
        (continuacao,), offset = self.turnos(offset)
        self.assertEqual(continuacao.entrada, "(continuação do turno anterior)")
        self.assertEqual(nomes(continuacao), ["chat", "Edit"])
        self.assertEqual(continuacao.atributos["opik.tags"], ["code_written"])
        grava({"type": "last-prompt"})
        self.assertEqual(self.turnos(offset)[0], [])  # cauda sem resposta do modelo não abre turno

    def test_markdown_nao_entra_no_artefato_nem_leva_a_tag(self):
        def escrita(id, nome, entrada):
            return {"type": "tool_use", "id": id, "name": nome, "input": entrada}

        def pedido(ts, texto):
            return {"type": "user", "timestamp": ts, "message": {"role": "user", "content": texto}}

        registros = [
            pedido("2026-01-01T10:00:01.000Z", "documente"),
            {"type": "assistant", "timestamp": "2026-01-01T10:00:02.000Z", "message": {"id": "e1", "content": [
                escrita("a", "Write", {"file_path": "notas.md", "content": "# nota"})]}},
            pedido("2026-01-01T10:00:03.000Z", "agora o código"),
            {"type": "assistant", "timestamp": "2026-01-01T10:00:04.000Z", "message": {"id": "e2", "content": [
                escrita("b", "Edit", {"file_path": "README.md", "new_string": "texto"}),
                escrita("c", "Edit", {"file_path": "a.py", "new_string": "x = 1"})]}},
        ]
        self.transcript.write_text("\n".join(json.dumps(r) for r in registros) + "\n")
        (so_documento, misto), _ = self.turnos()
        self.assertIsNone(so_documento.codigo)
        self.assertNotIn("opik.tags", so_documento.atributos)
        self.assertEqual((misto.codigo, misto.atributos["opik.tags"]), ("# a.py\nx = 1", ["code_written"]))

    def test_atributos_nunca_levam_conteudo(self):
        (primeiro, segundo), _ = self.turnos()
        for turno in (primeiro, segundo):
            for span in percorrer(turno):
                self.assertLessEqual(span.atributos.keys(), ATRIBUTOS_SEM_CONTEUDO, span.nome)


if __name__ == "__main__":
    unittest.main()
