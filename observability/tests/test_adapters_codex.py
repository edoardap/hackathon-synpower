import json
import shutil
import tempfile
import unittest
from pathlib import Path

from observability.adapters.codex import ler_turnos

FIXTURES = Path(__file__).parent / "fixtures"
PAI = "22222222-aaaa-4bbb-8ccc-000000000002"
FILHO = "33333333-aaaa-4bbb-8ccc-000000000003"
ATRIBUTOS_SEM_CONTEUDO = {
    "gen_ai.request.model", "gen_ai.usage.input_tokens", "gen_ai.usage.output_tokens", "gen_ai.system",
    "gen_ai.provider.name", "opik.tags",
}


def sessao(tmp):
    """Copia as fixtures para o layout do Codex: os dois rollouts lado a lado, com o id da sessão no nome."""
    pai = Path(tmp) / f"rollout-2026-01-01T11-00-00-{PAI}.jsonl"
    shutil.copy(FIXTURES / "codex-rollout.jsonl", pai)
    shutil.copy(FIXTURES / "codex-rollout-subagente.jsonl", Path(tmp) / f"rollout-2026-01-01T11-00-05-{FILHO}.jsonl")
    return pai


def nomes(span):
    return [f.nome for f in span.filhos]


def percorrer(span):
    yield span
    for f in span.filhos:
        yield from percorrer(f)


class LeitorCodexTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.rollout = sessao(self.tmp.name)

    def turnos(self, offset=0):
        return ler_turnos(self.rollout, offset)

    def test_turno_com_comando_e_subagente_aninhado(self):
        (turno,), _ = self.turnos()
        self.assertEqual(nomes(turno), ["chat", "exec", "spawn_agent", "chat", "exec", "chat", "exec", "chat", "exec"])
        agente = turno.filhos[2]
        self.assertEqual(nomes(agente), ["exec", "chat", "chat"])
        self.assertEqual((agente.filhos[0].entrada, agente.filhos[0].saida), ("cat README.md", "Chunk ID: 1\nlinha inventada"))

    def test_tokens_por_chamada_e_modelo_do_turno(self):
        (turno,), _ = self.turnos()
        usos = [(c.atributos["gen_ai.usage.input_tokens"], c.atributos["gen_ai.usage.output_tokens"])
                for c in turno.filhos if c.nome == "chat"]
        self.assertEqual(usos, [(1000, 40), (1200, 30), (1400, 25), (1500, 20)])
        self.assertEqual(turno.filhos[0].atributos["gen_ai.request.model"], "modelo-codex-ficticio")
        self.assertEqual(turno.atributos["gen_ai.request.model"], "modelo-codex-ficticio")
        filhos = turno.filhos[2].filhos
        self.assertEqual([(c.atributos["gen_ai.usage.input_tokens"]) for c in filhos if c.nome == "chat"], [500, 520])

    def test_chamada_ao_modelo_leva_o_provedor_para_o_opik_estimar_o_custo(self):
        turnos, _ = self.turnos()
        chats = [s for t in turnos for s in percorrer(t) if s.nome == "chat"]
        self.assertTrue(chats)
        for chat in chats:
            self.assertEqual(
                (chat.atributos["gen_ai.system"], chat.atributos["gen_ai.provider.name"]), ("openai", "openai")
            )

    def test_pedido_vira_entrada_e_resposta_final_saida_do_turno(self):
        (turno,), _ = self.turnos()
        self.assertEqual((turno.entrada, turno.saida), ("Crie o script.", "Feito."))
        self.assertEqual((turno.inicio, turno.fim), (1767265201 * 10**9, 1767265212 * 10**9))

    def test_saida_do_comando_negado_traz_a_marca_do_guard(self):
        (turno,), _ = self.turnos()
        self.assertIn("politica de segredos", turno.filhos[6].saida)

    def test_codigo_de_saida_do_comando_vira_erro_do_span(self):
        (turno,), _ = self.turnos()
        echo, agente, patch, negado, falha = (turno.filhos[i] for i in (1, 2, 4, 6, 8))
        self.assertEqual([s.erro for s in (echo, agente, patch, falha)], [False, False, False, True])
        self.assertFalse(negado.erro)

    def test_apply_patch_dentro_do_exec_marca_o_turno_e_anexa_o_patch(self):
        (turno,), _ = self.turnos()
        self.assertEqual(turno.atributos["opik.tags"], ["code_written"])
        self.assertIn("*** Add File: exemplo.sh", turno.codigo)
        self.assertNotIn("echo ok", turno.codigo)

    def test_turno_sem_codigo_nao_leva_tag_nem_artefato(self):
        linhas = (FIXTURES / "codex-rollout.jsonl").read_text().splitlines()
        sem_patch = [l for l in linhas if "apply_patch" not in l and '"c-patch"' not in l]
        self.rollout.write_text("\n".join(sem_patch) + "\n")
        (turno,), _ = self.turnos()
        self.assertNotIn("opik.tags", turno.atributos)
        self.assertIsNone(turno.codigo)

    def test_apply_patch_so_no_texto_do_comando_nao_marca_codigo(self):
        rollout = [
            {"timestamp": "2026-01-01T12:00:00.000Z", "type": "event_msg", "payload": {"type": "task_started"}},
            {"timestamp": "2026-01-01T12:00:01.000Z", "type": "response_item", "payload": {
                "type": "custom_tool_call", "name": "exec", "call_id": "c1", "input": "rg apply_patch tools/"}},
        ]
        self.rollout.write_text("\n".join(json.dumps(r) for r in rollout) + "\n")
        (turno,), _ = self.turnos()
        self.assertNotIn("opik.tags", turno.atributos)
        self.assertIsNone(turno.codigo)

    def test_leitura_seguinte_nao_repete_turnos(self):
        (_,), fim = self.turnos()
        self.assertEqual(fim, len((FIXTURES / "codex-rollout.jsonl").read_text().splitlines()))
        self.assertEqual(self.turnos(fim), ([], fim))
        novo = [
            {"timestamp": "2026-01-01T12:00:00.000Z", "type": "event_msg",
             "payload": {"type": "task_started", "turn_id": "turno-2", "root_turn_id": "turno-2"}},
            {"timestamp": "2026-01-01T12:00:01.000Z", "type": "response_item",
             "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "outro"}]}},
            {"timestamp": "2026-01-01T12:00:02.000Z", "type": "event_msg",
             "payload": {"type": "task_complete", "turn_id": "turno-2", "last_agent_message": "ok"}},
        ]
        with self.rollout.open("a") as f:
            f.write("\n".join(json.dumps(r) for r in novo) + "\n")
        (segundo,), novo_fim = self.turnos(fim)
        self.assertEqual((segundo.entrada, segundo.saida, novo_fim), ("outro", "ok", fim + 3))

    def test_atributos_nunca_levam_conteudo(self):
        (turno,), _ = self.turnos()
        for span in percorrer(turno):
            self.assertLessEqual(span.atributos.keys(), ATRIBUTOS_SEM_CONTEUDO, span.nome)


if __name__ == "__main__":
    unittest.main()
