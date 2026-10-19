# Evals das skills

Esta pasta guarda os testes das skills do Grupo 1 (Produto e Arquitetura). A regra do hackathon é que
uma skill só está pronta quando se mostra que o agente a usa e que o resultado atende ao esperado.
Aqui ficam os cenários, os arquivos de apoio e os resultados.

Última atualização: 19/10/2026.

## Dois tipos de teste

| Tipo | Pergunta que responde | Arquivo | Como roda |
|---|---|---|---|
| **Qualidade da saída** | A skill, quando usada, produz o resultado certo? | `<skill>/evals.json` | Na mão ou com o skill-creator |
| **Ativação** | O Claude escolhe a skill quando deveria (e não quando não deveria)? | `<skill>/triggers.json` | `run_activation.py` |

Uma skill pode produzir saída excelente e nunca ser chamada, ou ser chamada sempre e produzir saída
ruim. Por isso os dois testes existem separados.

## O que existe

```
evals/
├── README.md
├── run_activation.py            # teste de ativação (script)
└── <skill>/
    ├── evals.json               # cenários de qualidade (3 por skill)
    ├── triggers.json            # frases de ativação (6 positivas + 6 negativas), só nas 4 do arquiteto
    ├── files/                   # arquivos de apoio dos cenários (PRDs de exemplo, mini-crm, ADRs)
    └── results/                 # resultados versionados
```

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
2. Cole o `prompt` de um cenário. Se tiver `files`, o prompt já cita o caminho (`evals/<skill>/files/...`).
3. Leia a resposta e marque cada asserção como passou ou falhou, com uma linha de evidência.
4. Para ver o valor da skill, repita o mesmo prompt **sem a skill** (numa pasta sem `.claude/`) e compare.

O cenário `limite-substitui-adr-existente` do `adr-writer` altera ADRs. Rode numa cópia de
`evals/adr-writer/files/docs`, não no original.

### 2. Qualidade, com o skill-creator (compara com e sem a skill)

Peça numa sessão: "use o skill-creator para rodar `evals/<skill>/evals.json`". Ele roda cada cenário
com e sem a skill, gera `grading.json`, `benchmark.md` e um `review.html`.
Salve tudo em `evals/<skill>/results/iteration-N/` (regra do `AGENTS.md`).

### 3. Ativação

No seu terminal (onde `claude -p "oi"` funciona), na raiz do repo:

```bash
evals/run_activation.py adr-writer               # uma skill (recomendado)
evals/run_activation.py --selftest               # confere o detector, sem chamar o claude
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
- Resultados vão para `evals/<skill>/results/activation-<data-hora>.json` e nunca sobrescrevem.

## Resultados até agora

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
