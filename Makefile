

dev:
	poetry install # TODO add pre-commit
	echo "DONE!"

test: 
	poetry run pytest --cov=openLibrary --cov-report=term-missing --cov-fail-under=85 --durations=5 --tb=short 