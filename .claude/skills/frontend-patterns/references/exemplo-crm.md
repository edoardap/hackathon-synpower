# Exemplos do Frontend de Referência

Trechos reais do [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template), commit
`b1125d8`, sem os *imports*. Os caminhos partem de `frontend/`. Use-os como molde para recurso novo no mesmo
repositório.

## Listagem com Espera e Estado Vazio

A página define a *query* com uma chave por recurso, envolve a tabela em `Suspense` com o componente de espera e trata a
lista vazia antes de desenhar a tabela (`src/routes/_layout/items.tsx:12-55`):

```tsx
function getItemsQueryOptions() {
  return {
    queryFn: async () =>
      (await ItemsService.readItems({ query: { skip: 0, limit: 100 } })).data,
    queryKey: ["items"],
  }
}

function ItemsTableContent() {
  const { data: items } = useSuspenseQuery(getItemsQueryOptions())

  if (items.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <h3 className="text-lg font-semibold">You don't have any items yet</h3>
        <p className="text-muted-foreground">Add a new item to get started</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={items.data} />
}

function ItemsTable() {
  return (
    <Suspense fallback={<PendingItems />}>
      <ItemsTableContent />
    </Suspense>
  )
}
```

O erro da *query* é capturado pelo `errorComponent` registrado na rota raiz (`src/routes/__root.tsx:17`), que desenha
`src/components/Common/ErrorComponent.tsx`. Toda tela nova herda esse tratamento.

## Formulário com Validação e Mutation

O formulário valida com zod, envia pelo cliente gerado, mostra o erro do backend em *toast* e invalida a chave da
listagem ao terminar (`src/components/Items/AddItem.tsx:33-70`):

```tsx
const formSchema = z.object({
  title: z.string().min(1, { message: "Title is required" }),
  description: z.string().optional(),
})

const form = useForm<FormData>({
  resolver: zodResolver(formSchema),
  mode: "onBlur",
  criteriaMode: "all",
  defaultValues: { title: "", description: "" },
})

const mutation = useMutation({
  mutationFn: (data: ItemCreate) => ItemsService.createItem({ body: data }),
  onSuccess: () => {
    showSuccessToast("Item created successfully")
    form.reset()
    setIsOpen(false)
  },
  onError: handleError.bind(showErrorToast),
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ["items"] })
  },
})
```

O botão de envio é o `LoadingButton` com `loading={mutation.isPending}`, e o de cancelar fica desabilitado durante o
envio (`src/components/Items/AddItem.tsx:126-135`).

## Erro do Backend

`handleError` extrai o `detail` da resposta do FastAPI, seja texto ou lista de erros de validação, e entrega a mensagem
ao *toast* (`src/utils.ts:3-20`). Formulário novo usa o mesmo `onError`.

## Teste de Tela

Os testes usam Playwright e encontram elementos pelo nome acessível (`tests/items.spec.ts:11-20`):

```ts
test("Items page is accessible and shows correct title", async ({ page }) => {
  await page.goto("/items")
  await expect(page.getByRole("heading", { name: "Items" })).toBeVisible()
  await expect(page.getByText("Create and manage your items")).toBeVisible()
})
```

Testes que criam dado fazem login com um usuário próprio, criado em `beforeAll` pela API privada de desenvolvimento
(`tests/items.spec.ts:22-35`).

## Verificação

Comandos do `package.json` e do `scripts/generate-client.sh`. O projeto usa `bun`:

```bash
bash scripts/generate-client.sh     # na raiz, depois de mudar o backend
cd frontend
bun run lint                        # Biome com --write
bun run build                       # tsc e vite build
bunx playwright test                # exige o backend e o frontend de pé
```
