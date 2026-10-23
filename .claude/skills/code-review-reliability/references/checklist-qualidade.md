# Checklist de Qualidade

Foco do `qa-engineer`: a mudança faz o que foi pedido, falha de forma previsível e tem teste que prova isso. Aplique
cada item e registre no relatório os que falharam.

1. **Critérios de aceite.** Cada critério da tarefa ou do design tem um teste que o prova e que passa. Critério sem
   teste é `WARNING`.
2. **Testes e lint.** A suíte inteira e o lint do repositório passam. Anexe o comando e o total. Falha é `CRITICAL`.
3. **Casos limite.** Entrada vazia, no limite e logo acima do limite (`0`, `-1`, 255 e 256 caracteres), id inexistente e
   id malformado têm comportamento definido e testado.
4. **Erro previsível.** Cada caminho de falha devolve o status certo (`404`, `422`, `409`) com mensagem curta. Exceção
   não tratada que vira `500` é `WARNING`.
5. **Teste que prova.** Cada teste novo falharia se o comportamento quebrasse: asserção sobre o corpo e o efeito, e não
   só sobre o status; valor esperado literal; *mock* só na fronteira externa.
6. **Estado limpo.** Testes criam os próprios dados e não dependem da ordem de execução nem de dado deixado por outro
   teste.
7. **Migração.** Toda migração tem `down` que desfaz o `up`. Coluna obrigatória nova em tabela com dados segue o caminho
   em passos (opcional, preencher, obrigatória).
8. **Frontend.** Tela que busca dado trata carregando, vazio e erro. *Mutation* invalida o cache do recurso alterado.
9. **Espaços e sobras.** `git diff --check` sai vazio. Nada de `print` de depuração, código comentado ou teste marcado
   para pular sem motivo escrito.
