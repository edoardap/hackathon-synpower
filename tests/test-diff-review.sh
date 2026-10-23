#!/bin/sh
set -u
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RAIZ=$(CDPATH= cd -- "$DIR/.." && pwd)
. "$DIR/helpers.sh"

repo=$(tmpdir)
g() { git -C "$repo" -c user.name=t -c user.email=t@t "$@"; }
g init -q -b dev
printf 'a\nb\nc\n' > "$repo/mod.py"
printf 'sai\n' > "$repo/del.txt"
printf 'um\ndois\ntres\nquatro\n' > "$repo/velho.md"
seq 20 > "$repo/longo.txt"
g add . && g commit -qm base
g checkout -qb feat
printf 'a\nB\nc\n' > "$repo/mod.py"
printf 'novo\n' > "$repo/novo.sql"
seq 20 | sed 's/^10$/dez/' > "$repo/longo.txt"
g rm -q del.txt
g mv velho.md novo.md
g add . && g commit -qm 'feat: muda'

html=$(tmpdir)/r.html
saida=$("$RAIZ/tools/diff-review" "$repo" dev feat -o "$html" 2>&1)
assert_eq "imprime o caminho do html" "$saida" "$html"

resumo=$(python3 - "$html" <<'EOF'
import json, re, sys
d = json.loads(re.search(r'<script id="dados" type="application/json">(.*?)</script>', open(sys.argv[1]).read(), re.S)[1])
for f in d["files"]:
    print(f["path"], "completo", sum(len(h["lines"]) for h in f.get("full", [])))
    print(f["path"], f["status"], f["add"], f["del"], "".join(l["t"] + (str(l["n"] or l["o"])) for h in f["hunks"] for l in h["lines"]))
print("commits", len(d["commits"]), d["head"], d["base"])
EOF
)
assert_contains "modificado com linhas numeradas" "$resumo" "mod.py modified 1 1  1-2+2 3"
assert_contains "adicionado" "$resumo" "novo.sql added 1 0 +1"
assert_contains "removido usa o caminho antigo" "$resumo" "del.txt deleted 0 1 -1"
assert_contains "renomeado sem conteudo" "$resumo" "novo.md renamed 0 0 "
assert_contains "arquivo completo quando o diff corta linhas" "$resumo" "longo.txt completo 21"
assert_contains "sem copia quando o diff ja cobre o arquivo" "$resumo" "mod.py completo 0"
assert_contains "commits so de head" "$resumo" "commits 1 feat dev"

erro=$("$RAIZ/tools/diff-review" "$repo" nao-existe 2>&1)
assert_contains "ref inexistente lista branches" "$erro" "feat"

fim
