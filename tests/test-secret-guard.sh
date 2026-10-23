#!/bin/sh
set -u
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RAIZ=$(CDPATH= cd -- "$DIR/.." && pwd)
. "$DIR/helpers.sh"

GUARD="${SECRET_GUARD_BIN:-$RAIZ/tools/secret-guard}"

nega() {
  saida=$("$GUARD" check "$1" "$2" 2>&1)
  codigo=$?
  assert_saida "nega $2" "$codigo" 1
  assert_contains "motivo de $2" "$saida" "negad"
}

permite() {
  "$GUARD" check "$1" "$2" >/dev/null 2>&1
  assert_saida "permite $2" "$?" 0
}

# --- Modo --path: politica larga, glob contra o caminho completo ------------

nega --path ".env"
nega --path "/home/alguem/projeto/.env"
nega --path ".env.local"
nega --path "certificado.pem"
nega --path "chave.key"
nega --path "$HOME/.ssh/id_rsa"
nega --path "$HOME/.my-credentials-git"
nega --path "$HOME/.config/gh/hosts.yml"
nega --path "$HOME/.aws/credentials"
nega --path "$HOME/.netrc"

permite --path ".env.example"
permite --path "/home/alguem/projeto/.env.example"
permite --path "README.md"
permite --path "tools/diff-review"

# --- Modo --command: politica estreita, glob contra o basename do token -----

nega --command "cat .env"
nega --command "grep TOKEN /home/alguem/.env"
nega --command "cat $HOME/.my-credentials-git"
nega --command "env"
nega --command "printenv"
nega --command "export -p"

permite --command "ls -la"
permite --command "git status"
permite --command "cat .env.example"
permite --command "env FOO=bar meu-comando"

# O motivo aponta a alternativa, para o agente saber o que fazer.
saida=$("$GUARD" check --path ".env" 2>&1)
assert_contains "motivo cita alternativa" "$saida" "pergunte ao usuario"

# --- Bypasses ja fechados em rodadas anteriores ------------------------------

# Aspas coladas no token.
nega --command "cat \"$HOME/.my-credentials-git\""
# Aspas simples em subshell.
nega --command "sh -c 'cat .env'"
# printenv com argumento vaza um token especifico.
nega --command "printenv GITLAB_TOKEN"
# env em pipe nao e env puro.
nega --command "env | grep TOKEN"
# Prefixo legitimo continua passando.
permite --command "env FOO=bar meu-comando"

# Expansao de $HOME, ${HOME} e ~/ entregues como texto literal pelo gancho.
nega --command 'cat $HOME/.my-credentials-git'
nega --command 'cat ${HOME}/.my-credentials-git'
nega --command 'cat "$HOME/.my-credentials-git"'
nega --path '$HOME/.my-credentials-git'
nega --path '${HOME}/.my-credentials-git'

# --- Trabalho legitimo nao pode ser negado ----------------------------------
# Um guarda que atrapalha o trabalho normal e desligado, e ai nao ha guarda.
# O casamento por basename e o que derruba estes falsos positivos.

permite --command "git commit -m 'fix credentials'"
permite --command "grep -rn 'credentials' src/"
permite --command "jq '.key' dados.json"
permite --command "find . -name '*.key'"
permite --command "echo printenv"
permite --command "man printenv"
# printenv fora da posicao de palavra de comando, dentro de um invocador.
permite --command "sh -c 'echo printenv'"
# ssh consome o host antes da palavra de comando.
permite --command "ssh host ls"

# --- Bypasses fechados pelo redesenho ---------------------------------------

# env e printenv detectados pela palavra de comando do segmento.
nega --command "FOO=bar env"
nega --command "/usr/bin/env"
nega --command "/usr/bin/printenv"
# Segmentacao por parenteses, barra invertida e & sozinho.
nega --command "(cat .env)"
nega --command 'cat \.env'
nega --command 'cat .env&'

# --- Falha fechada: politica ausente ou ilegivel nega tudo ------------------

dir_politica=$(tmpdir)

saida=$(SECRET_GUARD_POLICY=/nao/existe/secrets-deny.conf "$GUARD" check --path "README.md" 2>&1)
codigo=$?
assert_saida "politica de caminho inexistente nega" "$codigo" 1
assert_contains "motivo da politica inexistente" "$saida" "negad"

saida=$(SECRET_GUARD_POLICY="$dir_politica" "$GUARD" check --path "README.md" 2>&1)
codigo=$?
assert_saida "politica de caminho que e diretorio nega" "$codigo" 1
assert_contains "motivo da politica diretorio" "$saida" "negad"

saida=$(SECRET_GUARD_COMMAND_POLICY=/nao/existe/secrets-command.conf "$GUARD" check --command "ls" 2>&1)
codigo=$?
assert_saida "politica de comando inexistente nega" "$codigo" 1
assert_contains "motivo da politica de comando inexistente" "$saida" "negad"

saida=$(SECRET_GUARD_COMMAND_POLICY="$dir_politica" "$GUARD" check --command "ls" 2>&1)
codigo=$?
assert_saida "politica de comando que e diretorio nega" "$codigo" 1
assert_contains "motivo da politica de comando diretorio" "$saida" "negad"

# --- Independencia do diretorio corrente ------------------------------------
# Com set -f o veredito nao pode mudar com o conteudo do disco.

dir_vazio=$(tmpdir)
dir_cheio=$(tmpdir)
: > "$dir_cheio/servidor.key"
: > "$dir_cheio/id_rsa"

(cd "$dir_vazio" && "$GUARD" check --command 'ls *' >/dev/null 2>&1)
veredito_vazio=$?
(cd "$dir_cheio" && "$GUARD" check --command 'ls *' >/dev/null 2>&1)
veredito_cheio=$?
assert_saida "ls * em diretorio vazio" "$veredito_vazio" 0
assert_saida "ls * em diretorio com servidor.key" "$veredito_cheio" "$veredito_vazio"

# --- HOME hostil nao trava o gancho -----------------------------------------
# Se HOME contiver a propria string $HOME, substituir ate convergir nunca
# terminaria e o PreToolUse congelaria todo prompt do usuario.

HOME='$HOME' timeout 5 "$GUARD" check --command 'cat $HOME/.env' >/dev/null 2>&1
assert_saida "HOME hostil nao trava no modo comando" "$?" 1
HOME='$HOME' timeout 5 "$GUARD" check --path '$HOME/.netrc' >/dev/null 2>&1
assert_saida "HOME hostil nao trava no modo caminho" "$?" 1

# --- A mensagem nunca repete a palavra do comando ---------------------------

saida=$("$GUARD" check --command 'TOKEN=glpat-SEGREDO.key cat .env' 2>&1)
codigo=$?
assert_saida "nega comando com prefixo de token" "$codigo" 1
assert_nao_contains "motivo nao vaza a palavra do comando" "$saida" "glpat-SEGREDO"

saida=$("$GUARD" check --path "segredo-glpat-xyz.key" 2>&1)
codigo=$?
assert_saida "nega caminho de nome sensivel" "$codigo" 1
assert_nao_contains "motivo nao vaza o caminho" "$saida" "glpat-xyz"

# --- Rodada 5: escopo reduzido do modo comando ------------------------------

# Item 1: *.pem restaurado. O .key continua fora, por jq '.key' e find -name.
nega --command "cat servidor.pem"

# Item 2: hosts.yml e environ sairam da politica, ambiguos demais.
permite --command "ansible-playbook -i hosts.yml site.yml"
permite --command "grep -rn environ src/"
permite --command "awk '{set}' dados.txt"

# Item 3: chave publica nao e segredo, e exemplo de .env tambem nao.
permite --command "cat id_rsa.pub"
permite --command "cat $HOME/.ssh/id_ed25519.pub"
permite --command "cat .env.sample"
permite --command "cat .env.template"

# Item 4: diretorio de segredo por componente de caminho, que o basename perdia.
nega --command "tar -czf /tmp/x.tgz ~/.ssh"
nega --command "cp -r ~/.ssh /tmp/bkp"
nega --command "cp -r .env/ /tmp"

# Item 5: busca literal por texto nao e acesso a arquivo. A barra invertida so
# cai quando o token nao tinha aspas, e por isso `cat \.env` continua negado.
permite --command 'grep -n "\.env" README.md'

# Item 6: a ultima linha vale mesmo sem quebra final, e espaco a direita no
# padrao nao pode torna-lo inerte. Vale nos dois modos.
dir_conf=$(tmpdir)
printf '%s' '.segredo-sem-quebra' > "$dir_conf/cmd-sem-quebra.conf"
printf '%s\n' '.segredo-espaco   ' > "$dir_conf/cmd-espaco.conf"
printf '%s' '*/segredo-sem-quebra' > "$dir_conf/path-sem-quebra.conf"
printf '%s\n' '*/segredo-espaco   ' > "$dir_conf/path-espaco.conf"

saida=$(SECRET_GUARD_COMMAND_POLICY="$dir_conf/cmd-sem-quebra.conf" \
  "$GUARD" check --command "cat .segredo-sem-quebra" 2>&1)
codigo=$?
assert_saida "ultima linha sem quebra vale no modo comando" "$codigo" 1
assert_contains "motivo da ultima linha sem quebra" "$saida" "negad"

saida=$(SECRET_GUARD_COMMAND_POLICY="$dir_conf/cmd-espaco.conf" \
  "$GUARD" check --command "cat .segredo-espaco" 2>&1)
codigo=$?
assert_saida "espaco a direita nao inutiliza padrao de comando" "$codigo" 1
assert_contains "motivo do padrao com espaco" "$saida" "negad"

saida=$(SECRET_GUARD_POLICY="$dir_conf/path-sem-quebra.conf" \
  "$GUARD" check --path "dir/segredo-sem-quebra" 2>&1)
codigo=$?
assert_saida "ultima linha sem quebra vale no modo caminho" "$codigo" 1
assert_contains "motivo da ultima linha sem quebra no caminho" "$saida" "negad"

saida=$(SECRET_GUARD_POLICY="$dir_conf/path-espaco.conf" \
  "$GUARD" check --path "dir/segredo-espaco" 2>&1)
codigo=$?
assert_saida "espaco a direita nao inutiliza padrao de caminho" "$codigo" 1
assert_contains "motivo do padrao com espaco no caminho" "$saida" "negad"

# Item 7: o contrato so preve 0 e 1. Argumento vazio nega, nao sai 2.
nega --path ""
nega --command ""

# Item 8: o ramo "~/" de absoluto era inalcancavel, porque expandir_home ja
# resolve o til antes. A asserção de fonte fixa a remocao; as de comportamento
# garantem que o til continua funcionando sem ele.
fonte=$(cat "$GUARD")
assert_nao_contains "absoluto sem ramo de til morto" "$fonte" '"~/"*) expandir_til'
nega --path "~/.my-credentials-git"

# --- Limitacoes declaradas, fixadas em teste --------------------------------
# Os casos abaixo PERMITEM de proposito. Nao sao defeito: sao a decisao da
# rodada 5 de abandonar a lista de invocadores, que produzia bypass e falso
# positivo ao mesmo tempo e nunca ia ficar completa. Quem for "consertar" isto
# precisa antes ler as limitacoes declaradas no cabecalho de tools/secret-guard.
# A deteccao de despejo de ambiente vale so na primeira palavra do segmento.

permite --command "docker run alpine env"
permite --command "sudo env"
permite --command "sudo -u nobody env"
permite --command "sh -c 'env'"
permite --command "xargs env"
permite --command "ssh host env"
# O outro lado da mesma moeda: a lista tambem negava trabalho legitimo.
permite --command "command -v env"

# O cabecalho do script precisa dizer isso sem rodeio, nao so os testes.
assert_contains "cabecalho declara limitacao de invocador" "$fonte" "docker run alpine env"
assert_contains "cabecalho declara limitacao de indirecao" "$fonte" 'A=.env; cat $A'
assert_contains "cabecalho declara que previne acidente" "$fonte" "nao adversario"

# --- Correcao final: tres achados adjudicados -------------------------------

# Item 1: despejo de ambiente por /proc volta a ser negado, agora pela forma de
# caminho completo da politica, sem trazer de volta o basename `environ`.
nega --command "cat /proc/self/environ"
nega --command "cat /proc/1234/environ"
permite --command "grep -rn environ src/"
permite --command "cat environ"

# Item 2: token com * ou ? e padrao escrito por quem chamou, nao caminho
# concreto, e nao e casado contra a politica. Corrige a classe, nao o caso.
permite --command "find . -name '*.pem'"
permite --command "find . -name '*.key'"
nega --command "cat servidor.pem"

# Item 3: nem tudo no ~/.ssh e segredo. A excecao e escopada ao componente.
permite --command "cp -r ~/.ssh/config /tmp"
permite --command "cat ~/.ssh/known_hosts"
permite --command "cat ~/.ssh/authorized_keys"
permite --command "cat ~/.ssh/minha-chave.pub"
nega --command "cat ~/.ssh/id_rsa"
nega --command "tar -czf /tmp/x.tgz ~/.ssh"
nega --command "cp -r ~/.ssh /tmp/bkp"

# --- Glob inteiro nao e caminho; glob dentro de nome concreto e --------------
# Pular o casamento so vale quando o basename COMECA com * ou ?, porque ai o
# token e padrao que o chamador entrega a outro programa. `.en?` e `.en*` sao
# nome concreto com glob no meio: o shell que for rodar o comando expande cada
# um deles para o arquivo de verdade, entao continuam sendo casados.
nega --command 'cat .en?'
nega --command 'cat .en*'
nega --command 'cat ~/.ssh/id_rs?'
# O glob tambem nao pode entrar pela porta da excecao: `.env.*` expande para
# .env.local tanto quanto para .env.example.
nega --command 'cat .env.*'
permite --command "cat .env.example"
permite --command "find . -name '*.pem'"
permite --command "find . -name '*.key'"

# --- Canarios: o guarda inspeciona, nunca executa ---------------------------
# Se eval voltar por descuido, os canarios aparecem e estes testes falham.

tmpdir_canario=$(tmpdir)

canario1="$tmpdir_canario/canario1"
"$GUARD" check --command "touch $canario1" >/dev/null 2>&1
[ ! -f "$canario1" ]
assert_saida "canario 1 nao foi criado" "$?" 0

canario2="$tmpdir_canario/canario2"
"$GUARD" check --command "cat \$(touch $canario2)" >/dev/null 2>&1
[ ! -f "$canario2" ]
assert_saida "canario 2 nao foi criado" "$?" 0

canario3="$tmpdir_canario/canario3"
"$GUARD" check --command "cat \`touch $canario3\`" >/dev/null 2>&1
[ ! -f "$canario3" ]
assert_saida "canario 3 nao foi criado" "$?" 0

# --- Rodada de correcao 3, item 1: via inversa so com >= 3 literais --------
# Antes desta correcao, qualquer token com * ou ? virava padrao na direcao
# contraria (INVERSO=1) e era testado contra CADA linha da politica como se
# fosse um glob. Um token quase todo glob, como ".*" (so um literal: "."),
# vira um padrao tao largo que casa com ".aws", ".ssh" e quase qualquer linha
# -- um "grep -c '.*' foo.txt" corriqueiro era negado citando ".aws/". A via
# inversa continua necessaria para ".en?"/".en*" (o shell que roda o comando
# expande para ".env" de verdade), entao nao da para desligar geral: o limiar
# de 3 literais (contando so o que sobra do token depois de tirar *, ? e /)
# e o minimo que mantem esses dois presos e ja exclui ".*" (1 literal).
permite --command 'grep -c ".*" foo.txt'
permite --command 'grep -rn "< \"\$|done < |cat \"|jq .* \"\$" tools/ adapters/'
permite --command 'sed -E "s/^([^:]+:[0-9]+):.*(Item [A-H]\b).*/\1 \2/"'

nega --command 'cat .en?'
nega --command 'cat .en*'
nega --command 'cat .env.*'
nega --command 'cat .env'
nega --command 'cat ~/.aws/credentials'
nega --command 'tar -czf x.tgz ~/.ssh'
nega --command 'cp .env /tmp/x'
nega --command 'printenv'
nega --command 'env'
nega --command 'cat /proc/1/environ'
nega --command 'cat ~/.ssh/id_rsa'

# --- Colchete e glob de caminho igual a "?" ---------------------------------
# A deteccao de glob so olhava "*" e "?", entao ".en[v]" nao ligava a via
# inversa -- e o casamento direto tambem falha, porque a string ".en[v]" nao
# e igual a ".env". O token passava livre, com qualquer quantidade de
# literais, embora o shell que roda o comando expanda ".en[v]" para ".env" de
# verdade (verificado no zsh desta maquina). Diferente do teto declarado de
# ".??v", aqui nao havia teto nenhum.
nega --command 'cat .en[v]'
nega --command 'cat .en[!x]'
nega --command 'cat ~/.ssh/id_rs[a]'
# Colchete em uso legitimo continua passando: o token so e negado quando, como
# padrao, casa com uma linha da politica.
permite --command 'grep -E "[0-9]+" foo.txt'
permite --command 'sed -E "s/(Item [A-H])/x/" relatorio.txt'
permite --command 'ls src/[abc]*.py'

# O carregador do .env monta o caminho por dentro: sourciado no Bash, entregava
# os tokens sem que o comando citasse .env.
nega --command '. tools/lib/env.sh; carregar_env "$PWD"'
nega --command 'source ./tools/lib/env.sh'
nega --command '. tools/lib/*.sh; carregar_env .'
nega --command 'resolver_token gitlab gitlab.com'
permite --command 'tools/diff-review . main'
permite --command 'tools/secret-guard check --path README.md'

fim
