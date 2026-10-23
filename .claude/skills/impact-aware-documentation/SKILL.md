---
name: impact-aware-documentation
description: Analisar PRs, MRs, commits ou diffs entre branches para identificar impactos na documentação e atualizar somente o conteúdo afetado. Usar quando mudanças de código puderem afetar README.md, docs/, APIs, exemplos, configurações, diagramas ou changelogs.
---

# Impact-Aware Documentation

## Objetivo

Avaliar o impacto documental de uma mudança de código antes de editar qualquer arquivo.

Comparar uma versão base com uma versão atualizada, relacionar as alterações de código à documentação existente e atualizar somente o conteúdo afetado, com base em evidências verificáveis.

## Quando usar

Use esta Skill quando houver:

- Um pull request (PR) ou merge request (MR).
- Uma comparação entre branches, tags ou commits.
- Alterações em APIs, configurações, instalação, dependências, comandos, arquitetura, fluxos ou comportamentos visíveis aos usuários.
- Necessidade de verificar se a documentação está pronta para acompanhar uma mudança.

Não use esta Skill para criar a documentação inicial de um projeto sem uma base comparável. Nesse caso, utilize `source-grounded-documentation`.

## Entradas necessárias

Obtenha:

- Repositório e raiz Git.
- `base` e `head`, identificados por branch, tag ou commit.
- Identificador e descrição do PR/MR, quando disponíveis.
- Caminhos autorizados para escrita.
- Políticas de aprovação, publicação e geração de arquivos.
- Verificações obrigatórias do projeto.

Se `base` ou `head` forem ambíguos, não presuma que correspondem a `main`, `master` ou à branch atual. Registre a ambiguidade e solicite confirmação quando ela puder alterar o resultado da análise.

## Workflow

### 1. Preparar a comparação

1. Identifique as instruções aplicáveis e a estrutura documental do repositório.
2. Verifique o estado da árvore de trabalho e identifique alterações preexistentes.
3. Obtenha as estatísticas, a lista de arquivos alterados, o diff completo e o histórico relevante.
4. Confirme que a comparação utiliza o merge-base correto ou a referência aprovada pelo PR/MR.
5. Inventarie `README.md`, `docs/`, exemplos, schemas, OpenAPI, frontmatter, diagramas, changelogs e arquivos gerados.

Não sobrescreva alterações locais preexistentes nem as misture silenciosamente ao diff analisado.

### 2. Mapear o impacto documental

Para cada arquivo de código alterado, investigue possíveis relações com:

- Símbolos, classes, funções, endpoints e comandos mencionados na documentação.
- Configurações e variáveis de ambiente.
- Manifests, lockfiles, Docker, Compose, `Makefile` e scripts.
- Testes e exemplos que descrevam comportamentos públicos.
- Páginas, links, âncoras, diagramas, índices e changelogs.

Registre os resultados em um mapa de impacto:

```text
code_path | change | candidate_docs | reason | impact | confidence | action
```

Não classifique um documento como afetado apenas por compartilhar palavras-chave com o código alterado. Identifique uma relação concreta entre a mudança e o conteúdo documental.

### 3. Classificar as mudanças

Classifique cada impacto identificado em uma das seguintes categorias:

- **Mecânico (`mechanical`):** renomeações, caminhos, assinaturas ou exemplos diretamente rastreáveis.
- **Contratual (`contractual`):** alterações em APIs, schemas, configurações, compatibilidade ou comportamentos públicos.
- **Semântico (`semantic`):** alterações de arquitetura, fluxos, segurança, trade-offs ou regras de negócio.
- **Desconhecido (`unknown`):** evidências insuficientes ou conflitos entre fontes.
- **Sem impacto conhecido (`none-known`):** nenhuma relação documental comprovada.

Mudanças contratuais e semânticas exigem revisão humana. Mudanças classificadas como desconhecidas não devem ser atualizadas automaticamente.

### 4. Planejar antes de editar

Antes de modificar arquivos, produza um plano que identifique:

- Documentos afetados e alterações necessárias.
- Afirmações que precisam ser reavaliadas.
- Documentos analisados que não precisam de alterações e as evidências que justificam essa decisão.
- Estrutura prevista das alterações.
- Fontes que sustentam cada afirmação.
- Exemplos, diagramas e changelogs que precisam ser atualizados.
- Verificações e revisões necessárias.

Se a mudança afetar o objetivo geral, o escopo ou a terminologia de negócio, exija validação humana.

Não inicie a edição enquanto houver ambiguidades relevantes que possam comprometer a correção das alterações.

### 5. Atualizar a documentação incrementalmente

Altere somente o conteúdo necessário para refletir a nova versão do projeto.

- Preserve conteúdo manual e seções não afetadas.
- Mantenha `README.md` e `docs/` como estrutura documental oficial.
- Atualize requisitos, instalação, variáveis de ambiente, execução e testes quando o diff afetar esses aspectos.
- Atualize referências de API, schemas e exemplos quando contratos ou respostas forem alterados.
- Utilize operações idempotentes e delimitadas para atualizar blocos gerados.
- Não remova documentação apenas porque sua evidência desapareceu. Identifique o conteúdo como desatualizado e solicite uma decisão, salvo quando houver uma política explícita de remoção.

Não altere código, dependências, infraestrutura ou workflows para fazer a documentação parecer correta ou passar nas verificações.

### 6. Validar as alterações

Execute as verificações pertinentes ao impacto identificado:

- Links, âncoras, frontmatter e navegação.
- Exemplos e snippets afetados.
- Comandos de instalação, execução e testes modificados.
- Lint, type-check, build e testes relevantes.
- Validação de OpenAPI e schemas.
- Diagramas e renderização.
- Verificações específicas da documentação.

Confirme que:

- As afirmações afetadas refletem a nova versão do código.
- Nenhum conteúdo relevante ficou desatualizado.
- As alterações documentais estão relacionadas ao diff analisado.
- Nenhum conteúdo preexistente foi removido ou sobrescrito indevidamente.

Registre cada verificação como `pass`, `fail` ou `skipped`. Informe o motivo das verificações não executadas.

### 7. Reportar os resultados

Produza um relatório que permita uma revisão humana rápida.

Inclua:

- Resumo do impacto documental.
- Arquivos de código analisados e suas mudanças relevantes.
- Documentos alterados.
- Documentos avaliados, mas mantidos sem alterações.
- Evidências que sustentam as decisões.
- Verificações executadas e seus resultados.
- Conteúdo desatualizado ou sem comprovação.
- Riscos, pendências e próximos passos.
- Necessidade de revisão humana.

Não execute commits, pushes, merges, publicações ou auto-merge por padrão.

## Critérios de bloqueio

Bloqueie a conclusão ou solicite revisão humana quando:

- `base` ou `head` forem ambíguos.
- O diff contiver mudanças relevantes de segurança, privacidade, contratos ou compatibilidade.
- Não houver evidências suficientes para determinar se um documento foi afetado.
- A atualização exigir interpretar intenções de produto ou regras de negócio.
- Comandos ou conteúdo documental não puderem ser validados.
- O PR/MR misturar alterações locais não relacionadas.
- A remoção de uma página ou afirmação exigir uma decisão editorial.

Quando possível, apresente os resultados parciais, identifique os bloqueios e indique as ações necessárias para prosseguir.

Não invente informações nem declare a análise concluída para contornar um bloqueio.

## Formato de saída

Retorne os resultados em JSON, preferencialmente seguindo esta estrutura:

```json
{
  "status": "changed|unchanged|blocked",
  "skill": "impact-aware-documentation",
  "scope": {
    "repository": "...",
    "base": "...",
    "head": "...",
    "pr_or_mr": "...",
    "paths": []
  },
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
  "checks": [
    {
      "command": "...",
      "result": "pass|fail|skipped",
      "reason": "..."
    }
  ],
  "human_validation": [],
  "review_required": true,
  "risks": [],
  "next_steps": []
}
```

Adapte os valores ao resultado real da análise. Não invente arquivos alterados, evidências ou verificações.

Se o ambiente não permitir JSON, utilize os mesmos campos em Markdown.

Nunca classifique uma página como `no-change` sem registrar as evidências que justificam a decisão. Nunca marque uma verificação como `pass` sem executá-la ou sem uma fonte autoritativa explícita que comprove o resultado.