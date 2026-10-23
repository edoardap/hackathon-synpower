# Exemplos de Teste

Formas de teste para backend FastAPI com pytest e para frontend React com Playwright, no estilo do
`full-stack-fastapi-template`. Os nomes de fábrica (`create_random_opportunity`,
`user_token_headers_in_new_organization`) são exemplos: use as fábricas do repositório ou crie-as em `tests/utils/` no
formato das vizinhas.

## Regressão

O teste descreve o comportamento certo e falha enquanto o defeito existir. A falha mostra o valor errado:

```python
def test_read_opportunity_other_organization_returns_404(client: TestClient, db: Session) -> None:
    opportunity = create_random_opportunity(db)  # organização A
    headers = user_token_headers_in_new_organization(client, db)  # usuário da organização B

    response = client.get(f"{settings.API_V1_STR}/opportunities/{opportunity.id}", headers=headers)

    assert response.status_code == 404
```

Saída no código com o defeito, que vai para a entrega:

```text
FAILED tests/api/routes/test_opportunities.py::test_read_opportunity_other_organization_returns_404
    assert response.status_code == 404
E   assert 200 == 404
```

## Falha Esperada

Quando o teste entra antes da correção, marque-o como falha esperada **estrita**. A suíte segue verde, e o teste passa a
falhar quando o defeito for corrigido, avisando para tirar a marca.

**pytest:**

```python
@pytest.mark.xfail(strict=True, reason="F1 da revisão: leitura por id sem filtro de organização")
def test_read_opportunity_other_organization_returns_404(client: TestClient, db: Session) -> None:
    ...
```

**Playwright:**

```ts
test("rejects negative value", async ({ page }) => {
  test.fail(true, "F4 da revisão: valor negativo aceito")
  // ...
})
```

## Validação de Entrada

Um teste por limite, com o literal no esperado:

```python
@pytest.mark.parametrize("value", [-1, -0.01])
def test_create_opportunity_negative_value_returns_422(
    client: TestClient, normal_user_token_headers: dict[str, str], value: float
) -> None:
    data = {"title": "Renovação anual", "value": value, "stage": "prospecting"}

    response = client.post(f"{settings.API_V1_STR}/opportunities/", headers=normal_user_token_headers, json=data)

    assert response.status_code == 422
```

## Tela

O teste encontra os elementos pelo nome acessível e confere o que o usuário vê:

```ts
test("shows backend error when value is negative", async ({ page }) => {
  await page.goto("/opportunities")
  await page.getByRole("button", { name: "Add Opportunity" }).click()
  await page.getByLabel("Title").fill("Renovação anual")
  await page.getByLabel("Value").fill("-10")
  await page.getByRole("button", { name: "Save" }).click()

  await expect(page.getByText("Value must be zero or more")).toBeVisible()
})
```

## Mock

Simule só o que fica fora do sistema:

| Pode simular                             | Não simule                                     |
| ---------------------------------------- | ---------------------------------------------- |
| Envio de e-mail, API de terceiros        | As próprias rotas, serviços e funções de banco |
| Relógio (`datetime.now`) e aleatoriedade | O banco de teste, que o repositório já sobe    |
| Falha de rede de um serviço externo      | O componente React que está em teste           |

No template, o envio de e-mail já é simulado nos testes de rota com `unittest.mock.patch`
(`tests/api/routes/test_users.py`).
