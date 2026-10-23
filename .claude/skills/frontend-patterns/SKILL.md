---
name: frontend-patterns
description: 'Padrões para escrever e alterar frontend React com TypeScript: onde fica cada tela e componente, chamada à API pelo cliente gerado, dado do servidor com cache e invalidação, formulário com validação, estados de carregando, vazio e erro, e teste de tela. Use ao criar ou alterar página, rota, componente, formulário, tabela ou listagem num frontend React, e ao ligar uma tela a um endpoint novo do backend. O backend é da backend-patterns.'
---

# Frontend Patterns

Guia de implementação para frontend React com TypeScript. O código novo segue o padrão que o repositório já usa, toda
tela que busca dado trata os quatro estados (carregando, vazio, erro e sucesso) e toda chamada à API passa pelo cliente
tipado do projeto.

Nos caminhos abaixo, `${CLAUDE_SKILL_DIR}` é a pasta desta skill (`.claude/skills/frontend-patterns/`).

## Princípios

- **O vizinho manda.** Antes de criar uma tela, abra a tela mais parecida do repositório (outra listagem, outro
  formulário) e copie a estrutura, os componentes de UI, os nomes e a forma de teste dela. Biblioteca nova só entra
  quando o usuário pedir.
- **Cliente gerado.** Quando o repositório gera o cliente da API a partir do OpenAPI do backend, chamadas e tipos vêm
  dele. Endpoint novo no backend pede o cliente gerado de novo antes de escrever a tela.
- **Dado do servidor no cache.** Leitura usa a biblioteca de *query* do projeto (TanStack Query, SWR) com uma chave por
  recurso. Toda criação, edição ou exclusão invalida a chave do recurso que mudou, para a listagem se atualizar.
- **Quatro estados.** Carregando mostra o *skeleton* ou o componente de espera do projeto; vazio mostra uma mensagem e a
  ação de criar; erro mostra a mensagem que o backend devolveu; sucesso mostra o dado.
- **Validação nos dois lados.** O formulário valida com um schema (zod, yup) que repete os limites do backend:
  obrigatório, tamanho, mínimo e máximo. O backend continua sendo a regra, e o erro dele aparece para o usuário pelo
  tratamento de erro do projeto.
- **Autorização é do backend.** A tela envia só o que o usuário preencheu. `organization_id`, dono e permissões vêm do
  backend, e esconder um botão ou filtrar uma lista na tela não protege dado nenhum.
- **Acessível e testável.** Todo campo tem `label` ligado ao `input` e todo botão tem nome visível ou `sr-only`. Os
  testes de tela encontram os elementos por esse nome (`getByLabel`, `getByRole`).

## Passos

1. **Leia as regras.** Abra o `AGENTS.md` do repositório e, se existirem, o `CLAUDE.md` e o guia de contribuição. Anote
   os comandos de lint, de *build* e de teste do `package.json`.
2. **Leia os vizinhos.** Ache a tela mais parecida com a pedida e os componentes que ela usa. A organização do template
   de referência está em [Onde Fica Cada Código](#onde-fica-cada-c%C3%B3digo).
3. **Atualize o cliente.** Se a tela usa endpoint novo ou alterado, gere o cliente de novo com o comando do repositório
   e confira o tipo e o método novos no código gerado.
4. **Implemente.** Rota, componentes, item de navegação e os quatro estados, na estrutura da tela vizinha.
5. **Teste.** Escreva o teste de tela no formato dos vizinhos: a página abre, a criação aparece na lista, a validação
   bloqueia o envio inválido e o erro do backend aparece.
6. **Verifique.** Rode lint, *build* (que inclui a checagem de tipos) e os testes de tela. A tarefa termina quando os
   três passam.

## Onde Fica Cada Código

Organização do `full-stack-fastapi-template`, o CRM de referência. Em outro repositório, monte a tabela equivalente a
partir dos diretórios dele.

| Peça                   | Lugar                                                         | Observação                                                                        |
| ---------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Página                 | `src/routes/_layout/<recurso>.tsx`                            | `createFileRoute("/_layout/<recurso>")`, rota por arquivo                         |
| Componentes do recurso | `src/components/<Recurso>/`                                   | `Add<X>.tsx`, `Edit<X>.tsx`, `Delete<X>.tsx`, `<X>ActionsMenu.tsx`, `columns.tsx` |
| Espera da listagem     | `src/components/Pending/Pending<Recursos>.tsx`                | *Skeleton* com as mesmas colunas da tabela                                        |
| Componentes de UI      | `src/components/ui/`                                          | Button, Dialog, Form, Input, Table e afins; use-os em vez de HTML solto           |
| Item de navegação      | `src/components/Sidebar/AppSidebar.tsx`                       | Entrada em `baseItems`                                                            |
| Cliente da API         | `src/client/`                                                 | Gerado; métodos em `<Tag>Service`                                                 |
| Erro e aviso           | `src/utils.ts` (`handleError`), `src/hooks/useCustomToast.ts` | `onError: handleError.bind(showErrorToast)`                                       |
| Teste de tela          | `tests/<recurso>.spec.ts`                                     | Playwright                                                                        |

Trechos reais dessas peças, com arquivo e linha, estão em `${CLAUDE_SKILL_DIR}/references/exemplo-crm.md`.

## Armadilhas

- **Arquivo gerado.** `src/routeTree.gen.ts` (plugin do roteador) e `src/client/` (gerador do OpenAPI) são reescritos a
  cada geração. Altere a rota ou o backend e gere de novo; a edição à mão some na próxima geração.
- **Cliente desatualizado.** Tela escrita antes de gerar o cliente usa tipo ou método que ainda não existe, e o *build*
  falha. No template, o cliente sai de `scripts/generate-client.sh`, que exige o backend instalado com `uv`.
- **Chave de cache divergente.** A *mutation* invalida `["items"]`, mas a listagem consulta `["items", filtro]`. Use o
  mesmo prefixo, para a invalidação alcançar todas as variações.
- **Texto que o teste procura.** Os testes de tela encontram botões e títulos pelo texto. Renomear "Add Item" quebra o
  teste que procura esse nome; atualize os dois juntos.
- **Lint que reescreve.** No template, `bun run lint` roda o Biome com `--write`, que altera arquivos. Rode-o antes de
  listar os arquivos da entrega.
- **Gerenciador de pacotes.** O template usa `bun` (`bun.lock` na raiz). Instalar com outro gerenciador cria um segundo
  arquivo de *lock*.

## Formato da Entrega

```text
Arquivos alterados:
<caminho a partir da raiz do repositório>, um por linha

Cliente gerado:
<comando rodado, ou "não necessário: nenhum endpoint novo">

Testes novos:
<arquivo> — <o que prova>, um por linha

Verificação:
<comando de lint, de build e de teste, com as últimas linhas de cada saída>

Pendências:
<o que ficou de fora e por quê, ou "nenhuma">
```
