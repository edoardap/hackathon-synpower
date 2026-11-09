#!/usr/bin/env bash
# regen_eval.sh — prepara e compara um eval de regeneração.
# Regra de ouro: NUNCA toca no projeto de origem. Tudo acontece em cópias dentro de <workdir>.
set -euo pipefail

usage() {
  cat <<'USAGE'
Uso:
  regen_eval.sh prepare <projeto_origem> <workdir> <caminho_a_remover> [mais_caminhos...]
      Copia o projeto para:
        <workdir>/golden  gabarito intacto (com git e o artefato original) — NÃO mostrar à skill
        <workdir>/clean   sala limpa onde a skill-sob-teste roda
      Na sala limpa: remove o .git original (sem histórico/diff que revele a resposta),
      apaga os caminhos informados e recria um git do zero com um único commit "baseline".

  regen_eval.sh diff <workdir> <caminho_removido> [mais_caminhos...]
      Depois da skill rodar na sala limpa, mostra:
        (a) o que a skill PRODUZIU  — git status/diff + arquivos novos da sala limpa
        (b) regenerado vs gabarito  — diff de cada caminho contra o original
USAGE
}

cmd="${1:-}"; shift || true

case "$cmd" in
  prepare)
    src="${1:?informe o projeto_origem}"; work="${2:?informe o workdir}"; shift 2
    [ "$#" -ge 1 ] || { echo "erro: informe ao menos um caminho a remover" >&2; exit 2; }
    [ -d "$src" ] || { echo "erro: origem não existe: $src" >&2; exit 2; }
    [ -e "$work" ] && { echo "erro: workdir já existe, escolha outro: $work" >&2; exit 2; }

    mkdir -p "$work"
    cp -a "$src" "$work/golden"
    cp -a "$src" "$work/clean"

    rm -rf "$work/clean/.git"

    for p in "$@"; do
      # shellcheck disable=SC2086
      if compgen -G "$work/clean/$p" > /dev/null; then
        rm -rf "$work/clean/"$p
        echo "removido: $p"
      else
        echo "aviso: nada casou com '$p' na sala limpa — confira o caminho" >&2
      fi
    done

    git -C "$work/clean" init -q
    git -C "$work/clean" add -A
    git -C "$work/clean" -c user.email=eval@local -c user.name=eval commit -qm baseline

    echo
    echo "sala limpa:  $work/clean   <- rode a skill-sob-teste AQUI"
    echo "gabarito:    $work/golden  <- não exponha à skill"
    ;;

  diff)
    work="${1:?informe o workdir}"; shift
    [ -d "$work/clean" ] && [ -d "$work/golden" ] || { echo "erro: workdir inválido: $work" >&2; exit 2; }

    echo "===== (a) o que a skill produziu na sala limpa ====="
    git -C "$work/clean" --no-pager status -s
    echo "--- alterações em arquivos já existentes ---"
    git -C "$work/clean" --no-pager diff
    echo "--- arquivos novos (não rastreados) ---"
    git -C "$work/clean" ls-files --others --exclude-standard

    echo
    echo "===== (b) regenerado vs gabarito, por caminho ====="
    for p in "$@"; do
      echo "--- $p ---"
      diff -ru "$work/golden/$p" "$work/clean/$p" 2>&1 || true
    done
    ;;

  *) usage; exit 2 ;;
esac
