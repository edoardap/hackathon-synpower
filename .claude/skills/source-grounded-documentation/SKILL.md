---
name: source-grounded-documentation
description: Criar documentação inicial de um repositório com base em código, testes, configuração e CI verificáveis. Usar quando o README.md ou o diretório docs/ estiver ausente ou quando a documentação existente for insuficiente ou não confiável.
---

# Source-Grounded Documentation

## Objetivo

Criar uma base documental útil e verificável para um repositório, utilizando evidências reais e sem transformar suposições em fatos.

A entrega mínima consiste em um `README.md` na raiz e um diretório `docs/` com páginas que contenham informações sustentadas por evidências.

## Quando usar

Use esta Skill quando:

- O projeto não possuir documentação suficiente.
- O `README.md` estiver ausente ou não explicar como configurar e executar o projeto.
- O diretório `docs/` não existir ou não contiver documentação útil.
- A documentação existente não permitir compreender o objetivo, a configuração, os testes e os componentes relevantes do projeto.

Não use esta Skill para atualizar a documentação com base em um PR/MR específico. Nesse caso, utilize `impact-aware-documentation`.

## Entradas necessárias

Obtenha, quando disponíveis:

- Caminho do repositório e raiz Git.
- Público-alvo e objetivo da documentação.
- Branch e commit de referência.
- Caminhos autorizados para escrita.
- Comandos e verificações obrigatórios.
- Responsável humano pela validação do objetivo geral do projeto.

Se o público-alvo, o objetivo de negócio ou o escopo de escrita forem desconhecidos, continue a investigação técnica e registre as lacunas. Não apresente interpretações não confirmadas como fatos.

## Workflow

### 1. Identificar o contexto

1. Identifique a raiz Git, a branch, o commit e o estado do repositório.
2. Leia `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING.md` e as demais instruções aplicáveis, incluindo as do ambiente de execução.
3. Verifique se `README.md` e `docs/` existem e avalie a qualidade do conteúdo atual.
4. Preserve a documentação existente. Se ela já for substancial, prefira atualizações incrementais a uma reconstrução completa.

### 2. Inventariar o projeto

Investigue o repositório sem presumir tecnologias, nomes de arquivos ou ferramentas.

Considere as seguintes fontes:

- **Dependências e runtimes:** `package.json`, lockfiles, `pyproject.toml`, `requirements*.txt`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle` e equivalentes.
- **Automação:** `Makefile`, `Taskfile`, scripts de build e comandos de desenvolvimento.
- **Containers e infraestrutura:** `Dockerfile`, `.dockerignore`, `compose.yaml`, `docker-compose.yml`, manifests e configurações de infraestrutura.
- **Configuração:** `.env.example`, `.env.sample`, schemas e arquivos de configuração.
- **CI e release:** workflows, scripts de release e pipelines.
- **Implementação:** entry points, rotas, módulos principais, testes e exemplos.
- **Documentação:** README, arquivos em `docs/` e demais materiais mantidos pelo projeto.

Identifique e registre:

- Linguagens, runtimes e versões.
- Gerenciadores de pacotes.
- Dependências e ferramentas externas.
- Serviços auxiliares, portas e bancos de dados.
- Credenciais e configurações necessárias.
- Comandos de instalação, execução e validação.

Diferencie requisitos confirmados de requisitos inferidos.

### 3. Validar o processo de inicialização

Defina o caminho necessário para partir de um checkout limpo e chegar a uma aplicação funcional.

Investigue, nesta ordem lógica:

1. Pré-requisitos.
2. Instalação das dependências.
3. Preparação de serviços externos e containers.
4. Configuração das variáveis de ambiente.
5. Inicialização da aplicação.
6. Verificação do funcionamento.
7. Execução de testes, lint, type-check e build.

Priorize comandos já definidos em manifests, scripts, `Makefile`, `Taskfile` ou CI.

Execute os comandos em uma sequência segura, quando possível. Não instale dependências nem inicie serviços sem autorização e sem avaliar o impacto da execução.

Não declare comandos como verificados sem executá-los ou sem uma fonte autoritativa explícita que comprove seu comportamento.

### 4. Criar a estrutura documental

Garanta a existência de:

```text
README.md
docs/
```

Crie os diretórios e arquivos somente nos caminhos autorizados.

Utilize a estrutura existente quando ela for adequada. Caso seja necessário estabelecer uma estrutura inicial, considere:

- `docs/architecture.md`: componentes, dependências e fluxos.
- `docs/development.md`: configuração do ambiente e desenvolvimento local.
- `docs/testing.md`: estratégia e execução dos testes.
- `docs/configuration.md`: configuração e variáveis de ambiente.
- `docs/operations.md`: operação e troubleshooting.
- `docs/adr/`: decisões arquiteturais, quando aplicável.
- `docs/rfc/`: propostas de mudanças ou evoluções, quando aplicável.

Crie apenas documentos com conteúdo sustentado por evidências ou explicitamente solicitado. Não produza páginas vazias para preencher uma estrutura predefinida.

### 5. Escrever o README

Organize o README conforme as necessidades do projeto, preferencialmente nesta ordem:

1. Nome e descrição factual.
2. Objetivo e público-alvo.
3. Estado e escopo conhecidos, sem presumir maturidade ou estabilidade.
4. Pré-requisitos.
5. Guia de instalação e inicialização.
6. Variáveis de ambiente.
7. Execução e verificação do funcionamento.
8. Testes, lint, type-check e build.
9. Links para a documentação complementar.
10. Limitações, troubleshooting e próximos passos, quando sustentados por evidências.

O objetivo geral deve ser escrito ou validado pelo responsável humano. Quando não houver confirmação suficiente, marque o conteúdo como `A validar pelo responsável`.

Para cada variável de ambiente relevante, documente:

- Nome.
- Finalidade.
- Obrigatoriedade.
- Formato esperado.
- Exemplo seguro, quando possível.

Nunca copie valores reais de arquivos `.env`, configurações de CI ou sistemas de secrets.

### 6. Escrever a documentação complementar

Priorize os assuntos mais relevantes para compreender, desenvolver, testar e operar o projeto.

- Documente a arquitetura com base nos componentes e fluxos observados.
- Explique como configurar e executar o ambiente de desenvolvimento.
- Registre os comandos de teste e as verificações disponíveis.
- Descreva as configurações necessárias e suas finalidades.
- Documente procedimentos operacionais e troubleshooting somente quando houver evidências suficientes.

Sempre que útil, inclua referências a arquivos, módulos, comandos e outras páginas da documentação.

Identifique decisões que dependam de conhecimento humano e informações que ainda não puderam ser confirmadas.

### 7. Validar e revisar

Execute as verificações pertinentes ao stack e às ferramentas disponíveis:

- Sintaxe e lint de Markdown ou MDX.
- Validação de links e âncoras.
- Comandos de instalação e inicialização.
- Testes, lint, type-check e build.
- Renderização ou preview, quando houver um site de documentação.
- Validação de exemplos, snippets, diagramas e frontmatter.

Revise o diff para identificar:

- Alterações fora do escopo autorizado.
- Segredos ou dados privados.
- Comandos inventados ou incorretos.
- Afirmações sem evidências.
- Conteúdo desatualizado ou ambíguo.
- TODOs desnecessários.
- Perda acidental de conteúdo existente.

Registre o resultado de cada verificação como `pass`, `fail` ou `skipped`. Para verificações não executadas, informe o motivo.

## Registro de evidências

Mantenha um registro que relacione cada afirmação relevante da documentação à sua fonte.

Utilize, no mínimo, os seguintes campos:

```text
claim: afirmação documentada
source: arquivo, símbolo, linha, comando, workflow ou versão
kind: code | test | config | ci | existing-doc | human-validation | inference
confidence: high | medium | low
verified: true | false
```

A classificação deve refletir a origem da informação:

- `code`: implementação do projeto.
- `test`: testes automatizados ou verificações de comportamento.
- `config`: manifests e arquivos de configuração.
- `ci`: workflows e pipelines.
- `existing-doc`: documentação existente.
- `human-validation`: informação confirmada pelo responsável humano.
- `inference`: conclusão inferida a partir das evidências disponíveis.

A descrição do objetivo geral deve ser associada a `human-validation` quando houver confirmação do responsável. Enquanto isso não ocorrer, mantenha a afirmação identificada como pendente de validação.

## Critérios de bloqueio

Não considere a documentação concluída quando:

- Não for possível determinar como instalar ou executar o projeto.
- Existirem conflitos relevantes entre implementação, testes e configuração.
- Comandos críticos não puderem ser verificados.
- Forem encontrados segredos ou dados privados que impeçam uma documentação segura.
- A tarefa exigir alterações de código ou infraestrutura não autorizadas.
- O objetivo geral depender de uma decisão humana ainda não fornecida.

Quando possível, entregue um rascunho parcial com `status: blocked` ou `status: planned`, identificando as lacunas, os riscos e as ações necessárias para prosseguir.

Não invente informações para contornar um bloqueio.

## Formato de saída

Retorne os resultados em JSON, preferencialmente seguindo esta estrutura:

```json
{
  "status": "planned|changed|blocked",
  "skill": "source-grounded-documentation",
  "scope": {
    "repository": "...",
    "commit": "...",
    "paths": ["README.md", "docs/"]
  },
  "project_inventory": {
    "stack": [],
    "requirements": [],
    "install_commands": [],
    "env_files": [],
    "external_services": []
  },
  "changed_files": [],
  "evidence": [],
  "human_validation": [
    "Objetivo geral precisa ser validado pelo responsável."
  ],
  "checks": [
    {
      "command": "...",
      "result": "pass|fail|skipped",
      "reason": "..."
    }
  ],
  "unproven_or_stale": [],
  "risks": [],
  "next_steps": []
}
```

Adapte os valores ao resultado real da execução. Não invente evidências, verificações ou arquivos alterados.

Se o ambiente não permitir JSON, utilize os mesmos campos em Markdown.

Nunca marque um comando como validado sem executá-lo ou sem uma fonte autoritativa explícita que comprove seu comportamento.