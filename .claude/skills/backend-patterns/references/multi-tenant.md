# Isolamento por Organização

Regras para todo dado que pertence a uma organização (*tenant*). Um vazamento entre organizações expõe dado de um
cliente a outro, por isso cada regra abaixo vale para toda rota, inclusive as de listagem e de contagem.

## Regras

1. **Coluna obrigatória.** Toda tabela de organização tem `organization_id` com chave estrangeira para
   `organization.id`, `NOT NULL` e índice.
2. **Origem única.** O `organization_id` sai do usuário autenticado (`current_user.organization_id`). O schema de
   criação (`XCreate`) e o de atualização (`XUpdate`) não têm esse campo, e a rota o preenche com
   `update={"organization_id": ...}`.
3. **Filtro em toda consulta.** Listagem, contagem, leitura por id, atualização e exclusão filtram por
   `organization_id`. A leitura por id usa `select(...).where(X.id == id, X.organization_id == org_id)`, e não
   `session.get(X, id)` seguido de comparação, porque a comparação esquecida numa rota nova devolve o dado de outra
   organização.
4. **Recurso alheio responde 404.** Um id de outra organização recebe a mesma resposta de um id inexistente (`404` com o
   mesmo `detail`). Responder `403` confirma ao chamador que o recurso existe.
5. **Relacionamento na mesma organização.** Ao receber o id de outra entidade (uma oportunidade que aponta para um
   cliente), confira que ela pertence à mesma organização antes de gravar.
6. **Superusuário explícito.** Acesso entre organizações existe só em rota administrativa que já exija superusuário, com
   o motivo registrado no código vizinho ou no design.

## Leitura por Id

**Bom:** o filtro faz parte da consulta.

```python
def get_opportunity(*, session: Session, id: uuid.UUID, organization_id: uuid.UUID) -> Opportunity | None:
    statement = select(Opportunity).where(
        Opportunity.id == id,
        Opportunity.organization_id == organization_id,
    )
    return session.exec(statement).first()


@router.get("/{id}", response_model=OpportunityPublic)
def read_opportunity(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    opportunity = crud.get_opportunity(session=session, id=id, organization_id=current_user.organization_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity
```

**Ruim:** a consulta traz o registro de qualquer organização, e a proteção depende de uma comparação que a próxima rota
pode esquecer.

```python
opportunity = session.get(Opportunity, id)
if opportunity.organization_id != current_user.organization_id:
    raise HTTPException(status_code=403, detail="Not enough permissions")
```

## Teste Obrigatório

Toda rota que toca dado de organização ganha um teste com duas organizações. O teste cria o recurso na organização A e
chama a rota com o usuário da organização B.

| Rota                                     | Resultado esperado para o usuário de B               |
| ---------------------------------------- | ---------------------------------------------------- |
| Listagem                                 | O recurso de A não aparece e a contagem não o inclui |
| Leitura por id                           | `404`                                                |
| Atualização                              | `404`, e o recurso de A continua igual no banco      |
| Exclusão                                 | `404`, e o recurso de A continua no banco            |
| Criação com id de entidade de A no corpo | `404` ou `422`, e nada é gravado                     |

```python
def test_read_opportunity_other_organization(client: TestClient, db: Session) -> None:
    opportunity = create_random_opportunity(db)  # organização A
    headers = user_token_headers_in_new_organization(client, db)  # usuário da organização B

    response = client.get(f"{settings.API_V1_STR}/opportunities/{opportunity.id}", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Opportunity not found"
```

Os nomes `create_random_opportunity` e `user_token_headers_in_new_organization` são fábricas de teste que a
funcionalidade cria em `tests/utils/`, no formato das fábricas vizinhas.
