# Segredos

A política de segredos do plugin bloqueia a leitura do `.env` e dos caminhos de `config/secrets-deny.conf`
(`tools/secret-guard`). Esta página cobre o que sai nos traces de observabilidade.

## Redação na Observabilidade

O hook de observabilidade redige o texto de cada turno antes de enviá-lo ao Opik ou gravá-lo no spool. A redação
substitui por `[REDIGIDO]`:

- os valores do `.env` com 8 ou mais caracteres cuja chave termina em `TOKEN`, `KEY`, `SECRET` ou `PASSWORD`, lidos
  pelo processo do hook e nunca pelo agente;
- padrões de token: `sk-`, `ghp_`, `github_pat_`, `glpat-`, `xox*-`, `AKIA`, JWT, `Bearer` e bloco de chave
  privada.

Valores curtos e flags como `OBS_DISABLED=1` não são redigidos, e um segredo fora dessa regra e dos padrões passa.
Com `OBS_CONTENT=metadata`, o hook corta todo o texto, inclusive pedido, resposta e código, e envia só nomes de
ferramenta, modelo, tokens, duração e status. Use esse modo quando o conteúdo não puder sair da máquina.
