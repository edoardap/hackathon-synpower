#!/bin/sh
set -u
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RAIZ=$(CDPATH= cd -- "$DIR/.." && pwd)
. "$DIR/helpers.sh"

# Cada executor registra o hook de observabilidade, assincrono, em Stop e SessionEnd.
checa() { # arquivo evento comando timeout
  item=$(jq -c --arg e "$2" '[.hooks[$e][].hooks[] | select(.command | contains("observability/adapters/hook.sh"))] | .[0]' "$1")
  assert_eq "$1 $2: comando" "$(printf '%s' "$item" | jq -r .command)" "$3"
  assert_eq "$1 $2: assincrono" "$(printf '%s' "$item" | jq -r .async)" "true"
  assert_eq "$1 $2: timeout" "$(printf '%s' "$item" | jq -r .timeout)" "$4"
  assert_eq "$1 $2: sem asyncRewake" "$(printf '%s' "$item" | jq -r 'has("asyncRewake")')" "false"
}
CC="$RAIZ/.claude/settings.json"
CX="$RAIZ/.codex/hooks.json"
checa "$CC" Stop 'sh "$CLAUDE_PROJECT_DIR/observability/adapters/hook.sh" claude-code' 60
checa "$CC" SessionEnd 'sh "$CLAUDE_PROJECT_DIR/observability/adapters/hook.sh" claude-code' 8
checa "$CX" Stop 'sh observability/adapters/hook.sh codex' 30
checa "$CX" SessionEnd 'sh observability/adapters/hook.sh codex' 3

assert_eq "MCP do Opik no Claude Code" "$(jq -r '.mcpServers.opik.url' "$RAIZ/.mcp.json")" "https://www.comet.com/opik/api/v1/mcp"
assert_contains "MCP do Opik no Codex" "$(cat "$RAIZ/.codex/config.toml")" 'url = "https://www.comet.com/opik/api/v1/mcp"'

# make init sincroniza o ambiente com uv e cria o .env a partir do modelo.
alvo=$(tmpdir)
cp "$RAIZ/Makefile" "$RAIZ/.env.example" "$alvo/"
plano=$(make -n -C "$alvo" init 2>&1)
assert_contains "make init copia o .env.example" "$plano" "cp $alvo/.env.example $alvo/.env"
assert_contains "make init roda uv sync" "$plano" "uv sync"

fim
