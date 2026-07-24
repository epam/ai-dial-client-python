VENV_DIR ?= .venv
POETRY ?= poetry
POETRY_PYTHON ?= python

# Any non-empty CI value (even 'false' or '0') means that CI is enabled
CI ?=

.PHONY: all init_env install clean lint format test

-include .env
export

all: build

init_env:
	$(if $(CI),,$(POETRY) env use $(POETRY_PYTHON))

install: init_env
	$(POETRY) install

build: install
	$(POETRY) build

clean:
	$(POETRY) run clean
	$(POETRY) env remove --all

install_git_hooks: install
	$(VENV_DIR)/bin/pre-commit install

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
	@echo 'install_git_hooks            - install the git hooks'
	@echo '-- LINTING --'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
