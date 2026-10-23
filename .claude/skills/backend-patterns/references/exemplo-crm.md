# Exemplos do Padrão Plano

Trechos reais do [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template), commit
`b1125d8`, base do CRM de referência, sem os comentários e as *docstrings* do original. Os caminhos partem de
`backend/`. Use-os como molde para entidade nova no mesmo repositório.

## Família de Modelos

Cada entidade tem uma família de classes em `app/models.py`. A tabela herda da base, e os schemas de entrada e saída
controlam o que o cliente envia e recebe (`app/models.py:69-105`):

```python
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)

class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User | None = Relationship(back_populates="items")

class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None

class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int
```

- `XCreate` e `XUpdate` não têm `owner_id`: a rota o preenche a partir do usuário. O `organization_id` segue a mesma
  regra.
- `XUpdate` tem todos os campos opcionais, e a rota aplica só os enviados com `model_dump(exclude_unset=True)`.
- `XsPublic` é o envelope de listagem, com `data` e `count`.

## Rota

A rota recebe a sessão e o usuário por dependência e registra o roteador com prefixo e *tag*
(`app/api/routes/items.py:10`, `app/api/main.py:10`). A criação preenche o dono pelo usuário autenticado
(`app/api/routes/items.py:61-72`):

```python
@router.post("/", response_model=ItemPublic)
def create_item(*, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate) -> Any:
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
```

> **Atenção:** a leitura por id do template usa `session.get(Item, id)` seguido de comparação do dono e responde `403`
> (`app/api/routes/items.py:53-57`). Para dado de organização, siga a forma de [multi-tenant.md](multi-tenant.md):
> filtro na consulta e `404`.

## Dependências

`SessionDep` e `CurrentUser` são `Annotated` com `Depends`, definidos em `app/api/deps.py:26` e `app/api/deps.py:49`.
Dependência nova, como a organização do usuário atual, segue a mesma forma no mesmo arquivo.

## Testes

Os testes de rota usam o `client` e os *headers* de token do `tests/conftest.py:27-42`, e criam dados com fábricas de
`tests/utils/` (`tests/utils/item.py`). Cada caso verifica o status e o corpo:

```python
def test_read_item_not_found(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    response = client.get(f"{settings.API_V1_STR}/items/{uuid.uuid4()}", headers=superuser_token_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
```

A fixture `db` do `conftest.py` apaga `Item` e `User` ao fim da sessão de testes (`tests/conftest.py:15-24`). Entidade
nova entra nessa limpeza, antes de `User`, por causa da chave estrangeira.

## Verificação

O `scripts/test.sh` da raiz falha porque a imagem do backend não copia `tests/`. Use o caminho do CI do template:

```bash
docker compose up -d --wait db mailpit
cd backend
uv run bash scripts/prestart.sh
uv run bash scripts/tests-start.sh
uv run coverage report --fail-under=90
uv run bash scripts/lint.sh
```
