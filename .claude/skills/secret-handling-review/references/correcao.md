# Correção de Segredo Exposto

O que propor em cada finding. A ordem importa: rotacionar vem antes de limpar, porque o segredo já exposto continua
válido até ser trocado.

## Segredo Real Versionado

1. **Rotacione.** Gere uma credencial nova no provedor (banco, API, nuvem) e revogue a antiga. Quem faz isso é o dono da
   credencial; o relatório diz qual credencial e onde ela é usada.
2. **Leve para o ambiente.** Troque o valor no código pela leitura da configuração:

```diff
-DATABASE_URL = "postgresql://crm_app:Kq7v...@db.interno:5432/crm"
+DATABASE_URL = os.environ["DATABASE_URL"]
```

3. **Documente a variável.** Acrescente a variável ao `.env.example` com um marcador
   (`DATABASE_URL=postgresql://usuario:senha@localhost:5432/crm`).
4. **Histórico.** Reescrever o histórico (`git filter-repo`) só depois da rotação, e só com o time avisado, porque muda
   o hash de todos os commits seguintes. Com a credencial rotacionada, o valor antigo no histórico não dá mais acesso.

## Padrão Inseguro

Sem a variável, o sistema falha ao iniciar, em vez de rodar com o valor público:

```diff
-SECRET_KEY = os.getenv("SECRET_KEY", "changethis")
+SECRET_KEY = os.environ["SECRET_KEY"]
```

Projetos com `pydantic-settings` declaram o campo sem padrão, ou validam o padrão como o `full-stack-fastapi-template`
faz em `_check_default_secret`.

## Segredo em Log

Registre o identificador da operação, e não a credencial:

```diff
-logger.info("enviando lead %s com token %s", lead["id"], token)
+logger.info("enviando lead %s", lead["id"])
```

## `.env` Fora do `.gitignore`

```diff
+.env
+.env.*
+!.env.example
```

Se o `.env` já foi commitado, remova-o do índice com `git rm --cached .env` e trate os valores como segredo real
versionado.

## Valor Fixo em Teste

Troque pelo gerador de dado do repositório (`random_lower_string()`, `faker`), para o valor não ser reaproveitado fora
do teste.
