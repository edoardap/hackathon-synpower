#!/bin/sh
set -u
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RAIZ=$(CDPATH= cd -- "$DIR/.." && pwd)
. "$DIR/helpers.sh"

SCRIPT="$RAIZ/.claude/skills/implement-feature/scripts/encerrar-change.sh"
git_q() { git -C "$repo" -c user.email=t@t -c user.name=t "$@" >/dev/null 2>&1; }

repo=$(tmpdir)
git -C "$repo" init -q
mkdir -p "$repo/openspec/specs/organizacoes" "$repo/openspec/changes/archive/2026-10-23-crm-r1-org/specs/organizacoes"
printf 'spec viva\n' > "$repo/openspec/specs/organizacoes/spec.md"
printf 'tarefas\n' > "$repo/openspec/changes/archive/2026-10-23-crm-r1-org/tasks.md"
printf 'delta\n' > "$repo/openspec/changes/archive/2026-10-23-crm-r1-org/specs/organizacoes/spec.md"

sh "$SCRIPT" >/dev/null 2>&1
assert_saida "sem argumentos sai 2" "$?" 2

sh "$SCRIPT" "$repo" ../fora >/dev/null 2>&1
assert_saida "nome com barra e recusado" "$?" 2

mkdir -p "$repo/openspec/changes/crm-r2-api"
sh "$SCRIPT" "$repo" crm-r2-api >/dev/null 2>&1
assert_saida "change ainda aberta e recusada" "$?" 3

saida=$(sh "$SCRIPT" "$repo" crm-r1-org 2>&1)
assert_saida "arquivamento nao commitado e recusado" "$?" 4
assert_contains "recusa explica o motivo" "$saida" "não commitado"

git_q add -A && git_q commit -m arquivamento
saida=$(sh "$SCRIPT" "$repo" crm-r1-org 2>&1)
assert_saida "listar sai zero" "$?" 0
assert_contains "lista o tasks.md" "$saida" "2026-10-23-crm-r1-org/tasks.md"
assert_contains "avisa que nada foi apagado" "$saida" "nada foi apagado"
assert_eq "listar nao apaga" "$([ -d "$repo/openspec/changes/archive/2026-10-23-crm-r1-org" ] && echo existe)" "existe"

sh "$SCRIPT" "$repo" crm-r1-org --apagar >/dev/null 2>&1
assert_saida "apagar sai zero" "$?" 0
assert_eq "pasta arquivada sai do disco" "$([ -d "$repo/openspec/changes/archive/2026-10-23-crm-r1-org" ] && echo existe || echo apagada)" "apagada"
assert_eq "spec viva continua" "$(cat "$repo/openspec/specs/organizacoes/spec.md")" "spec viva"
assert_contains "remocao fica preparada para o commit" "$(git -C "$repo" status --porcelain)" "D  openspec/changes/archive/2026-10-23-crm-r1-org/tasks.md"

fim
