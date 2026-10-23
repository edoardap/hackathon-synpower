#!/bin/sh
# Apaga do disco a pasta de uma change do OpenSpec já arquivada e commitada.
# Uso: encerrar-change.sh <repositorio> <change> [--apagar]
# Sem --apagar, só lista o que seria apagado. A spec viva (openspec/specs/) e o backlog nunca são tocados.
# Recusa apagar se a pasta tiver arquivo não commitado: o conteúdo precisa estar no histórico do Git.
set -u

repo=${1:-}
change=${2:-}
modo=${3:-listar}
[ -n "$repo" ] && [ -n "$change" ] || { echo "uso: encerrar-change.sh <repositorio> <change> [--apagar]" >&2; exit 2; }
case "$change" in */*|.*|'') echo "nome de change inválido: $change" >&2; exit 2 ;; esac
[ -d "$repo/openspec/changes" ] || { echo "sem openspec/changes em $repo" >&2; exit 2; }

if [ -d "$repo/openspec/changes/$change" ]; then
  echo "a change $change ainda não foi arquivada: rode 'openspec archive $change --yes' antes" >&2
  exit 3
fi

alvos=$(find "$repo/openspec/changes/archive" -mindepth 1 -maxdepth 1 -type d -name "????-??-??-$change" 2>/dev/null)
[ -n "$alvos" ] || { echo "nenhuma pasta arquivada de $change em openspec/changes/archive/" >&2; exit 3; }

for alvo in $alvos; do
  relativo=${alvo#"$repo/"}
  pendente=$(git -C "$repo" status --porcelain --untracked-files=all -- "$relativo")
  if [ -n "$pendente" ]; then
    echo "recusado: $relativo tem arquivo não commitado; commite o arquivamento antes" >&2
    printf '%s\n' "$pendente" >&2
    exit 4
  fi
  echo "== $relativo ($(find "$alvo" -type f | wc -l | tr -d ' ') arquivos, $(du -sh "$alvo" | cut -f1))"
  (cd "$repo" && find "$relativo" -type f | sort)
  if [ "$modo" = "--apagar" ]; then
    git -C "$repo" rm -r -q -- "$relativo" && echo "apagado: $relativo (fica no histórico do Git)"
  fi
done

[ "$modo" = "--apagar" ] || echo "nada foi apagado; rode de novo com --apagar"
