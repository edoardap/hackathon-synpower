# PRD: Controle de alunos com relatório diário

| Campo | Valor |
| -- | -- |
| Responsável | Instrutor (nome: A definir) |
| Status | Rascunho |
| Data | 2026-10-23 |

## 1. Visão geral
App para um instrutor acompanhar seus alunos e registrar um relatório diário de cada um. Os responsáveis acessam esse relatório com uma conta própria e podem comentar. A descoberta (`docs/discovery/controle-alunos.md`) recomendou **Testar mais**, então este PRD parte de hipóteses ainda não validadas (ver Premissas e Riscos).

## 2. Problema e oportunidade
Um aluno desrespeitou o instrutor diante da turma. O instrutor esqueceu de avisar os responsáveis e, ao avisar depois, sem registro do ocorrido, eles ficaram contra ele. Hoje o instrutor não registra o acompanhamento dos alunos. A oportunidade é ter um registro datado de cada aula e uma forma de os responsáveis acompanharem os filhos. Frequência do problema: 1 caso relatado.

## 3. Objetivos e não objetivos
**Objetivos**
- O instrutor passa a registrar o que acontece em cada aula, por aluno.
- Os responsáveis conseguem acompanhar o relatório do próprio filho e comentar.

**Não objetivos:** A definir. O usuário ainda não confirmou o que fica de fora.

## 4. Usuários
- **Instrutor:** dá aulas de esporte, música ou atividade similar, com 5 alunos por seção. Registra os relatórios.
- **Responsável:** pai, mãe ou responsável de um aluno. Hoje se comunica com o instrutor por WhatsApp. Lê o relatório e comenta.
- **Aluno:** menor de idade, é o assunto do relatório e não usa o app.

## 5. Métricas de sucesso
| Métrica | Valor atual | Meta | Como medir |
| -- | -- | -- | -- |
| Aulas com relatório registrado | Nenhum registro hoje | A definir (sugestão da descoberta: 80% ou mais, não confirmada) | Relatórios registrados sobre as aulas dadas |
| Relatórios lidos pelos responsáveis | Não existe hoje | A definir | Relatórios abertos sobre os enviados |
| Relatórios com comentário do responsável | Não existe hoje | A definir | Comentários recebidos |

## 6. Escopo
- **Dentro (MVP):** cadastro de alunos e responsáveis, relatório diário por aluno, histórico, acesso do responsável por conta, comentário do responsável.
- **Fora:** A definir.

## 7. Fluxos do usuário
**Instrutor registra a aula**
1. Escolhe a seção e a data da aula.
2. Para cada aluno, registra presença, comportamento e ocorrências, e pontos positivos e evolução.
3. Salva e o relatório fica no histórico do aluno.

**Responsável acompanha**
1. Entra com a própria conta.
2. Vê os relatórios do filho, do mais recente ao mais antigo.
3. Comenta em um relatório, se quiser.

**Instrutor lê o comentário**
1. Abre o relatório e vê o comentário do responsável.

## 8. Requisitos funcionais
| ID | Requisito | Prioridade | Critério de aceite | Origem |
| -- | -- | -- | -- | -- |
| RF-01 | O instrutor cadastra alunos, associa cada um a uma seção de aula e vincula o responsável | Essencial | O instrutor cadastra um aluno e o vê na lista da sua seção, com o responsável vinculado | Pedido inicial ("controle sobre meus alunos") |
| RF-02 | O instrutor registra o relatório diário de um aluno com presença, comportamento e ocorrências, e pontos positivos e evolução | Essencial | O instrutor escolhe aluno e data, preenche os três itens e vê o relatório salvo com a data | Problema (falta de registro) |
| RF-03 | O instrutor consulta o histórico de relatórios de um aluno | Essencial | O instrutor abre um aluno e vê seus relatórios em ordem de data | Problema (precisou mostrar o que aconteceu) |
| RF-04 | O responsável acessa o app com conta e vê só os relatórios do próprio filho | Essencial | O responsável entra e vê os relatórios do filho. Não vê os de outros alunos | Pedido ("pais devem ter acesso") |
| RF-05 | O responsável comenta em um relatório e o instrutor vê o comentário | Importante | O responsável envia um comentário e o instrutor o vê no mesmo relatório | Pedido (interação: ler e comentar) |

## 9. Requisitos não funcionais
| ID | Requisito | Limite ou meta |
| -- | -- | -- |
| RNF-01 | Acesso restrito: o responsável só vê dados do próprio filho | Nenhum acesso a dados de outro aluno, verificável por teste |
| RNF-02 | Tratamento de dados de menores de idade | A definir (requisitos legais ainda não levantados) |
| RNF-03 | Registro rápido de um relatório, para sustentar o hábito diário | A definir (tempo máximo por aluno) |

## 10. Dependências e restrições
- O WhatsApp é o canal de comunicação atual com os responsáveis (fato informado).
- 5 alunos por seção de aula. Número de seções: A definir.
- Os relatórios envolvem dados de menores de idade.

## 11. Riscos e mitigação
| Risco | Impacto | Mitigação |
| -- | -- | -- |
| O instrutor não mantém o registro diário (H-02) | Alto: o app perde o valor | Piloto manual antes de construir |
| Os responsáveis não leem ou reagem mal ao relatório (H-03) | Alto: não resolve o problema original | Piloto manual com os pais de uma seção |
| Dados sensíveis de menores expostos ou mal tratados | A definir | A definir, encaminhar ao arquiteto |

## 12. Marcos
A definir. A descoberta sugere um piloto manual de 2 semanas, sugestão não confirmada.

## 13. Partes interessadas
Instrutor (dono do produto), responsáveis dos alunos. Outras: A definir.

## 14. Premissas
- O instrutor registrará a aula todos os dias (H-02, não validada).
- Os responsáveis lerão o relatório e reagirão melhor do que a um aviso solto (H-03, não validada).
- O problema é comum a outros instrutores (H-01, não validada).

## 15. Perguntas em aberto
- O que fica fora do MVP (não objetivos)? *(bloqueia as seções 3 e 6)*
- O responsável recebe aviso quando sai um relatório novo? Por qual canal? *(bloqueia o fluxo do responsável)*
- O instrutor pode editar ou apagar um relatório depois de salvo, e isso fica registrado? *(afeta RF-02 e o valor como registro)*
- O comportamento e as ocorrências são texto livre ou campos fixos? *(afeta RF-02)*
- Quantas seções o instrutor tem? *(afeta o tamanho do uso)*
- Quais cuidados legais valem para dados de menores? *(RNF-02, para o arquiteto)*
- Metas das métricas, tempo máximo de registro (RNF-03) e limites do piloto.
