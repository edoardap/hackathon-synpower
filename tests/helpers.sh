# tests/helpers.sh — asserções compartilhadas. Cada arquivo de teste sai 1 se houver falha.
CASOS=0
FALHAS=0
TMPDIRS=""

trap 'rm -rf $TMPDIRS' EXIT INT TERM

_falha() {
  FALHAS=$((FALHAS + 1))
  printf '  FALHOU %s\n' "$1" >&2
}

assert_eq() {
  CASOS=$((CASOS + 1))
  [ "$2" = "$3" ] && return 0
  _falha "$1: esperado [$3], obtido [$2]"
}

assert_contains() {
  CASOS=$((CASOS + 1))
  case $2 in *"$3"*) return 0 ;; esac
  _falha "$1: texto nao contem [$3]"
}

assert_nao_contains() {
  CASOS=$((CASOS + 1))
  case $2 in *"$3"*) _falha "$1: texto contem [$3] e nao deveria" ;; esac
  return 0
}

assert_saida() {
  CASOS=$((CASOS + 1))
  [ "$2" = "$3" ] && return 0
  _falha "$1: saida esperada [$3], obtida [$2]"
}

tmpdir() {
  _d=$(mktemp -d)
  TMPDIRS="$TMPDIRS $_d"
  printf '%s\n' "$_d"
}

fim() {
  printf '%s: %d caso(s), %d falha(s)\n' "$(basename "$0")" "$CASOS" "$FALHAS"
  [ "$FALHAS" -eq 0 ]
}
