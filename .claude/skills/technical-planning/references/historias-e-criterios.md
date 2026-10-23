# Histórias e critérios de aceite

Material de consulta para quebrar requisitos em histórias e escrever critérios verificáveis. O modelo a preencher está em `assets/planejamento.md`.

## Épicos

Um épico agrupa histórias que entregam **um objetivo de usuário**, nomeado em linguagem de negócio.

| Bom | Ruim |
|---|---|
| "Cadastro e acesso" | "Backend de usuários" |
| "Ingestão de documentos" | "Sprint 1" |
| "Acompanhamento do pedido" | "Banco de dados" |

Épico organizado por camada técnica atrasa a primeira entrega de valor.

## Quando quebrar uma história

Quebre quando ela:

- não cabe em poucos dias de trabalho;
- tem mais de um comportamento principal;
- mistura usuários diferentes;
- tem critérios que se dividem em grupos independentes.

### Padrões de quebra

| Padrão | Exemplo |
|---|---|
| Por passo do fluxo | Cadastrar, depois confirmar e-mail, depois recuperar senha |
| Por tipo de usuário | Visão do atendente, depois visão do gestor |
| Caminho feliz primeiro | Caso comum, depois erros e exceções |
| Por regra de negócio | Cada regra como uma história |
| Por dado ou formato | Importar CSV, depois outros formatos |

Prefira **fatias verticais** (da interface ao dado, entregando algo que o usuário vê) a fatias por camada.

## Escrever a história

> Como **[usuário]**, quero **[ação]**, para **[benefício]**.

- O benefício não repete a ação. "Quero filtrar, para filtrar" não é benefício.
- Sem benefício claro, questione se a história é necessária.
- O usuário é um papel real do PRD, e não "o sistema".
- Tarefa técnica pura (migração, infra) vai na lista de tarefas da história ou do épico, sem virar história de usuário.

## INVEST: checagem rápida

| Letra | Pergunta |
|---|---|
| **I**ndependente | Pode ser entregue sem esperar outra? Se não, declare a dependência |
| **N**egociável | Descreve o resultado, sem travar a forma? |
| **V**aliosa | Alguém percebe o valor? |
| **E**stimável | O time entende o suficiente para estimar? |
| **S**mall (pequena) | Cabe numa entrega curta? |
| **T**estável | Dá para dizer sem discutir se está pronta? |

## Critérios de aceite (Dado, Quando, Então)

```
Dado [contexto ou estado inicial],
quando [ação do usuário ou evento],
então [resultado observável].
```

Regras:

- Um comportamento por critério.
- O resultado é observável: mensagem, estado, dado salvo, tela.
- Sem adjetivo vago. Troque "rápido", "fácil", "amigável" por número, texto ou estado.
- Números e mensagens vêm do PRD ou do usuário. Se não existem, escreva `A definir` e liste em "Pendências".

### O que cobrir

| Categoria | Pergunta |
|---|---|
| Caminho feliz | O fluxo normal funciona? |
| Validação | O que acontece com dado inválido ou faltando? |
| Permissão | Quem não pode fazer isso e o que vê? |
| Estado vazio | E se não houver nada ainda? |
| Falha | E se um serviço externo falhar ou a conexão cair? |
| Borda | Limite máximo, duplicidade, repetição da ação |

Nem toda história precisa de todas as categorias. Inclua as relevantes, porque são as que costumam ser esquecidas.

### Exemplo ilustrativo (não é dado do projeto)

```markdown
### HU-03: Recuperar senha
- **Origem:** RF-04
- **Prioridade:** Importante
- **História:** Como usuário cadastrado, quero redefinir minha senha, para voltar a acessar a conta sem pedir ajuda.
- **Critérios de aceite:**
  1. Dado um e-mail cadastrado, quando solicito a redefinição, então recebo uma mensagem com o link.
  2. Dado um e-mail não cadastrado, quando solicito a redefinição, então vejo a mesma mensagem de confirmação (para não revelar quem tem conta).
  3. Dado um link expirado, quando tento usá-lo, então vejo aviso de expiração e posso pedir outro.
  4. Prazo de validade do link: A definir.
- **Depende de:** HU-01
```

## Critérios transversais

Um RNF que vale para o sistema todo (segurança, LGPD, desempenho, acessibilidade) fica em "Critérios transversais" e é referenciado nas histórias afetadas ("ver RNF-02"). Um RNF que vale para uma história só vira critério dela.

## Dependências e ordem

- Registre **o que bloqueia o quê**. Dependência externa (outra equipe, outro sistema) ganha destaque.
- Ordem: Essencial primeiro (MVP), respeitando as dependências.
- Dependência circular indica história mal quebrada.

## Cobertura e rastreabilidade

Cadeia: `RF-xx` → `HU-xx` → componente do design → ADR.

Antes de entregar, confira:

- [ ] Todo RF do PRD aparece em pelo menos uma história
- [ ] Toda história cita o RF de origem
- [ ] Prioridade herdada do requisito, sem promover nem rebaixar sem avisar
- [ ] Critérios verificáveis, sem adjetivo vago
- [ ] Nenhuma estimativa inventada
- [ ] Lacunas listadas em "Pendências"

## Estimativas

Só dê pontos ou prazos se o usuário pedir, e diga que são palpites. O planejamento não deve conter estimativa por padrão.
