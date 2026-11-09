#!/bin/sh
# Hook assíncrono de observabilidade: sem endpoint (e sem OBS_SPIKE) não faz nada e sempre sai com 0.
set -u

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
PY="$RAIZ/.venv/bin/python"
[ -x "$PY" ] || exit 0

# Lê CHAVE=valor do .env sem executá-lo; variável já definida (mesmo vazia) vence o arquivo.
if [ -f "$RAIZ/.env" ]; then
  while IFS= read -r linha || [ -n "$linha" ]; do
    case $linha in ''|\#*|*=*) ;; *) continue ;; esac
    chave=${linha%%=*}
    case $chave in ''|[!A-Za-z_]*|*[!A-Za-z0-9_]*) continue ;; esac
    case $chave in  # chaves que controlam o shell ou processos filhos nunca vêm do .env
      PATH|IFS|LD_*|SHELL|ENV|BASH_ENV|CDPATH|HOME|PWD|TMPDIR|PS[1-4]|PYTHON*|*_PROXY|*_proxy) continue ;;
    esac
    awk -v k="$chave" 'BEGIN { exit !(k in ENVIRON) }' && continue
    export "$chave=${linha#*=}"
  done < "$RAIZ/.env"
fi

[ "${OBS_DISABLED:-}" = 1 ] && exit 0
[ -n "${OBS_OTLP_ENDPOINT:-}" ] || [ "${OBS_SPIKE:-}" = 1 ] || exit 0

cd "$RAIZ" || exit 0
"$PY" -m observability.adapters.hook "${1:-}" > /dev/null 2>&1
exit 0
