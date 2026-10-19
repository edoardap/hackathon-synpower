# Convenções de API HTTP

Padrões de partida. Se o projeto já tem convenção diferente, ela vence.

## Recursos e caminhos
- Substantivos no plural: `/agents`, `/agents/{id}/bots`. Verbo só em ações que não cabem em CRUD: `POST /agents/{id}/publish`.
- Hierarquia só quando o filho não existe sem o pai. Evite mais de 2 níveis.
- Identificadores opacos nos caminhos, não dados do usuário.

## Métodos e status
| Método | Uso | Sucesso |
|---|---|---|
| GET | ler, sem efeito colateral | 200 |
| POST | criar ou ação | 201 (criou) / 200 / 202 (assíncrono) |
| PUT | substituir inteiro | 200 / 204 |
| PATCH | alterar parcialmente | 200 |
| DELETE | remover | 204 |

Erros: 400 requisição inválida, 401 não autenticado, 403 sem permissão, 404 não encontrado (também para recurso de outro usuário, para não revelar existência), 409 conflito (ex.: token já em uso), 422 validação de regra, 429 limite excedido, 5xx falha do servidor.

## Formato de erro
Um só formato em toda a API, por exemplo: `{"error": {"code": "token_in_use", "message": "...", "details": []}}`. O `code` é estável e legível por máquina, a `message` é para humanos.

## Paginação, filtro e ordenação
- Listas que podem crescer sempre têm paginação. Cursor é mais robusto que offset quando os dados mudam. O tamanho padrão e o máximo ficam `A definir`.
- Filtros e ordenação por query string, com nomes previsíveis.

## Idempotência
- GET, PUT e DELETE já são idempotentes.
- POST que cria algo caro ou sensível aceita uma chave de idempotência no cabeçalho para repetições seguras.

## Autenticação e autorização
- Autenticação por token no cabeçalho, nunca na URL.
- Autorização por recurso em todo endpoint: verifique que o recurso pertence ao usuário autenticado.
- Nunca devolva segredos (tokens de terceiros, senhas) nas respostas nem em logs. Quando for preciso mostrar, mostre mascarado.

## Versionamento
- Prefira evoluir sem quebrar. Só crie versão nova quando não houver como.
- Escolha um mecanismo (prefixo `/v1` ou cabeçalho) e use sempre o mesmo.
- Plano de depreciação (aviso, prazo) fica `A definir` se ninguém informou.

## Compatível ou quebra?
- **Compatível:** novo endpoint, novo campo opcional na resposta, novo campo opcional na requisição, novo valor aceito em campo livre.
- **Quebra:** remover ou renomear campo ou endpoint, mudar tipo ou formato, tornar campo obrigatório, mudar significado, mudar código de status ou formato de erro, apertar validação.
- Cuidado com enums: adicionar valor pode quebrar clientes que não esperam valores novos.

## Webhooks recebidos
- Valide a origem (segredo ou assinatura definidos pela plataforma) antes de processar.
- Responda 2xx rápido e processe em segundo plano, senão o emissor reenvia.
- Trate duplicidade: o mesmo evento pode chegar mais de uma vez, então use o identificador do evento.
- Registre o payload bruto de forma segura para depuração, sem segredos.
