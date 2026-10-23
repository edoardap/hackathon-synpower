#!/bin/sh
set -u
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RAIZ=$(CDPATH= cd -- "$DIR/.." && pwd)
. "$DIR/helpers.sh"

PRE="$RAIZ/adapters/claude-code/pretooluse.sh"
GUARD="$RAIZ/tools/secret-guard"

# ---------------------------------------------------------------------------
# PreToolUse
# ---------------------------------------------------------------------------

# Leitura de .env e negada, com motivo.
saida=$(printf '{"tool_name":"Read","tool_input":{"file_path":".env"}}' | sh "$PRE")
assert_eq "nega leitura de .env" "$(printf '%s' "$saida" | jq -r '.hookSpecificOutput.permissionDecision')" "deny"
assert_eq "nomeia o evento" "$(printf '%s' "$saida" | jq -r '.hookSpecificOutput.hookEventName')" "PreToolUse"
assert_contains "motivo e acionavel" \
  "$(printf '%s' "$saida" | jq -r '.hookSpecificOutput.permissionDecisionReason')" "pergunte ao usuario"

# Leitura de arquivo comum nao e negada.
saida=$(printf '{"tool_name":"Read","tool_input":{"file_path":"README.md"}}' | sh "$PRE")
assert_nao_contains "permite README" "$saida" "deny"

# Bash que le segredo e negado pelo campo command.
saida=$(printf '{"tool_name":"Bash","tool_input":{"command":"cat .env"}}' | sh "$PRE")
assert_eq "nega bash que le .env" "$(printf '%s' "$saida" | jq -r '.hookSpecificOutput.permissionDecision')" "deny"

# Bash inofensivo passa.
saida=$(printf '{"tool_name":"Bash","tool_input":{"command":"git status"}}' | sh "$PRE")
assert_nao_contains "permite git status" "$saida" "deny"

# git commit exige aprovacao humana: o gancho pede confirmacao, em qualquer forma de chamar o commit.
decisao_bash() {
  printf '{"tool_name":"Bash","tool_input":{"command":%s}}' "$(jq -Rn --arg c "$1" '$c')" | sh "$PRE" |
    jq -r '.hookSpecificOutput.permissionDecision // ""'
}
assert_eq "git commit pede confirmacao" "$(decisao_bash 'git commit -m "feat: x"')" "ask"
assert_eq "git -C repo commit pede confirmacao" "$(decisao_bash 'git -C /tmp/repo commit -m x')" "ask"
assert_eq "commit depois de add pede confirmacao" "$(decisao_bash 'git add a.py && git commit -m x')" "ask"
assert_eq "git commit --amend pede confirmacao" "$(decisao_bash 'git -c user.name=a commit --amend')" "ask"
assert_eq "git status passa" "$(decisao_bash 'git status --short')" ""
assert_eq "git commit-tree nao e commit" "$(decisao_bash 'git commit-tree abc')" ""
assert_eq "segredo continua negado antes do commit" "$(decisao_bash 'cat .env && git commit -m x')" "deny"
saida=$(printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m x"}}' | sh "$PRE")
assert_contains "motivo do commit pede o diff" \
  "$(printf '%s' "$saida" | jq -r '.hookSpecificOutput.permissionDecisionReason')" "git diff --staged"

# Entrada malformada nao derruba o gancho.
saida=$(printf 'isto nao e json' | sh "$PRE")
assert_saida "json invalido sai zero" "$?" 0
assert_nao_contains "json invalido nao nega" "$saida" "deny"

# Defeito conhecido do esboco do plano: Grep usava .tool_input.pattern como se
# fosse caminho. Padrao de busca nao e caminho -- "grep -rn '\.env' src/" nao
# pode ser negado so porque o TEXTO procurado contem ".env". Grep so pode ser
# julgado pelo campo "path".
saida=$(printf '{"tool_name":"Grep","tool_input":{"pattern":"\\\\.env","path":"src/"}}' | sh "$PRE")
assert_nao_contains "grep buscando o TEXTO .env em caminho comum nao e negado" "$saida" "deny"

# Mas Grep cujo "path" aponta de fato para o segredo tem que ser negado.
saida=$(printf '{"tool_name":"Grep","tool_input":{"pattern":"TOKEN","path":".env"}}' | sh "$PRE")
assert_eq "grep com path apontando pro .env e negado" \
  "$(printf '%s' "$saida" | jq -r '.hookSpecificOutput.permissionDecision')" "deny"

# Glob: "pattern" AQUI e caminho de verdade (glob de arquivo), diferente de
# Grep -- os dois campos (path e pattern) sao checados.
saida=$(printf '{"tool_name":"Glob","tool_input":{"pattern":"**/.env"}}' | sh "$PRE")
assert_eq "glob com pattern apontando pro .env e negado" \
  "$(printf '%s' "$saida" | jq -r '.hookSpecificOutput.permissionDecision')" "deny"
saida=$(printf '{"tool_name":"Glob","tool_input":{"pattern":"**/*.ts"}}' | sh "$PRE")
assert_nao_contains "glob comum nao e negado" "$saida" "deny"

# NotebookEdit e MultiEdit sao tratados como Read/Edit/Write, pelo file_path.
saida=$(printf '{"tool_name":"NotebookEdit","tool_input":{"file_path":".env","new_source":"x"}}' | sh "$PRE")
assert_eq "notebookedit no .env e negado" \
  "$(printf '%s' "$saida" | jq -r '.hookSpecificOutput.permissionDecision')" "deny"
saida=$(printf '{"tool_name":"MultiEdit","tool_input":{"file_path":".env","edits":[]}}' | sh "$PRE")
assert_eq "multiedit no .env e negado" \
  "$(printf '%s' "$saida" | jq -r '.hookSpecificOutput.permissionDecision')" "deny"

# Contrato do qual "motivo=$(guard ...) || negar ..." depende: secret-guard
# imprime o motivo em STDOUT (nao stderr) quando nega. Se isso mudar,
# pretooluse.sh passa a capturar uma string vazia como motivo.
saida_guard_stdout=$("$GUARD" check --path ".env" 2>/dev/null)
assert_contains "contrato: secret-guard escreve o motivo em stdout" "$saida_guard_stdout" "negad"

PLUGIN_HOOKS="$RAIZ/hooks/hooks.json"
assert_eq "Plugin registra so o PreToolUse" "$(jq -r '.hooks | keys | join(",")' "$PLUGIN_HOOKS")" "PreToolUse"
assert_contains "Plugin chama o guard pela raiz do plugin" \
  "$(jq -r '[.hooks.PreToolUse[].hooks[].command] | join(" ")' "$PLUGIN_HOOKS")" '${CLAUDE_PLUGIN_ROOT}/adapters/claude-code/pretooluse.sh'
assert_contains "Plugin cobre leitura, edicao, busca e comando" \
  "$(jq -r '[.hooks.PreToolUse[].matcher] | join(" ")' "$PLUGIN_HOOKS")" "Read|Edit|Write|NotebookEdit|MultiEdit|Grep|Glob|Bash"

fim
