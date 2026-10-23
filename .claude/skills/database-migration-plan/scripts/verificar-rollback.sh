#!/usr/bin/env bash
# Prova o rollback: aplica tudo, desfaz N migrações, aplica de novo e confere a versão.
# Uso:
#   verificar-rollback.sh --url <url do banco> [--tool alembic|golang-migrate] [--steps N] [--dir db/migrations]
#                         [--env-var NOME]
# Só aceita banco local: localhost, 127.0.0.1, ::1 ou os containers db e postgres. Qualquer outro host é recusado
# antes de rodar um comando. A URL sai de --url ou de $DATABASE_URL e é exportada em --env-var (padrão:
# DATABASE_URL) para a ferramenta usar o mesmo banco que foi conferido.
# Alembic: rode de onde fica o alembic.ini. Comando em $ALEMBIC (padrão: "uv run alembic").
# golang-migrate: diretório em --dir (padrão: db/migrations).
# Saída: o log de cada etapa e, na última linha, um JSON com o resultado.
set -u

tool=""
steps=1
dir="db/migrations"
url="${DATABASE_URL:-}"
env_var=DATABASE_URL
hosts_locais="localhost 127.0.0.1 ::1 db postgres"

while [ $# -gt 0 ]; do
  case "$1" in
    --tool) tool=$2; shift 2 ;;
    --steps) steps=$2; shift 2 ;;
    --dir) dir=$2; shift 2 ;;
    --url) url=$2; shift 2 ;;
    --env-var) env_var=$2; shift 2 ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *) echo "argumento desconhecido: $1" >&2; exit 2 ;;
  esac
done

# Host da URL, sem imprimir usuário nem senha: esquema://usuario:senha@host:porta/banco
host_da_url() {
  local resto=${1#*://}
  resto=${resto##*@}
  resto=${resto%%/*}
  resto=${resto%%\?*}
  case "$resto" in
    \[*\]*) resto=${resto#\[}; resto=${resto%%\]*} ;;
    *) resto=${resto%%:*} ;;
  esac
  printf '%s' "$resto"
}

[ -n "$url" ] || { echo "recusado: informe o banco local com --url ou DATABASE_URL" >&2; exit 3; }
host=$(host_da_url "$url")
case " $hosts_locais " in
  *" $host "*) echo "banco local confirmado: $host" ;;
  *) echo "recusado: o host '$host' não é local ($hosts_locais)" >&2; exit 3 ;;
esac
export "$env_var=$url"

if [ -z "$tool" ]; then
  if [ -f alembic.ini ]; then tool=alembic
  elif [ -d "$dir" ]; then tool=golang-migrate
  else echo "ferramenta não detectada: use --tool, ou rode de onde fica o alembic.ini" >&2; exit 2
  fi
fi

resultado() {
  printf '{"ferramenta":"%s","passos":%s,"versao_antes":"%s","versao_depois":"%s","resultado":"%s","etapa":"%s"}\n' \
    "$tool" "$steps" "$1" "$2" "$3" "$4"
  [ "$3" = ok ]
}

etapa() {
  echo "== $1"
  shift
  "$@"
}

case "$tool" in
  alembic)
    read -r -a cmd <<< "${ALEMBIC:-uv run alembic}"
    versao() { "${cmd[@]}" current 2>/dev/null | awk 'NF {v=$1} END {print v}'; }

    etapa "upgrade head" "${cmd[@]}" upgrade head || { resultado "" "" falha "upgrade inicial"; exit 1; }
    antes=$(versao)
    etapa "downgrade -$steps" "${cmd[@]}" downgrade "-$steps" || { resultado "$antes" "" falha downgrade; exit 1; }
    etapa "upgrade head" "${cmd[@]}" upgrade head || { resultado "$antes" "" falha "upgrade depois do downgrade"; exit 1; }
    depois=$(versao)
    ;;
  golang-migrate)
    command -v migrate >/dev/null || { echo "migrate não encontrado no PATH" >&2; exit 2; }
    faltando=$(for f in "$dir"/*.up.sql; do [ -f "${f%.up.sql}.down.sql" ] || echo "$f"; done)
    if [ -n "$faltando" ]; then
      echo "migrações sem .down.sql:"; echo "$faltando"
    fi
    m() { migrate -path "$dir" -database "$url" "$@"; }
    versao() { m version 2>&1 | tail -1; }

    etapa "up" m up || { resultado "" "" falha "up inicial"; exit 1; }
    antes=$(versao)
    etapa "down $steps" m down "$steps" || { resultado "$antes" "" falha down; exit 1; }
    etapa "up" m up || { resultado "$antes" "" falha "up depois do down"; exit 1; }
    depois=$(versao)
    if [ -n "$faltando" ]; then resultado "$antes" "$depois" falha "pares sem .down.sql"; exit 1; fi
    ;;
  *)
    echo "ferramenta não suportada: $tool" >&2; exit 2 ;;
esac

if [ -n "$antes" ] && [ "$antes" = "$depois" ]; then
  resultado "$antes" "$depois" ok "ciclo completo"
else
  resultado "$antes" "$depois" falha "versão final diferente da inicial"
  exit 1
fi
