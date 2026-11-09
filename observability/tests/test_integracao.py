import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from observability.adapters import hook
from observability.tests.test_tracing import Receptor, atributos

NEGADO = "Acesso negado pela politica de segredos: casa com o padrao .pem"


def jsonl(*registros):
    return "".join(json.dumps(r) + "\n" for r in registros)


def t(s):
    return f"2026-01-01T10:00:{s:02d}.000Z"


# Um turno com duas ferramentas: o `Bash` negado pelo guard e um `Read` que passa.
CLAUDE = jsonl(
    {"type": "user", "timestamp": t(1), "message": {"role": "user", "content": "leia a chave"}},
    {"type": "assistant", "timestamp": t(2), "message": {
        "id": "m1", "model": "claude-sonnet-5-5", "usage": {"input_tokens": 1_000_000, "output_tokens": 100_000},
        "content": [{"type": "tool_use", "id": "a", "name": "Bash", "input": {"command": "cat chave.pem"}},
                    {"type": "tool_use", "id": "b", "name": "Read", "input": {"file_path": "/ws/a.txt"}}]}},
    {"type": "user", "timestamp": t(3), "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "a", "content": NEGADO, "is_error": True},
        {"type": "tool_result", "tool_use_id": "b", "content": "conteudo", "is_error": False}]}},
    {"type": "assistant", "timestamp": t(4), "message": {"id": "m2", "model": "claude-sonnet-5-5", "usage": {"input_tokens": 0, "output_tokens": 0},
        "content": [{"type": "text", "text": "Negado."}]}},
)

# No Codex o bloqueio não tem flag de erro: só o texto na saída.
CODEX = jsonl(
    {"timestamp": t(1), "type": "event_msg", "payload": {"type": "task_started"}},
    {"timestamp": t(1), "type": "turn_context", "payload": {"model": "gpt-6-luna"}},
    {"timestamp": t(2), "type": "response_item", "payload": {"type": "message", "role": "user",
                                                           "content": [{"type": "input_text", "text": "leia a chave"}]}},
    {"timestamp": t(3), "type": "token_usage_record", "payload": {"usage": {"input_tokens": 1_000_000, "output_tokens": 100_000}}},
    {"timestamp": t(4), "type": "response_item", "payload": {
        "type": "custom_tool_call", "name": "exec", "call_id": "a", "input": "cat chave.pem"}},
    {"timestamp": t(4), "type": "response_item", "payload": {
        "type": "custom_tool_call_output", "call_id": "a", "output": [{"type": "input_text", "text": NEGADO}]}},
    {"timestamp": t(5), "type": "response_item", "payload": {
        "type": "custom_tool_call", "name": "exec", "call_id": "b", "input": "ls"}},
    {"timestamp": t(5), "type": "response_item", "payload": {
        "type": "custom_tool_call_output", "call_id": "b", "output": [{"type": "input_text", "text": "a.txt"}]}},
    {"timestamp": t(6), "type": "event_msg", "payload": {"type": "task_complete", "last_agent_message": "Negado."}},
)


class BloqueioDoGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.rec = Receptor()
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(self.rec.fechar)

    def exportar(self, executor, transcript, **env):
        arquivo = Path(self.tmp.name) / "sessao.jsonl"
        arquivo.write_text(transcript)
        payload = json.dumps({"session_id": "s1", "transcript_path": str(arquivo), "hook_event_name": "Stop"})
        env = {"OBS_OTLP_ENDPOINT": self.rec.url.removesuffix("/v1/traces"), **env}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(hook, "CACHE", Path(self.tmp.name) / "o"):
            with mock.patch("sys.stdin", io.StringIO(payload)):
                hook.main(executor)
        (raiz,) = [s for s in self.rec.spans() if s.name == "turno"]
        return atributos(raiz)

    def confere(self, raiz):
        self.assertEqual(raiz["opik.metadata.score.guard_blocks"].int_value, 1)
        self.assertEqual(raiz["opik.metadata.score.tool_failure_rate"].double_value, 0.5)
        self.assertEqual([v.string_value for v in raiz["opik.tags"].array_value.values], ["tool_failure", "guard_block"])
        self.assertEqual(raiz["opik.metadata.score.tokens_total"].int_value, 1_100_000)
        self.assertNotIn("gen_ai.usage.input_tokens", raiz)

    def test_bash_negado_no_claude_code(self):
        raiz = self.exportar("claude-code", CLAUDE)
        self.confere(raiz)
        self.assertEqual(raiz["opik.metadata.score.cost_usd"].double_value, 3.0)

    def test_exec_negado_no_codex_sem_preco_do_modelo(self):
        raiz = self.exportar("codex", CODEX)
        self.confere(raiz)
        self.assertNotIn("opik.metadata.score.cost_usd", raiz)

    def test_modo_metadado_mantem_as_heuristicas(self):
        raiz = self.exportar("codex", CODEX, OBS_CONTENT="metadata")
        self.assertEqual(raiz["opik.metadata.score.guard_blocks"].int_value, 1)
        self.assertNotIn("output.value", raiz)


if __name__ == "__main__":
    unittest.main()
