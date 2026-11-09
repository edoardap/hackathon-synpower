# Prepara o repositório do zero: .env e .venv do hook de observabilidade. Pode rodar de novo sem estragar nada.
RAIZ := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))

.PHONY: init venv

init: $(RAIZ)/.env venv

$(RAIZ)/.env:
	cp $(RAIZ)/.env.example $@
	@echo ".env criado: preencha OBS_OTLP_ENDPOINT, OPIK_API_KEY, OPIK_WORKSPACE e OBS_PROJECT (docs/tutorial/configuracao/observabilidade.md)."

venv:
	@command -v uv >/dev/null || { echo "uv nao encontrado: https://docs.astral.sh/uv/"; exit 1; }
	cd $(RAIZ) && uv sync
