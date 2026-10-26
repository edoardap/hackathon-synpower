#!/bin/sh
set -u
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RAIZ=$(CDPATH= cd -- "$DIR/.." && pwd)
. "$DIR/helpers.sh"

HOOK="$RAIZ/observability/adapters/hook.sh"
PY="$RAIZ/.venv/bin/python"
# Transcript real: sem as guardas do hook.sh o hook leria o turno e criaria observability/ no cache.
PAYLOAD="{\"session_id\":\"s1\",\"transcript_path\":\"$RAIZ/observability/tests/fixtures/claude-code-ismeta.jsonl\",\"hook_event_name\":\"Stop\"}"

# Sem endpoint o hook sai com 0 e nao cria nada no diretorio de cache. OBS_OTLP_ENDPOINT vazio e exportado
# para que o .env da pessoa nao o preencha (o hook.sh respeita variavel ja definida, mesmo vazia).
cache=$(tmpdir)
printf '%s' "$PAYLOAD" |
  OBS_OTLP_ENDPOINT= OBS_SPIKE= OBS_DISABLED= RAS_CACHE_DIR="$cache" sh "$HOOK" claude-code
assert_eq "sem endpoint o hook sai com 0" "$?" "0"
assert_eq "sem endpoint nao cria observability/ no cache" "$(ls -A "$cache")" ""

# Com OBS_DISABLED=1 o hook tambem nao faz nada, mesmo com endpoint.
printf '%s' "$PAYLOAD" | OBS_DISABLED=1 OBS_OTLP_ENDPOINT=http://127.0.0.1:9 RAS_CACHE_DIR="$cache" sh "$HOOK" claude-code
assert_eq "OBS_DISABLED=1 sai com 0" "$?" "0"
assert_eq "OBS_DISABLED=1 nao cria observability/ no cache" "$(ls -A "$cache")" ""

# Controle positivo: o mesmo payload com endpoint morto roda o hook e grava no cache, o que prova que os
# asserts acima discriminam.
printf '%s' "$PAYLOAD" | OBS_OTLP_ENDPOINT=http://127.0.0.1:9 OBS_SPIKE= OBS_DISABLED= RAS_CACHE_DIR="$cache" sh "$HOOK" claude-code
assert_eq "endpoint morto sai com 0" "$?" "0"
assert_contains "endpoint morto grava observability/ no cache" "$(ls -A "$cache")" "observability"

# O Python tambem recusa a falta de endpoint (envio.configuracao), entao com transcript real so a guarda de
# OBS_DISABLED e observavel. Stdin invalido derruba o Python e ele grava erros.log: so a guarda do hook.sh,
# que nem inicia o Python, mantem o cache vazio.
cache2=$(tmpdir)
printf 'nao e json' | OBS_OTLP_ENDPOINT= OBS_SPIKE= OBS_DISABLED= RAS_CACHE_DIR="$cache2" sh "$HOOK" claude-code
assert_eq "sem endpoint o hook.sh nao inicia o Python" "$(ls -A "$cache2")" ""
printf 'nao e json' | OBS_OTLP_ENDPOINT=http://127.0.0.1:9 OBS_SPIKE= OBS_DISABLED= RAS_CACHE_DIR="$cache2" sh "$HOOK" claude-code
assert_contains "com endpoint o hook.sh inicia o Python" "$(ls -A "$cache2")" "observability"

# Export do span raiz, redacao, spool e leitores, contra um servidor HTTP local.
saida=$(cd "$RAIZ" && "$PY" -m unittest discover -s observability/tests 2>&1)
assert_eq "suite Python de observability passa" "$?" "0"
assert_contains "suite Python termina com OK" "$saida" "OK"

# O .env nao e executado e a variavel ja definida, mesmo vazia, vence o arquivo.
raiz=$(tmpdir)
mkdir -p "$raiz/observability/adapters" "$raiz/.venv/bin"
cp "$HOOK" "$raiz/observability/adapters/hook.sh"
printf '#!/bin/sh\nprintf "%s|%s" "${OBS_OTLP_ENDPOINT-nao}" "${OBS_PROJECT-nao}" > "$0.saida"\n' '%s' '%s' > "$raiz/.venv/bin/python"
chmod +x "$raiz/.venv/bin/python"
printf 'OBS_OTLP_ENDPOINT=http://x\nOBS_PROJECT=do-env\nVAR=$(touch %s/executou)\n' "$raiz" > "$raiz/.env"
OBS_PROJECT= sh "$raiz/observability/adapters/hook.sh" claude-code
assert_eq ".env preenche o que falta e o vazio exportado vence" "$(cat "$raiz/.venv/bin/python.saida")" "http://x|"
assert_eq ".env nao e executado" "$([ -e "$raiz/executou" ] && echo sim || echo nao)" "nao"

fim
