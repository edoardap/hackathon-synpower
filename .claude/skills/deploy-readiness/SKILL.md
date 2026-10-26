---
name: deploy-readiness
description: 'Rito de pré e pós-deploy de um serviço Synpower sobre o layout Kubernetes/ArgoCD (manifests em infra/<serviço>/<ambiente>/, migração Liquibase em PreSync antes do app). Verifica que está tudo pronto antes de subir, confirma que subiu bem depois e define o procedimento de rollback. Use ao perguntar "esse deploy está pronto?", "pode promover pra produção?", "o que checar antes de subir?", "checklist de deploy", "criar o ambiente de staging/prod", "como faço o rollback desse deploy?". Só lê e checa; não escreve código de feature, não roda a migração (isso é da liquibase-migration) e não altera manifests sem o usuário pedir.'
---

# Deploy Readiness

Rito de operação para promover um serviço Synpower. O deploy é **Kubernetes gerenciado por ArgoCD**, com os manifests
versionados em `infra/<serviço>/<ambiente>/`. Esta skill **verifica e opera**: confere que está pronto antes de subir,
confirma que subiu bem depois e define o rollback. Ela não escreve código de feature, não desenha a migração (isso é da
`liquibase-migration`) e não instrumenta o serviço (isso é da `observability-coverage`). Manifest só é alterado quando o
usuário pedir.

Nos caminhos abaixo, `${CLAUDE_SKILL_DIR}` é a pasta desta skill (`.claude/skills/deploy-readiness/`).

## O rito em uma frase

O ArgoCD sincroniza os manifests por **sync-waves**, e é nisso que o rito se apoia:

| Wave | Recurso | Papel |
| --- | --- | --- |
| `0` | ConfigMap (`<serviço>-config`) e ExternalSecret (`<serviço>-secret`), ambos `hook: PreSync` | Config e segredo existem antes de tudo |
| `1` | Job Liquibase (`hook: PreSync`, `restartPolicy: Never`, `backoffLimit`) | **A migração roda antes do app subir** |
| `2` | Deployment, Service, IngressRoute | O app sobe só depois |

A consequência é a regra central: **se o Job de migração falha, o `backoffLimit` estoura, o PreSync não completa e o
Deployment nem avança.** A readiness da aplicação depende da migração ter passado. Por isso o rito olha a migração
primeiro, sempre.

## Princípios

- **Pronto se prova, não se parece.** Cada item do checklist fecha com uma evidência concreta: o `kubectl get` que mostra
  o Job `Complete`, o `diff` entre as chaves do `.env.example` e as do ConfigMap, a tag da imagem no manifest. Sem a
  evidência, o item fica `A verificar`, não `ok`.
- **A migração manda.** Antes de qualquer coisa, a mudança de schema que o Job PreSync vai aplicar precisa estar pronta e
  ser compatível com o código **que já está no ar**. O desenho e a reversibilidade dela são da `liquibase-migration`;
  aqui só se confirma que ela existe e que não derruba a versão atual durante a janela de deploy.
- **Config é contrato.** Uma chave que o código lê em runtime e que falta no ConfigMap ou no ExternalSecret não aparece
  no build nem no lint: o pod sobe e quebra na primeira requisição. A lista de chaves do `.env.example` é o contrato a
  conferir.
- **O deploy não acaba no `Synced`.** ArgoCD verde significa que os manifests foram aplicados, não que o serviço
  responde nem que está sendo observado. O pós-deploy fecha o loop: readiness, smoke test e sinal chegando na
  observabilidade.
- **Rollback definido antes de subir.** O caminho de volta é decidido na fase pré, não improvisado no incidente. Se a
  migração não permite reverter o app sozinho, isso é um risco conhecido antes do deploy, não uma surpresa.
- **Comente o mínimo.** Se precisar ajustar um manifesto na promoção, reduza os comentários ao estritamente necessário —
  o YAML já é declarativo. Só comente o *porquê* de um valor não óbvio (um limite, uma anotação de hook); comentário que
  repete o que a chave já diz é ruído.
- **Só lê e checa.** Os comandos servem para inspecionar (`kubectl`, `git`, `grep`, `curl`) e provar. Alterar manifest,
  rodar a migração ou dar o `argocd sync` é ação do usuário ou de quem opera, com o usuário ciente.

## Checklist PRÉ-deploy

Rode cada item e anote a evidência. Qualquer `CRITICAL` aberto reprova a promoção.

1. **Migração Liquibase pronta e compatível.** *Por quê:* o Job PreSync (wave 1) vai aplicá-la antes do app; se ela
   quebra, nada sobe. E durante a janela de deploy a versão antiga do código ainda está no ar contra o schema já migrado.
   *Como checar:* confirme com a `liquibase-migration` que o changeset está escrito, tem rollback e é **expand/contract**
   quando a mudança quebraria o código atual (nunca um `DROP`/`RENAME` destrutivo na mesma rodada que o código que ainda
   depende da coluna). Veja a imagem do Job em `infra/<serviço>/<ambiente>/liquibase.yaml`.
2. **ConfigMap e ExternalSecret com todas as chaves exigidas.** *Por quê:* chave faltando no `<serviço>-config` ou no
   `<serviço>-secret` não falha no build — o pod sobe e estoura em runtime quando o código lê a variável. *Como checar:*
   compare as duas listas. As chaves que o código espera estão em `.env.example` na raiz do repo; as entregues estão no
   `data:` do `config.yaml` (ConfigMap) e no `data:` do `secrets.yaml` (ExternalSecret, que puxa do `ClusterSecretStore`
   por `secretKey`). Toda chave do `.env.example` precisa aparecer num dos dois. Qualquer sobra ou falta é finding.

   ```bash
   # chaves que o código espera (nomes antes do '=')
   grep -oE '^[A-Z_]+' /home/fafnir/Projects/Synpower/<repo>/.env.example | sort -u
   # chaves entregues pelo ConfigMap
   grep -oE '^  [A-Z_]+:' infra/<serviço>/<ambiente>/config.yaml
   # chaves entregues pelo ExternalSecret
   grep -oE 'secretKey: [A-Z_]+' infra/<serviço>/<ambiente>/secrets.yaml
   ```
3. **Imagem é a do commit/tag certo.** *Por quê:* `image: registry.synchro.com.br/.../api:latest` promove o que o
   registry tiver em `latest` naquele instante — pode ser um build velho ou um que ninguém validou. *Como checar:* no
   `deployment.yaml`, confirme que a tag corresponde ao commit que se quer subir. Se o padrão do serviço fixa tag por
   release (o CI tem `docker-build-release`/`create-tag`), um `latest` solto é finding. Confirme que a imagem existe no
   registry.
4. **Probes e sync-waves corretos.** *Por quê:* sem `readinessProbe` o Service manda tráfego para um pod que ainda está
   subindo; waves trocadas fazem o app subir antes da migração. *Como checar:* no `deployment.yaml` confirme
   `readinessProbe` e `livenessProbe` apontando para `/api/v1/health/ready` e `/api/v1/health/live` na porta `8000`, com
   `initialDelaySeconds` folgado (o serviço demora ~60–90s no startup — um valor baixo mata o pod antes dele ficar
   pronto). Confirme os waves: ConfigMap/Secret `0`, Liquibase `1`, Deployment `2`.

## Checklist PÓS-deploy

Depois do `sync`, confirme nesta ordem — cada passo só faz sentido se o anterior passou.

1. **Job de migração concluído.** *Por quê:* é o wave 1; se ele não terminou `Complete`, o app nem subiu. *Como checar:*

   ```bash
   kubectl -n <namespace> get job <serviço>-liquibase-migration
   kubectl -n <namespace> logs job/<serviço>-liquibase-migration   # em caso de falha
   ```
2. **Pod passou no readiness.** *Por quê:* `Running` não é `Ready`; o Service só roteia para pods prontos. *Como checar:*
   `kubectl -n <namespace> get pods -l app=<serviço>` até `READY 1/1`. Depois um smoke test no endpoint crítico (não só o
   health): uma requisição real que exercite o caminho principal do serviço e volte `2xx` com corpo esperado.

   ```bash
   kubectl -n <namespace> get pods -l app=<serviço>
   curl -fsS https://<host-do-ingress>/<prefixo>/api/v1/health/ready
   ```
3. **Observabilidade recebendo sinal.** *Por quê:* fecha o loop com a `observability-structure`/`observability-coverage`:
   o deploy pode estar `Synced` e `Ready` e ainda assim **cego** — se o Grafana/Tempo/Loki seguem sem dado do serviço,
   não há como ver o próximo incidente. *Como checar:* o serviço exporta via OTel (no ConfigMap: `OTEL_ENDPOINT`
   apontando para o `alloy`, `SERVICE_NAME`, `DEPLOYMENT_ENVIRONMENT`). Confirme que chegam traces/métricas/logs novos
   desse `SERVICE_NAME` depois do deploy. Se não chegam, o deploy "funcionou" mas está cego: finding `WARNING` que fica
   para a `observability-coverage`.

## Rollback

Decida o caminho na fase pré; aqui está o procedimento.

- **App (quase sempre basta).** Reverta a imagem do Deployment para a tag anterior e sincronize — ou, mais simples,
  reverta o commit do manifest e deixe o ArgoCD reconciliar. Confirme o rollback com o mesmo readiness + smoke test do
  pós-deploy.
- **Banco (só se a migração não é compatível com a versão anterior).** *Por que normalmente não precisa:* uma migração
  **expand/contract** bem-feita (da `liquibase-migration`) mantém o schema compatível com a versão anterior do código —
  a fase expand só adiciona, nunca remove o que o código antigo usa. Então reverter o app **não** exige reverter o banco,
  e é por isso que o rollback é barato. *Quando precisa:* se a migração desta rodada foi destrutiva ou incompatível,
  rode o rollback do Liquibase (`rollback`/`rollbackCount`) **na ordem inversa dos changesets**, e só depois reverta o
  app — nessa ordem, para o schema nunca ficar à frente do código que vai responder. Essa é a situação a ter marcado como
  risco desde a fase pré.

## Promover para um ambiente novo (staging/prod)

Hoje só existe o ambiente `dev` (namespace tipo `ai-dev`); parte do valor da skill é dizer o que um ambiente novo
precisa ter. Copie `infra/<serviço>/dev/` para `infra/<serviço>/<novo-ambiente>/` e ajuste **sem inventar valores** —
cada valor que não vier do usuário ou de outro manifest fica `A definir`:

| O que ajustar | Onde | Nota |
| --- | --- | --- |
| `namespace` | todos os manifests | o novo namespace do ambiente — `A definir` |
| Host do Ingress | `ingress.yaml` (`Host(...)`), e o `PathPrefix`/middleware se mudar | o domínio do ambiente — `A definir` |
| Tag da imagem | `deployment.yaml` | a release que vai para o ambiente, não um `latest` de dev |
| `replicas` e `resources` | `deployment.yaml` | capacidade do ambiente — `A definir` com o usuário |
| Valores de config | `config.yaml` | hosts de banco, URLs de dependências, `DEPLOYMENT_ENVIRONMENT`, endpoint de observabilidade do ambiente — `A definir` |
| Origem dos segredos | `secrets.yaml` | o `remoteRef.key` do `ClusterSecretStore` aponta para o caminho do novo ambiente — `A definir` |

Mantenha os sync-waves e as probes iguais aos de `dev`: a estrutura do rito (migração PreSync antes do app) é a mesma em
qualquer ambiente. O que muda é o endereço, a capacidade e de onde vêm config e segredo.

## Veredito

Feche com um veredito simples, no espírito da `code-review-reliability` — só lê e checa, a ação é do usuário:

```text
PRONTO | NÃO PRONTO

Serviço: <serviço>  Ambiente: <ambiente>  Imagem: <tag>

Pré-deploy:
  [ok|CRITICAL|A verificar] Migração compatível — <evidência>
  [ok|CRITICAL|A verificar] Config e Secret completos — <chaves faltando, ou "nenhuma">
  [ok|CRITICAL|A verificar] Imagem correta — <tag vs commit>
  [ok|CRITICAL|A verificar] Probes e sync-waves — <evidência>

Pós-deploy (se já subiu):
  [ok|CRITICAL|A verificar] Job de migração Complete — <evidência>
  [ok|CRITICAL|A verificar] Pod Ready + smoke test — <evidência>
  [ok|WARNING|A verificar]  Observabilidade recebendo sinal — <evidência>

Rollback: <reverter imagem para <tag anterior>; migração compatível? sim/não>

Falta para ficar PRONTO:
  <item, um por linha, ou "nada">
```

`NÃO PRONTO` quando sobra qualquer item `CRITICAL`. O `WARNING` da observabilidade não bloqueia a subida, mas vai
listado para virar tarefa da `observability-coverage`.
