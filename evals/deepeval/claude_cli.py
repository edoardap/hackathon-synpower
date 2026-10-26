"""Executa o Claude Code em modo headless: gera as respostas do plugin e serve de juiz do DeepEval."""
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from deepeval.models import DeepEvalBaseLLM

PLUGIN_DIR = Path(__file__).resolve().parents[2]
PLUGIN_NAME = "hackathon-ai-swe"


def run_plugin(prompt: str, model: str | None = None, timeout: int = 600) -> dict:
    """Roda um prompt com o plugin carregado, num diretório vazio e sem permissão de escrita.

    Devolve a resposta final e as skills/agentes que o Claude acionou.
    """
    cmd = [
        "claude", "-p", prompt,
        "--plugin-dir", str(PLUGIN_DIR),
        "--output-format", "stream-json", "--verbose",
        "--permission-mode", "dontAsk",
        "--allowedTools", "Read Glob Grep Skill Agent",
        "--disallowedTools", "Write Edit Bash NotebookEdit",
        "--max-turns", "12",
        "--no-session-persistence",
        "--setting-sources", "project",
    ]
    if model:
        cmd += ["--model", model]
    with tempfile.TemporaryDirectory(prefix="eval-sandbox-") as sandbox:
        proc = subprocess.run(cmd, cwd=sandbox, capture_output=True, text=True,
                              timeout=timeout, stdin=subprocess.DEVNULL)
    activated, text = [], ""
    for line in proc.stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            for block in ev["message"]["content"]:
                if block.get("type") != "tool_use":
                    continue
                inp = block.get("input", {})
                if block["name"] == "Skill":
                    activated.append(inp.get("skill", "").removeprefix(f"{PLUGIN_NAME}:"))
                elif block["name"] == "Agent":
                    activated.append(inp.get("subagent_type", "").removeprefix(f"{PLUGIN_NAME}:"))
        elif ev.get("type") == "result":
            text = ev.get("result") or ""
    return {"output": text, "activated": activated, "returncode": proc.returncode}


class ClaudeJudge(DeepEvalBaseLLM):
    """Juiz do DeepEval que usa o `claude -p` (sem plugin e sem ferramentas), sem precisar de API key."""

    def __init__(self, model: str = "sonnet"):
        self.model = model
        super().__init__(model)

    def load_model(self):
        return self.model

    def get_model_name(self) -> str:
        return f"claude-cli:{self.model}"

    def generate(self, prompt: str, schema=None):
        if schema is not None:
            prompt += ("\n\nResponda SOMENTE com um objeto JSON válido que siga este JSON Schema, "
                       "sem texto antes ou depois e sem bloco de código:\n"
                       + json.dumps(schema.model_json_schema(), ensure_ascii=False))
        with tempfile.TemporaryDirectory(prefix="eval-judge-") as sandbox:
            proc = subprocess.run(
                ["claude", "-p", prompt, "--model", self.model, "--tools", "",
                 "--setting-sources", "", "--no-session-persistence"],
                cwd=sandbox, capture_output=True, text=True, timeout=300,
                stdin=subprocess.DEVNULL, env={**os.environ})
        out = proc.stdout.strip()
        if schema is None:
            return out
        match = re.search(r"\{.*\}", out, re.DOTALL)
        return schema.model_validate_json(match.group(0) if match else out)

    async def a_generate(self, prompt: str, schema=None):
        import asyncio
        return await asyncio.to_thread(self.generate, prompt, schema)
