.PHONY: all install clean lint format test spell_check

all: build

install:
	poetry install

clean:
	poetry run clean
	poetry env remove --all

lint: install
	poetry run nox -s lint

format: install
	poetry run nox -s format

test: install
	poetry run nox -s test $(if $(PYTHON),--python=$(PYTHON),)

integration_test: install
	poetry run nox -s integration_test $(if $(PYTHON),--python=$(PYTHON),)

coverage: install
	poetry run nox -s coverage

publish: build
	poetry publish -u __token__ -p ${PYPI_TOKEN} --skip-existing

help:
	@echo '===================='
	@echo 'install                      - install virtual env and dependencies'
	@echo 'clean                        - clean virtual env and build artifacts'
	@echo '-- LINTING --'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
	@echo 'spell_check                  - run spell check'
