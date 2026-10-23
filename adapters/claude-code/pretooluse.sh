#!/bin/sh
# Traduz o PreToolUse do Claude Code em consulta ao secret-guard. Saida vazia
# significa "sem opiniao". Grep e julgado so pelo "path" (o "pattern" e TEXTO
# de busca, nao caminho); Glob pelos dois, porque ali o pattern E um glob de
# caminho ("**/.env").
set -u

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
GUARD="$RAIZ/tools/secret-guard"

entrada=$(cat)
ferramenta=$(printf '%s' "$entrada" | jq -r '.tool_name // ""' 2>/dev/null) || exit 0
[ -n "$ferramenta" ] || exit 0

negar() {
  jq -n --arg motivo "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $motivo
    }
  }'
  exit 0
}

perguntar() {
  jq -n --arg motivo "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: $motivo
    }
  }'
  exit 0
}

# git commit, com opcoes antes do subcomando (git -C <repo> commit, git -c k=v commit).
COMMIT_RE='(^|[;&|(`[:space:]])git([[:space:]]+(-C|-c)[[:space:]]+[^[:space:]]+|[[:space:]]+--?[A-Za-z][^[:space:]]*)*[[:space:]]+commit([[:space:]]|$)'
MOTIVO_COMMIT="Commit exige aprovacao humana: confira o diff (git diff --staged) antes de permitir."

campo_json() {
  printf '%s' "$entrada" | jq -r --arg c "$1" '.tool_input[$c] // ""' 2>/dev/null
}

case $ferramenta in
  Bash)
    comando=$(campo_json command)
    [ -n "$comando" ] || exit 0
    # secret-guard imprime o motivo em stdout (nao stderr) e sai 1 ao negar.
    motivo=$("$GUARD" check --command "$comando") || negar "$motivo"
    printf '%s' "$comando" | grep -Eq "$COMMIT_RE" && perguntar "$MOTIVO_COMMIT"
    ;;
  Read|Edit|Write|NotebookEdit|MultiEdit)
    caminho=$(campo_json file_path)
    [ -n "$caminho" ] || exit 0
    motivo=$("$GUARD" check --path "$caminho") || negar "$motivo"
    ;;
  Grep)
    caminho=$(campo_json path)
    [ -n "$caminho" ] || exit 0
    motivo=$("$GUARD" check --path "$caminho") || negar "$motivo"
    ;;
  Glob)
    for campo in path pattern; do
      caminho=$(campo_json "$campo")
      [ -n "$caminho" ] || continue
      motivo=$("$GUARD" check --path "$caminho") || negar "$motivo"
    done
    ;;
esac

exit 0
