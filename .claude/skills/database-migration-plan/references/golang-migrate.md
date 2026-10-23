# golang-migrate

Referência para projetos que migram o banco com [golang-migrate](https://github.com/golang-migrate/migrate), em que cada
versão é um par de arquivos SQL.

## Arquivos

Cada versão tem dois arquivos no diretório de migrações, com número sequencial e o mesmo nome:

```text
000012_add_opportunity.up.sql
000012_add_opportunity.down.sql
```

O `.down.sql` desfaz exatamente o `.up.sql`, em ordem inversa e com `IF EXISTS`, para o rollback não falhar se parte do
`up` não tiver sido aplicada. Versão sem `.down.sql` é irreversível.

**Conferir pares ausentes:**

```bash
for f in db/migrations/*.up.sql; do [ -f "${f%.up.sql}.down.sql" ] || echo "sem down: $f"; done
```

## Comandos

Projetos costumam encapsular os comandos no `Makefile` (`make migrate-new name=...`, `make migrate-up`,
`make migrate-down`). Use os alvos do projeto quando existirem. Os comandos diretos:

| Ação                               | Comando                                                                |
| ---------------------------------- | ---------------------------------------------------------------------- |
| Criar o par de arquivos            | `migrate create -ext sql -dir db/migrations -seq <nome>`               |
| Aplicar todas                      | `migrate -path db/migrations -database "$DATABASE_URL" up`             |
| Desfazer a última                  | `migrate -path db/migrations -database "$DATABASE_URL" down 1`         |
| Versão atual                       | `migrate -path db/migrations -database "$DATABASE_URL" version`        |
| Marcar versão após conserto manual | `migrate -path db/migrations -database "$DATABASE_URL" force <versão>` |

## Estado `dirty`

Se um `up` falha no meio, o `version` mostra `<versão> (dirty)` e nenhum comando avança.

1. Veja no banco o que o arquivo chegou a aplicar.
2. Desfaça à mão essas operações, ou complete-as.
3. Corrija o SQL do arquivo, que ainda não foi aplicado com sucesso em lugar nenhum.
4. Rode `force` com a versão anterior à que falhou e depois `up` de novo.
