
.PHONY: test

POETRY := python -m poetry

dev: clean hooks
	@$(POETRY) install --with dev,build
	echo "DONE"

hooks:
	@$(POETRY) add pre-commit
	@$(POETRY) run pre-commit install

lint: # suppress exit codes with `|| true` so that both linters can run
	@$(POETRY) run ruff check openLibrary tests || true
	@$(POETRY) run flake8 openLibrary tests || true

bump:
	@$(POETRY) run cz bump

build:
	@$(POETRY) build

test: 
	@$(POETRY) run pytest

clean:
	rm -rf dist/ build/ .pytest_cache/ .coverage mdcov/