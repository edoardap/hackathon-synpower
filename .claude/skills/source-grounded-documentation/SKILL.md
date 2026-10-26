---
name: source-grounded-documentation
description: Criar documentação inicial de um repositório (README.md e docs/) com base em código, testes, configuração e CI verificáveis, sem transformar suposição em fato. Use sempre que o README.md ou o docs/ estiver ausente, quando a documentação existente for insuficiente ou não confiável, ou quando o usuário pedir "documenta esse projeto", "cria o README", "como rodar isso?" ou "gera a documentação inicial", mesmo que ele não diga "source-grounded". Não use para atualizar a documentação a partir de um PR/MR ou diff específico; nesse caso use `impact-aware-documentation`.
---

# Source-Grounded Documentation

Cria uma base documental útil e verificável para um repositório, usando evidências reais. A documentação só vale se o leitor puder confiar nela: por isso cada afirmação relevante precisa de uma fonte, e o que não tem fonte fica marcado como lacuna.

A entrega mínima é um `README.md` na raiz e um `docs/` com páginas sustentadas por evidências.

## Entradas

Obtenha, quando disponíveis: raiz Git, branch e commit de referência, público-alvo e objetivo da documentação, caminhos autorizados para escrita, comandos obrigatórios e o responsável humano que valida o objetivo geral.

Se público-alvo, objetivo de negócio ou escopo de escrita forem desconhecidos, continue a investigação técnica e registre as lacunas. Não apresente interpretação não confirmada como fato.

## Workflow

### 1. Identificar o contexto

- Identifique raiz Git, branch, commit e estado do repositório.
- Leia `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING.md` e outras instruções aplicáveis.
- Avalie o `README.md` e o `docs/` existentes. Se já forem substanciais, prefira atualização incremental a reconstrução, para não perder conteúdo.

### 2. Inventariar o projeto

Investigue sem presumir tecnologia, nome de arquivo ou ferramenta. Fontes a considerar: manifests e lockfiles (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml` e equivalentes), automação (`Makefile`, `Taskfile`, scripts), containers e infraestrutura, configuração (`.env.example`, schemas), CI e release, implementação (entry points, rotas, módulos, testes, exemplos) e documentação existente.

Registre linguagens e versões, gerenciadores de pacotes, dependências e ferramentas externas, serviços auxiliares, portas, bancos, configurações necessárias e comandos de instalação, execução e validação. Diferencie requisito confirmado de requisito inferido.

### 3. Validar a inicialização

Trace o caminho de um checkout limpo até a aplicação funcionando: pré-requisitos, dependências, serviços e containers, variáveis de ambiente, inicialização, verificação e, por fim, testes, lint, type-check e build.

- Priorize comandos já definidos em manifests, scripts ou CI.
- Execute em sequência segura. Não instale dependências nem inicie serviços sem autorização e sem avaliar o impacto.
- Só declare um comando verificado se o executou ou se há fonte autoritativa explícita do comportamento dele.

### 4. Criar a estrutura

Crie arquivos só nos caminhos autorizados e reaproveite a estrutura existente quando for adequada. Sem estrutura prévia, considere: `docs/architecture.md`, `development.md`, `testing.md`, `configuration.md`, `operations.md`, `adr/` e `rfc/`. Crie apenas páginas com conteúdo sustentado por evidência ou pedido explícito; página vazia para "preencher estrutura" não ajuda ninguém.

### 5. Escrever o README

Siga esta ordem, adaptando ao projeto: nome e descrição factual; objetivo e público-alvo; estado e escopo conhecidos (sem presumir maturidade); pré-requisitos; instalação e inicialização; variáveis de ambiente; execução e verificação; testes, lint, type-check e build; links para a documentação complementar; limitações, troubleshooting e próximos passos, quando sustentados por evidência.

O objetivo geral deve ser escrito ou validado pelo responsável humano. Sem confirmação, marque como `A validar pelo responsável`.

Para cada variável de ambiente relevante, documente nome, finalidade, obrigatoriedade, formato esperado e exemplo seguro. Nunca copie valores reais de `.env`, CI ou sistemas de secrets.

### 6. Escrever a documentação complementar

Priorize o que ajuda a compreender, desenvolver, testar e operar: arquitetura (componentes e fluxos observados), ambiente de desenvolvimento, comandos de teste, configuração e, só com evidência suficiente, operação e troubleshooting. Referencie arquivos, módulos, comandos e outras páginas. Aponte decisões que dependem de conhecimento humano e o que não foi confirmado.

### 7. Validar e revisar

Execute o que couber no stack: lint de Markdown/MDX, links e âncoras, comandos de instalação e inicialização, testes, lint, type-check e build, preview do site de docs e validação de exemplos, diagramas e frontmatter.

Revise o diff procurando: alteração fora do escopo autorizado, segredo ou dado privado, comando inventado ou incorreto, afirmação sem evidência, conteúdo ambíguo ou desatualizado, TODO desnecessário e perda de conteúdo existente.

Registre cada verificação como `pass`, `fail` ou `skipped`, com o motivo quando não executada.

## Registro de evidências

Relacione cada afirmação relevante à sua fonte:

```text
claim: afirmação documentada
source: arquivo, símbolo, linha, comando, workflow ou versão
kind: code | test | config | ci | existing-doc | human-validation | inference
confidence: high | medium | low
verified: true | false
```

`kind` indica a origem: implementação (`code`), testes (`test`), manifests e configuração (`config`), pipelines (`ci`), documentação existente (`existing-doc`), confirmação do responsável (`human-validation`) ou conclusão inferida (`inference`). O objetivo geral só é `human-validation` depois da confirmação; até lá, fica pendente.

## Critérios de bloqueio

Não dê a documentação por concluída quando:

- não for possível determinar como instalar ou executar o projeto;
- houver conflito relevante entre implementação, testes e configuração;
- comandos críticos não puderem ser verificados;
- houver segredo ou dado privado que impeça documentar com segurança;
- a tarefa exigir alteração de código ou infraestrutura não autorizada;
- o objetivo geral depender de decisão humana ainda não fornecida.

Nesses casos, entregue um rascunho parcial com `status: blocked` ou `planned`, listando lacunas, riscos e ações necessárias. Não invente informação para contornar o bloqueio.

## Formato de saída

Retorne JSON com esta estrutura (ou os mesmos campos em Markdown, se o ambiente não permitir JSON), adaptando os valores ao resultado real:

```json
{
  "status": "planned|changed|blocked",
  "skill": "source-grounded-documentation",
  "scope": {"repository": "...", "commit": "...", "paths": ["README.md", "docs/"]},
  "project_inventory": {
    "stack": [], "requirements": [], "install_commands": [],
    "env_files": [], "external_services": []
  },
  "changed_files": [],
  "evidence": [],
  "human_validation": ["Objetivo geral precisa ser validado pelo responsável."],
  "checks": [{"command": "...", "result": "pass|fail|skipped", "reason": "..."}],
  "unproven_or_stale": [],
  "risks": [],
  "next_steps": []
}
```

Não invente evidência, verificação nem arquivo alterado.
