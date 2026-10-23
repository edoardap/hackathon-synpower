# Onde Procurar Além do Script

Pontos que a varredura por padrão não cobre. Confira cada um no repositório ou no diff em revisão.

| Ponto                      | O que procurar                                                                                                 | Como achar                                                                         |
| -------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Padrão inseguro            | `getenv`, `os.environ.get` ou campo de `Settings` com valor padrão de exemplo para chave, senha ou token       | `grep -rn "getenv\|environ.get" --include=*.py`; o campo em `config.py`            |
| Log                        | Token, senha, cabeçalho `Authorization` ou o objeto de configuração inteiro passados ao *logger* ou ao `print` | `grep -rn "logger\.\|print(" ` perto de `token`, `password`, `headers`, `settings` |
| Erro                       | Mensagem de exceção com string de conexão ou credencial devolvida ao cliente                                   | `except` que devolve `str(e)`                                                      |
| `.env.example`             | Valor real em vez de marcador                                                                                  | Leitura do arquivo de exemplo, que é versionado de propósito                       |
| `Dockerfile`               | `ENV` ou `ARG` com segredo, `COPY .env`                                                                        | Leitura do `Dockerfile` e do `compose.yml`                                         |
| CI                         | Segredo escrito no YAML em vez de variável protegida do CI (`secrets.X`, variável mascarada)                   | `.github/workflows/`, `.gitlab-ci.yml`                                             |
| Frontend                   | Chave de API privada em variável de *build* (`VITE_*`, `NEXT_PUBLIC_*`), que vai para o navegador              | `grep -rn "VITE_\|NEXT_PUBLIC_"`                                                   |
| Notebook e dado de exemplo | Saída de célula com token, *dump* de banco com dado pessoal                                                    | `*.ipynb`, `*.sql`, `*.csv` versionados                                            |
