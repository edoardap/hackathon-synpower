# Checklist de Arquitetura e PR

Foco do `code-reviewer` ao juntar os outros focos: a mudança cabe no repositório como se tivesse sido escrita por quem o
mantém. Aplique cada item e registre no relatório os que falharam.

1. **Escopo.** O diff traz só o que a tarefa pede. Arquivo alterado sem relação com a tarefa é `WARNING`; refatoração
   oportunista misturada à funcionalidade vai como `SUGGESTION` para PR separado.
2. **Regras do repositório.** Nada contradiz o `AGENTS.md`, o guia de contribuição ou um ADR aceito.
3. **Padrão vizinho.** Lugar do arquivo, nome, camada, forma de erro e forma de teste seguem o código vizinho. Camada ou
   biblioteca nova sem pedido é `WARNING`.
4. **Reuso.** Código novo não duplica *helper*, componente ou dependência que o repositório já tem.
5. **Contrato.** Mudança em rota, schema de resposta ou tipo público não quebra cliente existente. Quebra sem plano de
   versão é `CRITICAL`.
6. **Arquivos gerados.** Cliente da API, árvore de rotas e *lock* foram gerados pela ferramenta, e não editados à mão.
7. **Descrição do PR.** Diz o que muda, por quê, como testar e o que fica de fora. Ausência é `SUGGESTION`.
