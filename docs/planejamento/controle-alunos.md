# Planejamento: Controle de alunos com relatório diário

## Visão geral
3 épicos e 9 histórias. O MVP são as 7 histórias Essenciais (HU-01 a HU-07). HU-08 e HU-09 são Importantes e vêm depois.

Origem: `docs/prd/controle-alunos.md`.

## Critérios transversais
- **RNF-01:** o responsável só acessa dados do próprio filho. Vale para HU-06, HU-07 e HU-08.
- **RNF-02:** tratamento de dados de menores. Limite: A definir. Vale para HU-02, HU-04, HU-05 e HU-07.
- **RNF-03:** registro rápido de um relatório. Limite: A definir. Vale para HU-04.

## Épico 1: Alunos e seções
O instrutor tem seus alunos organizados por seção de aula, com o responsável de cada um vinculado.

### HU-01: Criar seção de aula
- **Origem:** RF-01
- **Prioridade:** Essencial
- **História:** Como instrutor, quero criar uma seção de aula, para organizar meus alunos por turma.
- **Critérios de aceite:**
  1. Dado que informei o nome da seção, quando salvo, então a seção aparece na minha lista.
  2. Dado que o nome está vazio, quando tento salvar, então vejo aviso e a seção não é criada.
- **Depende de:** nenhuma

### HU-02: Cadastrar aluno em uma seção
- **Origem:** RF-01
- **Prioridade:** Essencial
- **História:** Como instrutor, quero cadastrar um aluno em uma seção, para ter o controle de quem participa de cada aula.
- **Critérios de aceite:**
  1. Dado uma seção existente, quando cadastro um aluno com nome, então ele aparece na lista dessa seção.
  2. Dado que o nome está vazio, quando tento salvar, então vejo aviso e o aluno não é cadastrado.
- **Depende de:** HU-01

### HU-03: Vincular responsável ao aluno
- **Origem:** RF-01
- **Prioridade:** Essencial
- **História:** Como instrutor, quero vincular o responsável a um aluno, para que ele possa acompanhar o filho.
- **Critérios de aceite:**
  1. Dado um aluno cadastrado, quando vinculo um responsável, então o vínculo aparece no cadastro do aluno.
  2. Dado que faltam os dados do responsável, quando tento vincular, então vejo aviso e o vínculo não é criado. Quais dados: A definir.
- **Depende de:** HU-02

## Épico 2: Relatório diário
O instrutor registra o que aconteceu em cada aula e consulta o histórico de cada aluno.

### HU-04: Registrar relatório de um aluno
- **Origem:** RF-02
- **Prioridade:** Essencial
- **História:** Como instrutor, quero registrar presença, comportamento e ocorrências, e pontos positivos de um aluno em uma data, para ter um registro do que aconteceu na aula.
- **Critérios de aceite:**
  1. Dado uma seção com alunos, quando escolho a seção e a data, então vejo os alunos daquela seção.
  2. Dado um aluno e uma data, quando preencho presença, comportamento e ocorrências, e pontos positivos e salvo, então vejo o relatório salvo com a data.
  3. Dado que falta um campo obrigatório, quando tento salvar, então vejo aviso indicando o que falta. Quais são obrigatórios: A definir.
  4. Dado que já existe relatório do aluno na mesma data, quando tento registrar outro, então o comportamento é A definir.
- **Depende de:** HU-02

### HU-05: Consultar histórico de um aluno
- **Origem:** RF-03
- **Prioridade:** Essencial
- **História:** Como instrutor, quero ver os relatórios anteriores de um aluno, para mostrar o que aconteceu quando conversar com o responsável.
- **Critérios de aceite:**
  1. Dado um aluno com relatórios, quando abro o histórico, então vejo os relatórios em ordem de data, do mais recente ao mais antigo.
  2. Dado um aluno sem relatórios, quando abro o histórico, então vejo uma mensagem informando que ainda não há relatórios.
- **Depende de:** HU-04

## Épico 3: Acompanhamento pelos responsáveis
O responsável acompanha o filho e conversa com o instrutor dentro do relatório.

### HU-06: Acessar o app com conta
- **Origem:** RF-04
- **Prioridade:** Essencial
- **História:** Como responsável, quero entrar no app com minha conta, para acompanhar meu filho de forma privada.
- **Critérios de aceite:**
  1. Dado que tenho conta, quando informo meus dados corretos, então entro e vejo a área do meu filho.
  2. Dado que informo dados incorretos, quando tento entrar, então vejo mensagem de erro e não entro.
  3. Como a conta é criada: A definir.
- **Depende de:** HU-03

### HU-07: Ver os relatórios do filho
- **Origem:** RF-04
- **Prioridade:** Essencial
- **História:** Como responsável, quero ver os relatórios do meu filho, para saber como foram as aulas.
- **Critérios de aceite:**
  1. Dado que entrei, quando abro a área do meu filho, então vejo os relatórios dele, do mais recente ao mais antigo.
  2. Dado um filho sem relatórios, quando abro a área dele, então vejo uma mensagem informando que ainda não há relatórios.
  3. Dado que tento abrir um relatório de outro aluno, quando faço isso, então não tenho acesso ao conteúdo (ver RNF-01).
- **Depende de:** HU-04, HU-06

### HU-08: Comentar em um relatório
- **Origem:** RF-05
- **Prioridade:** Importante
- **História:** Como responsável, quero comentar em um relatório do meu filho, para responder ao instrutor sobre o que aconteceu.
- **Critérios de aceite:**
  1. Dado um relatório do meu filho, quando escrevo um comentário e envio, então o comentário aparece no relatório.
  2. Dado que o comentário está vazio, quando tento enviar, então vejo aviso e nada é enviado.
- **Depende de:** HU-07

### HU-09: Ver o comentário do responsável
- **Origem:** RF-05
- **Prioridade:** Importante
- **História:** Como instrutor, quero ver os comentários dos responsáveis nos relatórios, para saber como eles reagiram.
- **Critérios de aceite:**
  1. Dado um relatório com comentário, quando abro o relatório, então vejo o comentário do responsável.
  2. Dado um relatório sem comentário, quando o abro, então não vejo nenhum comentário.
- **Depende de:** HU-08

## Ordem sugerida de entrega
1. HU-01, HU-02 (MVP, base para o instrutor)
2. HU-04, HU-05 (MVP, o instrutor já registra e consulta)
3. HU-03, HU-06, HU-07 (MVP, os responsáveis passam a acompanhar)
4. HU-08, HU-09 (depois do MVP)

As etapas 1 e 2 entregam valor só para o instrutor. Isso permite testar a H-02 (o instrutor mantém o hábito diário) antes de envolver os responsáveis.

## Cobertura
| Requisito | Histórias |
| -- | -- |
| RF-01 | HU-01, HU-02, HU-03 |
| RF-02 | HU-04 |
| RF-03 | HU-05 |
| RF-04 | HU-06, HU-07 |
| RF-05 | HU-08, HU-09 |

Requisitos sem história: nenhum. Histórias sem origem: nenhuma.

## Pendências
- Como o instrutor entra no app? O PRD fala de conta só para o responsável.
- Como o responsável recebe a conta (convite, cadastro) e que dado o identifica? Afeta HU-03 e HU-06.
- Um responsável pode ter mais de um filho, e um aluno mais de um responsável?
- Quais campos do relatório são obrigatórios, e se comportamento e ocorrências são texto livre ou campos fixos (HU-04).
- O que acontece com dois relatórios do mesmo aluno na mesma data (HU-04).
- Editar ou apagar relatório e aviso de relatório novo ao responsável: sem história, porque o PRD deixou em aberto.
- Limites de RNF-02 e RNF-03: A definir.
- A ordem do histórico para o instrutor (HU-05) seguiu a do responsável. Confirmar.
