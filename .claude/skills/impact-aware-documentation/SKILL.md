---
name: impact-aware-documentation
description: Analisar PRs, MRs, commits ou diffs entre branches para identificar o impacto na documentação e atualizar somente o conteúdo afetado (README.md, docs/, APIs, exemplos, configurações, diagramas, changelogs). Use sempre que houver um PR/MR ou uma comparação entre branches, tags ou commits e o usuário perguntar "a doc precisa mudar?", "atualiza a documentação desse PR", "o que esse diff quebra na doc?", ou quando uma mudança de código mexer em API, configuração, instalação, dependências, comandos, arquitetura ou comportamento visível, mesmo que ele não fale em documentação. Não use para criar a documentação inicial de um projeto sem base comparável; nesse caso use `source-grounded-documentation`.
---

# Impact-Aware Documentation

Avalia o impacto documental de uma mudança de código antes de editar qualquer arquivo. Compara uma versão `base` com uma `head`, relaciona o que mudou no código à documentação existente e atualiza só o conteúdo afetado, com base em evidência verificável. Editar só o necessário preserva o trabalho manual e mantém a revisão humana rápida.

## Entradas

Obtenha: repositório e raiz Git, `base` e `head` (branch, tag ou commit), identificador e descrição do PR/MR, caminhos autorizados para escrita, políticas de aprovação, publicação e arquivos gerados, e as verificações obrigatórias do projeto.

Se `base` ou `head` forem ambíguos, não presuma `main`, `master` nem a branch atual. Registre a ambiguidade e peça confirmação quando ela puder mudar o resultado.

## Workflow

### 1. Preparar a comparação

- Leia as instruções aplicáveis e identifique a estrutura documental.
- Verifique a árvore de trabalho e identifique alterações preexistentes. Não as sobrescreva nem as misture ao diff analisado.
- Obtenha estatísticas, arquivos alterados, diff completo e histórico relevante, confirmando que a comparação usa o merge-base correto ou a referência do PR/MR.
- Inventarie `README.md`, `docs/`, exemplos, schemas, OpenAPI, frontmatter, diagramas, changelogs e arquivos gerados.

### 2. Mapear o impacto

Para cada arquivo de código alterado, procure relação com símbolos, endpoints e comandos citados na documentação, configurações e variáveis de ambiente, manifests, lockfiles, Docker, `Makefile` e scripts, testes e exemplos de comportamento público, e páginas, links, âncoras, diagramas, índices e changelogs.

Registre num mapa de impacto:

```text
code_path | change | candidate_docs | reason | impact | confidence | action
```

Um documento só é afetado se houver relação concreta com a mudança; compartilhar palavra-chave não basta.

### 3. Classificar

- `mechanical`: renomeação, caminho, assinatura ou exemplo diretamente rastreável.
- `contractual`: API, schema, configuração, compatibilidade ou comportamento público.
- `semantic`: arquitetura, fluxo, segurança, trade-off ou regra de negócio.
- `unknown`: evidência insuficiente ou fontes em conflito.
- `none-known`: nenhuma relação documental comprovada.

`contractual` e `semantic` exigem revisão humana. `unknown` não é atualizado automaticamente.

### 4. Planejar antes de editar

Produza um plano com: documentos afetados e alterações necessárias, afirmações a reavaliar, documentos analisados que não mudam (com a evidência), fontes de cada afirmação, exemplos, diagramas e changelogs a atualizar, e verificações necessárias.

Exija validação humana se a mudança afetar objetivo geral, escopo ou terminologia de negócio. Não edite enquanto houver ambiguidade relevante.

### 5. Atualizar incrementalmente

- Altere só o necessário e preserve conteúdo manual e seções não afetadas.
- Mantenha `README.md` e `docs/` como estrutura oficial.
- Atualize requisitos, instalação, variáveis, execução e testes quando o diff os afetar; o mesmo vale para referências de API, schemas e exemplos quando contratos ou respostas mudarem.
- Use operações idempotentes e delimitadas em blocos gerados.
- Se a evidência de um conteúdo sumiu, marque-o como desatualizado e peça decisão; só remova com política explícita.
- Não altere código, dependências, infraestrutura ou workflows para a documentação parecer correta ou passar nas verificações.

### 6. Validar

Execute o que couber ao impacto: links, âncoras, frontmatter e navegação; exemplos e snippets afetados; comandos de instalação, execução e testes modificados; lint, type-check, build e testes relevantes; OpenAPI e schemas; diagramas e renderização.

Confirme que as afirmações afetadas refletem a nova versão, que nada relevante ficou desatualizado, que as mudanças documentais se ligam ao diff e que nada preexistente foi removido ou sobrescrito. Registre cada verificação como `pass`, `fail` ou `skipped`, com o motivo quando não executada.

### 7. Reportar

Entregue um relatório para revisão humana rápida: resumo do impacto, código analisado, documentos alterados e documentos avaliados sem mudança (com evidência), verificações e resultados, conteúdo desatualizado ou sem comprovação, riscos, pendências e se há revisão humana necessária.

Não faça commit, push, merge, publicação nem auto-merge por padrão.

## Critérios de bloqueio

Bloqueie ou peça revisão humana quando:

- `base` ou `head` forem ambíguos;
- o diff tiver mudança relevante de segurança, privacidade, contrato ou compatibilidade;
- faltar evidência para saber se um documento foi afetado;
- a atualização exigir interpretar intenção de produto ou regra de negócio;
- comandos ou conteúdo documental não puderem ser validados;
- o PR/MR misturar alterações locais não relacionadas;
- remover página ou afirmação exigir decisão editorial.

Quando possível, apresente o resultado parcial, os bloqueios e as ações para prosseguir. Não invente informação nem declare a análise concluída para contornar um bloqueio.

## Formato de saída

Retorne JSON com esta estrutura (ou os mesmos campos em Markdown, se o ambiente não permitir JSON), adaptando os valores ao resultado real:

```json
{
  "status": "changed|unchanged|blocked",
  "skill": "impact-aware-documentation",
  "scope": {"repository": "...", "base": "...", "head": "...", "pr_or_mr": "...", "paths": []},
  "changed_code": [],
  "impact_map": [
    {
      "code": "...",
      "docs": [],
      "impact": "mechanical|contractual|semantic|unknown|none-known",
      "evidence": [],
      "confidence": "high|medium|low",
      "action": "update|review|no-change|blocked"
    }
  ],
  "changed_docs": [],
  "reviewed_without_change": [],
  "stale_or_unproven": [],
  "checks": [{"command": "...", "result": "pass|fail|skipped", "reason": "..."}],
  "human_validation": [],
  "review_required": true,
  "risks": [],
  "next_steps": []
}
```

Não invente arquivo alterado, evidência ou verificação. Não classifique uma página como `no-change` sem registrar a evidência, nem uma verificação como `pass` sem executá-la ou sem fonte autoritativa explícita.
