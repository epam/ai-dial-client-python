VENV_DIR ?= .venv
POETRY ?= $(VENV_DIR)/bin/poetry
POETRY_VERSION ?= 1.8.5

.PHONY: all init_env install clean lint format test spell_check

all: build

init_env:
	python -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install poetry==$(POETRY_VERSION) --quiet

install: init_env
	$(POETRY) install

build: install
	$(POETRY) build

clean:
	$(POETRY) run clean
	$(POETRY) env remove --all

lint: install
	$(POETRY) run nox -s lint

format: install
	$(POETRY) run nox -s format

test: install
	$(POETRY) run nox -s test $(if $(PYTHON),--python=$(PYTHON),)

integration_test: install
	$(POETRY) run nox -s integration_test $(if $(PYTHON),--python=$(PYTHON),)

coverage: install
	$(POETRY) run nox -s coverage

publish: build
	$(POETRY) publish -u __token__ -p $(PYPI_TOKEN) --skip-existing

help:
	@echo '===================='
	@echo 'install                      - install virtual env and dependencies'
	@echo 'clean                        - clean virtual env and build artifacts'
	@echo '-- LINTING --'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
	@echo 'spell_check                  - run spell check'
