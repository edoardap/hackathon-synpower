# Descoberta: Registro diário de alunos com acesso dos responsáveis

## Resumo
Um instrutor de esporte, música ou atividade similar não tem registro do que acontece nas aulas e, num episódio de comportamento, perdeu a confiança dos responsáveis. A ideia é um relatório diário por aluno, visível aos pais. **Recomendação: Testar mais**, com um piloto manual no WhatsApp antes de construir. O PRD segue em paralelo, com as hipóteses de maior risco registradas como premissas não validadas.

## Problema
Um aluno desrespeitou o instrutor diante da turma. O instrutor esqueceu de avisar os responsáveis e, ao avisar depois, sem registro do que aconteceu, eles ficaram contra ele. A dor é perder a confiança dos responsáveis por falta de registro e de aviso a tempo. Frequência: 1 caso relatado.

## Usuários e contexto
- **Instrutor (usuário principal):** turmas de 5 alunos por seção. Número de seções: A definir. Hoje não registra nada.
- **Responsáveis dos alunos:** se comunicam com o instrutor por WhatsApp. Passariam a receber e ler o relatório.
- **Alunos:** menores de idade, assunto do relatório.
- **Alternativa hoje:** não fazer nada, e avisar pelo WhatsApp quando lembra.

## O que já sabemos
| Afirmação | Tipo (Evidência / Relato / Suposição) | Fonte |
| -- | -- | -- |
| Aluno desrespeitou o instrutor e o aviso aos pais foi esquecido | Relato | Instrutor (1 caso) |
| Os pais reagiram contra o instrutor ao serem avisados depois | Relato | Instrutor |
| O instrutor não registra o acompanhamento hoje | Evidência | Instrutor |
| São 5 alunos por seção e a comunicação é por WhatsApp | Evidência | Instrutor |
| Um relatório diário resolveria o problema | Suposição | Ninguém testou |
| O instrutor manteria o registro todo dia | Suposição | Ninguém testou |
| Os pais leriam e reagiriam melhor | Suposição | Ninguém testou |

## Hipóteses
| ID | Hipótese | Risco | Sinal que confirma | Sinal que refuta |
| -- | -- | -- | -- | -- |
| H-01 | Acreditamos que instrutores perdem a chance de avisar os responsáveis a tempo e não têm como mostrar o que aconteceu | Alto | Outros instrutores contam casos recentes e concretos | Ninguém lembra de um caso, ou só falam em geral |
| H-02 | Acreditamos que o instrutor registraria a aula todos os dias | Alto | Registra em quase todas as aulas do piloto (sugestão: 80% ou mais) | Registra em bem menos (sugestão: abaixo de 50%) |
| H-03 | Acreditamos que os responsáveis leriam o relatório e reagiriam melhor do que a um aviso solto | Alto | Leem e respondem à maioria dos relatórios (sugestão: a maior parte dos pais, em 2 semanas) | Pouca leitura, ou reação negativa ao conteúdo |

Os limites marcados como sugestão não foram confirmados pelo usuário.

## Plano de validação
| Hipótese | Método | Quem/quantos | Prazo | Resultado esperado |
| -- | -- | -- | -- | -- |
| H-01 | Conversas curtas pedindo o último caso real | Outros instrutores; quantidade A definir | A definir | Casos concretos e recentes |
| H-02 | Piloto manual: nota ou planilha após cada aula | O instrutor, nas suas seções | Sugestão: 2 semanas | Registro feito na maioria das aulas |
| H-03 | No mesmo piloto, enviar o registro aos responsáveis pelo WhatsApp | Pais de 1 seção (5 alunos) | Sugestão: as mesmas 2 semanas | Pais leem e respondem |

## Recomendação
**Testar mais.** Existe uma dor real, mas só um caso relatado, e as duas hipóteses de maior risco (o hábito diário e a reação dos pais) não têm nenhuma evidência. O custo de testar é baixo: o instrutor já usa WhatsApp, então o piloto não exige construir nada.

O que mudaria a recomendação:
- Se H-02 e H-03 forem confirmadas no piloto: **Seguir**, e o app ganha justificativa.
- Se o WhatsApp manual já resolver: **Parar** ou reduzir o projeto, porque um app seria exagero.
- Se o hábito falhar: **Ajustar**, simplificando o registro antes de construir.

## Perguntas em aberto
- Quantas seções o instrutor tem no total?
- O relatório inclui só ocorrências ou também pontos positivos? Quem decide o que os pais veem?
- Os responsáveis precisam de conta, ou basta receber o conteúdo?
- Quais cuidados com dados de menores de idade são necessários? (Risco para o arquiteto e o PRD, sem decisão aqui.)
- Limites e prazos do piloto: A definir até o usuário confirmar.
