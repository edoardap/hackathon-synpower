---
name: diff-review
description: Review humano do diff entre duas branches locais, num HTML no estilo de MR do GitHub/GitLab em que o usuário anota linhas e arquivos e compila as notas num Markdown para o agente de codificação. Use quando o pedido for ver, revisar ou comparar a implementação de uma branch contra outra ("quero ver o diff da dev com a branch da issue", "gera o review do ai-agents", "/diff-review"), ou aplicar o Markdown de notas que saiu desse review. Revisão feita pelo próprio agente é da code-review.
---

# Diff Review

O `tools/diff-review` gera um HTML com o diff de MR entre duas branches locais de um repositório do workspace:
`git diff base...head`, contado a partir do merge-base. O usuário revisa no navegador, anota linhas e arquivos e, em
"Finalizar review", copia um Markdown com as observações numeradas. A skill tem dois ramos: **gerar o review** e
**aplicar as notas**.

## Gerar o Review

1. **Resolva o repositório, a head e a base.** Cada uma termina numa ref que existe no repositório.

   - **Repositório:** caminho do repositório; `.` quando a sessão está aberta nele.
   - **head:** a branch com a implementação. Sem indicação, é a branch atual do repositório
     (`git -C <repo> branch --show-current`). Quando o pedido citar uma issue, a branch costuma começar pelo número dela
     (`170-feat-vinculo-de-ferramentas-por-versao`); confira com `git -C <repo> branch`.
   - **base:** o alvo do MR. Sem indicação, use `dev` quando existir, senão `main`, e diga ao usuário qual escolheu.

2. **Confira o que fica de fora.** O relatório compara commits. Se `git -C <repo> status --porcelain` listar arquivos,
   avise o usuário de que essas mudanças não commitadas ficam fora do review.

3. **Gere e abra:**

   ```bash
   ${CLAUDE_PLUGIN_ROOT}/tools/diff-review <repo> <base> <head> --open
   ```

   O comando imprime o caminho do HTML em `.cache/diff-review/`, fora do git. Ref inexistente encerra com a lista das
   branches locais. Para mais contexto em volta de cada mudança, acrescente `-U 20`.

4. **Entregue o caminho local** como link, com o resumo do diff: arquivos e linhas por
   `git -C <repo> diff --shortstat <base>...<head>`, commits por `git -C <repo> rev-list --count <base>..<head>`. O HTML
   carrega o código do repositório, por isso fica só na máquina do usuário, sem publicação como Artifact.

## O que o HTML Oferece

Consulte esta seção para responder dúvidas do usuário sobre a página.

- **Notas de linha:** o `+` azul aparece ao passar o mouse na linha; Shift+clique em outro `+` do mesmo arquivo marca um
  intervalo. Cada nota guarda o trecho do diff e pode ser editada ou excluída.
- **Nota de arquivo:** o botão "Nota no arquivo", no cabeçalho de cada arquivo.
- **Navegação:** árvore com filtro, unificado ou lado a lado, um arquivo por vez, "Visto" com barra de progresso.
  Lockfiles e arquivos com mais de 600 linhas alteradas chegam recolhidos.
- **Arquivo completo:** o botão abre outra aba (`#completo=<caminho>`) com o arquivo inteiro da base e da head lado a
  lado e navegação entre os trechos alterados. A aba é só de leitura.
- **Finalizar review:** comentário geral e o Markdown compilado, para copiar ou baixar em `.md`.
- **Persistência:** as notas ficam no `localStorage` do navegador, na chave do repositório, da base e da head. Regerar o
  HTML mantém as notas; a nota cuja linha saiu do diff aparece em "Notas em linhas que não estão mais no diff". Limpar
  os dados do navegador apaga as notas, por isso o `.md` baixado é a cópia segura.
- **Commits novos na head:** o usuário roda o mesmo comando e recarrega a página, sem passar pelo agente.
- **Celular (até 768 px):** o diff fica sempre unificado, com rolagem horizontal no código. A árvore abre como gaveta
  pelo botão ☰, e "Finalizar review" flutua no canto. O toque no número da linha abre a nota, e "Estender intervalo", no
  formulário, troca o Shift+clique. No arquivo completo, base e head aparecem unificadas, e os botões de mudança
  anterior e próxima ficam no canto inferior.
- **Realce de sintaxe:** vem do CDN do highlight.js; sem internet, o código aparece sem cores.

## Aplicar as Notas

O Markdown do review começa com `# Review de código: <repo>`, traz as instruções para o agente e as observações
numeradas por arquivo.

1. **Confira a branch.** `git -C <repo> branch --show-current` precisa ser a "Branch revisada" do cabeçalho do Markdown.
   Se for outra, pergunte ao usuário antes de editar.
2. **Avalie cada observação com `receiving-code-review`**, contra o arquivo atual. O bloco `diff` da observação localiza
   o trecho quando a linha mudou de número desde o review.
3. **Responda com uma linha por observação**, pelo número, dizendo o que foi feito ou por que não foi aplicada.

## Manutenção

O gerador é `tools/diff-review` (Python, só biblioteca padrão) e a página é o modelo `tools/lib/diff-review.html`.
Mudança de layout ou de comportamento das notas entra no modelo, e o próximo `tools/diff-review` já gera com ela. Depois
de alterar qualquer um dos dois, rode `sh tests/test-diff-review.sh`.
