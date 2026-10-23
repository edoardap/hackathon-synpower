---
name: api-design
description: 'Ajuda a desenhar e evoluir APIs (REST/HTTP, webhooks e contratos entre módulos): recursos e endpoints, métodos, formato de requisição e resposta, erros, paginação, autenticação, idempotência, versionamento e mudanças compatíveis ou que quebram clientes. Use sempre que o usuário pedir para "desenhar a API", "definir os endpoints", "contrato da API", "OpenAPI/Swagger", "como versionar", "esse campo quebra o cliente?", "como receber webhook", revisar uma API existente, ou transformar histórias e requisitos em endpoints, mesmo que não diga a palavra "API".'
---

# API Design

Desenha o contrato de uma API a partir dos requisitos e avalia mudanças em APIs existentes. O contrato é a parte mais cara de mudar, porque clientes dependem dele. Por isso o desenho é feito antes do código e as mudanças são julgadas pelo que quebram.

## Princípios

- **Parta do consumidor e dos requisitos.** Cada endpoint deve existir por causa de uma história ou requisito. Cite a origem (RF, HU). Endpoint sem origem é especulação.
- **Siga o que já existe.** Em API existente, mantenha nomes, formato de erro, paginação e autenticação. Consistência vale mais do que a convenção "ideal". Se não conhecer o repositório, use a skill `repo-orientation` e consulte o `graphify` quando houver `graphify-out/`.
- **Respeite as decisões já registradas.** Leia os ADRs com status `Aceito` em `docs/adr/` antes de desenhar. Siga-os ou, se o contrato exigir contradizer um, diga isso e proponha um ADR que o substitua (`adr-writer`).
- **Compatível por padrão.** Adicionar campo opcional ou endpoint novo não quebra ninguém. Remover, renomear, mudar tipo ou tornar obrigatório quebra.
- **Segurança no contrato.** Defina autenticação, autorização por recurso (um usuário só acessa o que é dele) e o que nunca é devolvido (segredos, tokens de terceiros).
- **Não invente números.** Limites, tamanhos de página e prazos de depreciação ficam `A definir` se ninguém os informou.

## Passos: desenhar

1. **Levante recursos.** Liste os substantivos do domínio e suas relações a partir dos requisitos ou das histórias.
2. **Mapeie operações.** Para cada história, defina método e caminho. Consulte `references/convencoes.md` para nomes, métodos, status, erros, paginação e idempotência.
3. **Detalhe cada endpoint:** requisição (campos, obrigatórios, validações), resposta de sucesso, erros possíveis, autorização.
4. **Defina o transversal:** autenticação, formato único de erro, paginação, versionamento, idempotência de operações que criam coisas, limites a definir.
5. **Webhooks recebidos** (ex.: mensagens de um canal externo): valide a origem, responda rápido, trate duplicidade e processe em segundo plano.
6. **Registre pendências** e decisões relevantes (ofereça um ADR com `adr-writer`).

## Passos: evoluir

1. Compare o contrato antigo com o novo e classifique cada diferença como **compatível** ou **quebra**.
2. Para cada quebra, proponha uma alternativa compatível (campo novo, endpoint novo, valor padrão). Se não houver, proponha nova versão com plano de migração.
3. Se não houver clientes além do próprio projeto (ex.: PoC), diga isso: a quebra custa pouco e o versionamento formal pode esperar.

## Formato da resposta

```
## API: <tema>

### Recursos
- <recurso>: <descrição> (origem: RF-xx / HU-xx)

### Endpoints
| Método e caminho | Objetivo | Auth | Sucesso | Erros |
|---|---|---|---|---|

### Detalhe: <endpoint>
Requisição: ...
Resposta: ...

### Transversal
- Autenticação: ... | Erros: ... | Paginação: ... | Versionamento: ...

### Pendências
- ...
```

Se o usuário pedir OpenAPI, gere o YAML a partir desse desenho e salve onde ele indicar, sem sobrescrever arquivo existente. Mantenha o desenho enxuto e não proponha endpoints fora do escopo confirmado.
