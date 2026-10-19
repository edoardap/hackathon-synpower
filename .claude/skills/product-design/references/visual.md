# Design visual: princípios, tokens e componentes

## Roteiro

1. **Verifique o que já existe.** Procure marca, cores, fontes ou um design system no repositório e nos docs. Se existir, siga-o e não invente outro.
2. **Princípios visuais.** De 3 a 5 frases que orientam as decisões (ex.: "claro antes de bonito", "poucas cores, com uma de destaque"), ligadas ao usuário e ao tom do produto.
3. **Tokens.** Defina valores nomeados, não valores soltos: cores (neutras, primária, estados de sucesso, aviso, erro), tipografia (família, tamanhos, pesos), espaçamento, raio de borda, sombra. Use uma escala curta e consistente.
4. **Componentes.** Liste o que as telas precisam (botão, campo, cartão, lista, alerta, modal, passo a passo, indicador de estado) com variações e estados (padrão, foco, desabilitado, erro).
5. **Modo claro e escuro**, se o público ou o projeto pedirem. Marque como pendência se não foi definido.

## Regras

- **Não invente identidade.** Sem marca definida, proponha uma paleta neutra e funcional, marcada `a validar`, e não imite marcas existentes.
- **Contraste primeiro.** Valide pares de cor texto e fundo contra o contraste mínimo (WCAG AA). Cores de estado (erro, sucesso) vêm sempre acompanhadas de ícone ou texto.
- **Poucas cores, poucas fontes.** Uma família tipográfica principal e uma escala de tamanhos curta bastam para um MVP.
- **Componentes pelo uso.** Só especifique componentes que alguma tela do MVP usa.
- **Valores como tokens.** Nas telas, referencie o token (`cor-primaria`), não o valor hexadecimal.

## Formato dos tokens

```
| Token | Valor | Uso |
|---|---|---|
| cor-primaria | <valor, a validar> | ações principais |
```

Deixe o valor como `a definir` quando não houver base para escolher, em vez de chutar.
