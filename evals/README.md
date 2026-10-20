# Evals das skills

Esta pasta guarda os testes das skills do Grupo 1 (Produto e Arquitetura). A regra do hackathon é que
uma skill só está pronta quando se mostra que o agente a usa e que o resultado atende ao esperado.
Aqui ficam os cenários, os arquivos de apoio e os resultados.

Última atualização: 19/10/2026.

## Dois tipos de teste

| Tipo | Pergunta que responde | Arquivo | Como roda |
|---|---|---|---|
| **Qualidade da saída** | A skill, quando usada, produz o resultado certo? | `manual/<skill>/evals.json` | Na mão ou com o skill-creator |
| **Ativação** | O Claude escolhe a skill quando deveria (e não quando não deveria)? | `manual/<skill>/triggers.json` | `run_activation.py` |

Uma skill pode produzir saída excelente e nunca ser chamada, ou ser chamada sempre e produzir saída
ruim. Por isso os dois testes existem separados.

## O que existe

```
evals/
├── README.md                    # este índice
├── manual/                      # NOSSOS EVALS, feitos à mão e fora do plugin do Claude (uma pasta por skill)
│   └── <skill>/
│       ├── evals.json           # cenários de qualidade (3 por skill)
│       ├── triggers.json        # frases de ativação (6 positivas + 6 negativas), só nas 4 do arquiteto
│       ├── files/               # arquivos de apoio dos cenários (PRDs de exemplo, mini-crm, ADRs)
│       └── results/             # activation-*.json e iteration-N/, versionados
├── scripts/
│   ├── run_activation.py        # teste de ativação (nosso)
│   ├── summary.py               # resumo único dos resultados (lê results/, atualiza este README)
│   └── compare_tools.py         # compara o nosso teste de ativação com o claude plugin eval
├── plugin-eval/                 # DO CLAUDE: casos no formato do `claude plugin eval` (26 de ativação) e results/
└── comparacao/                  # comparação entre as duas ferramentas: método e resultados
```

**`manual/` é nosso, `plugin-eval/` é do Claude.** Em `manual/` o formato, os scripts e os resultados são nossos e não
dependem de nenhuma ferramenta do Claude Code (só do `claude -p` para o teste de ativação). Em `plugin-eval/` o formato é o
que o `claude plugin eval` exige, e ele grava os próprios resultados lá. As duas pastas não se leem entre si; só o
`scripts/compare_tools.py` compara o que cada uma produziu.

Na raiz do repo, a pasta `.claude-plugin/` existe só para o `claude plugin eval` carregar o repo como plugin. O
`plugin.json` dela aponta para as skills e os agentes em `.claude/` (sem links) e para os casos em `evals/plugin-eval/`.
Ao criar um agente novo, acrescente o arquivo dele em `agents` no `plugin.json`, porque o manifesto não aceita pasta.

| Skill | Cenários de qualidade | Frases de ativação |
|---|---|---|
| `product-discovery` | 3 | não |
| `prd-writing` | 3 | não |
| `technical-planning` | 3 | não |
| `product-design` | 3 | não |
| `repo-orientation` | 3 | 12 |
| `architecture-patterns` | 4 (inclui o design técnico) | 12 |
| `adr-writer` | 3 | 12 |
| `api-design` | 3 | 12 |

### Como é um cenário (`evals.json`)

Cada cenário tem `name`, `type`, `prompt`, `expected_output`, `files` e `assertions`:

- **`type: positivo`**: a skill deve funcionar. Ex.: `adr-writer` registra uma decisão fechada.
- **`type: negativo`**: a skill **não** deve ser usada. Ex.: pedir para renomear uma variável não gera ADR.
- **`type: limite`**: o caso difícil. Ex.: o usuário não deu números, e a skill escreve `A definir` em vez de inventar.
- **`assertions`**: afirmações que passam ou falham, como "não inventa números" ou "o ADR-0002 só muda o status".

## Como rodar

### 1. Qualidade, na mão (sem custo extra)

1. Abra uma sessão nova do Claude Code na raiz do repo.
2. Cole o `prompt` de um cenário. Se tiver `files`, o prompt já cita o caminho (`evals/manual/<skill>/files/...`).
3. Leia a resposta e marque cada asserção como passou ou falhou, com uma linha de evidência.
4. Para ver o valor da skill, repita o mesmo prompt **sem a skill** (numa pasta sem `.claude/`) e compare.

O cenário `limite-substitui-adr-existente` do `adr-writer` altera ADRs. Rode numa cópia de
`evals/manual/adr-writer/files/docs`, não no original.

### 2. Qualidade, com o skill-creator (compara com e sem a skill)

Peça numa sessão: "use o skill-creator para rodar `evals/manual/<skill>/evals.json`". Ele roda cada cenário
com e sem a skill, gera `grading.json`, `benchmark.md` e um `review.html`.
Salve tudo em `evals/manual/<skill>/results/iteration-N/` (regra do `AGENTS.md`).

### 3. Ativação

No seu terminal (onde `claude -p "oi"` funciona), na raiz do repo:

```bash
evals/scripts/run_activation.py adr-writer               # uma skill (recomendado)
evals/scripts/run_activation.py --selftest               # confere o detector, sem chamar o claude
```

Como funciona: para cada frase, roda `claude -p "<frase>"` **na raiz do repo**, onde as skills reais
existem, e olha as primeiras ferramentas chamadas. Se `Skill:<skill>` aparece entre as 3 primeiras
(`--within 3`), conta como ativação. Repete 2 vezes (`--runs`) e usa o corte de 50%. Para cada frase
imprime as ferramentas que o Claude usou (ex.: `Skill:adr-writer`, `Glob`, `Agent:solutions-architect`),
o que ajuda a entender **por que** falhou.

Cuidados:
- **Consome a cota da sua conta.** São 24 chamadas por skill. Rode uma skill por vez.
- Escrita e shell ficam bloqueados dentro do `claude -p`, e o processo é morto assim que o critério é decidido.
- Se aparecer `INVÁLIDO` ou `ATENÇÃO`, houve erro de execução (por exemplo limite de uso). Esse resultado
  **não vale**: espere o reset e rode de novo.
- Resultados vão para `evals/manual/<skill>/results/activation-<data-hora>.json` e nunca sobrescrevem.

## Agregando resultados

Seguimos a seção "Aggregating results" de https://agentskills.io/skill-creation/evaluating-skills. Depois de corrigir todas as execuções de uma
iteração, calcula-se por configuração a média e o desvio padrão de aprovação, tempo e tokens, e o **delta**
(com skill menos sem skill). O delta mostra o que a skill custa (tempo, tokens) e o que ela compra
(aprovação). Uma skill que dobra os tokens para ganhar 2 pontos provavelmente não compensa.

### Passo a passo, por iteração

1. Rode os cenários com e sem a skill, **cada execução em contexto limpo** (subagente novo).
2. **Grave o `timing.json` assim que cada subagente terminar.** `total_tokens` e `duration_ms` só chegam na
   notificação de término e não ficam guardados em lugar nenhum. Sem isso, o delta de tempo e de tokens sai zerado.
3. Corrija cada execução e grave o `grading.json` com evidência para cada asserção.
4. Gere o `benchmark.json` e o `benchmark.md` na raiz da iteração, a partir da pasta do skill-creator:
   ```bash
   python -m scripts.aggregate_benchmark evals/manual/<skill>/results/iteration-N --skill-name <skill>
   ```
5. Atualize o resumo abaixo: `evals/scripts/summary.py --write`.

### Formato dos arquivos (cuidado: difere da página)

A página mostra exemplos que o `aggregate_benchmark.py` do skill-creator **não lê**. Use o formato do script:

| Arquivo | Na página | O que o script lê (use este) |
|---|---|---|
| `grading.json` | `assertion_results` | **`expectations`**, cada item com `text`, `passed`, `evidence`, e `summary.pass_rate` |
| `timing.json` | `duration_ms` | **`total_duration_seconds`** e `total_tokens` |

Com o formato da página, a lista de asserções vem vazia e o tempo vira `0.0` sem nenhum aviso.

### Como ler os números

- **1 execução por cenário (o caso de hoje):** olhe a contagem bruta e o delta. O desvio padrão é 0 e não quer dizer
  nada. Para ter desvio útil, rode 2 ou mais execuções (`run-1/`, `run-2/`), começando pelos cenários `limite`, onde o
  modelo mais varia.
- **Asserção que passa nos dois lados** não mede a skill: o modelo faz sozinho e ela só infla o número. Troque por
  uma mais difícil ou tire. Os cenários `negativo` costumam cair aqui.
- **Asserção que falha nos dois lados:** a asserção, o cenário ou a skill está quebrado. Conserte antes da próxima iteração.
- **Asserção que passa com a skill e falha sem:** é onde a skill vale. Entenda qual instrução fez a diferença.
- **Aprovação oscilando entre execuções** (desvio alto): o cenário é instável ou a instrução da skill é ambígua.
- **Cenário muito mais lento que os outros:** leia a transcrição para achar o gargalo.

O `summary.py` já separa as asserções nessas faixas. Ele só lê `benchmark.json` e `activation-*.json`
(não roda eval, não chama o claude) e usa a iteração mais alta de cada skill.

### Resumo (gerado por `evals/scripts/summary.py --write`, não edite à mão)

<!-- RESUMO:INICIO -->
### Qualidade da saída (com a skill vs. sem a skill)

| Skill | Iteração | Execuções por cenário | Com skill | Sem skill | Δ aprovação | Δ tempo (s) | Δ tokens |
|---|---|---|---|---|---|---|---|
| `adr-writer` | — | — | sem iteração versionada | — | — | — | — |
| `api-design` | — | — | sem iteração versionada | — | — | — | — |
| `architecture-patterns` | 1 | 1 | 19/19 (100%) | 10/19 (53%) | +0.40 | +10.7 | +5964 |
| `prd-writing` | — | — | sem iteração versionada | — | — | — | — |
| `product-design` | — | — | sem iteração versionada | — | — | — | — |
| `product-discovery` | — | — | sem iteração versionada | — | — | — | — |
| `repo-orientation` | — | — | sem iteração versionada | — | — | — | — |
| `technical-planning` | — | — | sem iteração versionada | — | — | — | — |

Com 1 execução por cenário o desvio padrão não significa nada, então só mostramos contagem e delta.

### Quais asserções discriminam

- `architecture-patterns`: 9 discriminam (passam com a skill e falham sem), 10 passam nos dois (candidatas a sair), 0 falham nos dois (asserção ou cenário quebrado)
  - revisar: Registra explicitamente o que falta (prazo, time, carga) como pergunta em aberto
  - revisar: Recomenda a opção mais simples (monolito modular) e justifica sem exigir os dados que faltam
  - revisar: Informa gatilho de revisão ligado a condições concretas (ex.: times independentes, escala independente)
  - revisar: Corrige o tratamento de amount/quantity nulos (validação ou default)
  - revisar: Não produz análise de arquitetura (sem tabela de opções de padrões, sem 'Decisão:' com forças e restrições)
  - revisar: Resposta curta e focada no código
  - revisar: Apresenta de 2 a 4 opções reais, incluindo a mais simples (monolito/isolamento por coluna)
  - revisar: Recomenda uma única opção e liga a justificativa a requisitos (prazo de 5 dias, time de 3, isolamento por organização)
  - revisar: Lista perguntas em aberto ou premissas, sem inventar números (carga, custo, latência)
  - revisar: Cobre o isolamento entre organizações (ex.: filtro por org_id/RLS) como decisão explícita

### Ativação (a skill é chamada quando deveria)

| Skill | Acertos | Observação |
|---|---|---|
| `adr-writer` | 11/12 (92%) | activation-2026-10-20-1005.json |
| `api-design` | 10/12 (83%) | activation-2026-10-20-1006.json |
| `architecture-patterns` | 9/12 (75%) | activation-2026-10-20-1004.json |
| `prd-writing` | — | sem resultado |
| `product-design` | — | sem resultado |
| `product-discovery` | — | sem resultado |
| `repo-orientation` | 8/12 (67%) | activation-2026-10-20-1007.json |
| `technical-planning` | — | sem resultado |
<!-- RESUMO:FIM -->

## Resultados até agora (anteriores ao summary.py)

Estes números foram anotados à mão em 19/10, antes de existir `benchmark.json`. Os arquivos não estão no repo, então
não entram no resumo acima. Quando houver uma iteração versionada, ela substitui esta seção.

### Qualidade da saída (19/10, com a skill vs. sem a skill)

Rodamos `adr-writer` e `architecture-patterns`, 1 execução por cenário.

| Skill | Com skill | Sem skill |
|---|---|---|
| `adr-writer` | 12/12 | 8/12 |
| `architecture-patterns` | 13/13 | 11/13 |

- A skill garante formato e disciplina: seções completas do ADR, índice `README.md`, só o status do ADR antigo muda, não inventa números.
- Nos cenários negativos os dois lados acertam. O modelo sozinho já sabe não fazer ADR para renomear variável.
- **Os arquivos desses resultados ainda não estão em `results/`**: foram gerados fora do repo. Falta copiá-los ou rodar de novo.
- As outras 6 skills têm cenários escritos, mas **nunca foram rodadas**.

### Ativação (19/10)

| Skill | Resultado válido |
|---|---|
| `adr-writer` | 10/12 e 11/12 (duas rodadas). Todas as negativas corretas. A falha: "atualiza o ADR-0002", em que o Claude lista os arquivos antes de chamar a skill. |
| `architecture-patterns` | Só 3 frases válidas (o limite de uso da conta bateu): "monolito ou microsserviços" 0/3 (o Claude respondeu direto, sem ferramenta), "organizar módulos" 2/3, "isolar dados por tenant" 0/3. |
| `api-design`, `repo-orientation` | Sem resultado válido ainda. |

Leitura: o detector funciona. Para perguntas que o Claude responde de cabeça, ele tende a ignorar a skill.
Isso ainda precisa de mais dados antes de mexer nas descrições.

## Lições aprendidas (para não repetir)

- **O teste de ativação do skill-creator (`run_eval.py`) não funcionou aqui.** Ele cria um "clone" da
  skill como comando e checa se o Claude o chama. Deu 8% de ativação nas positivas e 0/4 até numa frase
  que citava a skill pelo nome. Foi descartado, e `run_activation.py` testa a skill real.
- **Plugins do usuário rodam dentro do `claude -p`.** Suspeitamos do plugin ponytail e o desligamos,
  mas o resultado não mudou. Não era a causa.
- **Erro de execução não é "não acionou".** Uma versão anterior do script contava erro de limite de uso
  como falha e mostrava números falsos. Hoje o script marca como `INVÁLIDO`.
- **Teste de ativação só mede a primeira(s) ferramenta(s).** Se o Claude explora o repo antes de chamar
  a skill, `--within 1` conta como falha. Por isso o padrão é 3.

## Pendências

- Rodar a ativação de `architecture-patterns`, `api-design` e `repo-orientation` (uma por vez).
- Rodar os cenários de qualidade das 6 skills que faltam, e versionar os resultados em `results/`.
- Criar `triggers.json` das skills de Produto (`product-discovery`, `prd-writing`, `technical-planning`, `product-design`).
- Depois de ter dados confiáveis, otimizar as descrições (o skill-creator tem o `run_loop.py`, mas ele depende do teste de ativação do clone, que não funcionou aqui).
- Alinhar com os Grupos 2 e 3 o formato dos evals e a pasta `results/` (versionar ou ignorar os `outputs/`).
- O `claude plugin eval` (comando do Claude Code) roda casos de teste de um plugin e compara com um cenário sem o plugin. Lê `case.yaml` ou `prompt.md` mais `graders/`, formato diferente do nosso. Não avaliamos se vale migrar.

## Limites

- Poucas execuções por cenário (1 na qualidade, 2 na ativação): os números têm ruído.
- As asserções de qualidade foram corrigidas por uma pessoa lendo as respostas, sem um avaliador independente.
- Subagentes recebem o caminho da skill, então o teste de qualidade mede a saída e não a ativação.
