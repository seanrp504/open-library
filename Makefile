
.PHONY: test

dev:
	@poetry install --with dev,build
	@poetry run pre-commit install
	@echo "DONE"

hooks:
	@poetry run pre-commit install

lint: # suppress exit codes with `|| true` so that both linters can run
	@poetry run ruff check openLibrary tests || true
	@poetry run flake8 openLibrary tests || true

bump:
	@poetry run cz bump

build:
	@poetry build

test: 
	@poetry run pytest

clean:
	rm -rf dist/ build/ .pytest_cache/ .coverage mdcov/