#!/bin/sh
# Executa todos os arquivos de teste e agrega o resultado.
set -u
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
total=0
falhas=0

for t in "$DIR"/test-*.sh; do
  [ -f "$t" ] || continue
  total=$((total + 1))
  sh "$t" || falhas=$((falhas + 1))
done

printf '\n%d arquivo(s) de teste, %d com falha\n' "$total" "$falhas"
[ "$falhas" -eq 0 ]
