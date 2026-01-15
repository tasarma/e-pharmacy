.PHONY: format tests run test test-cov test-fast venv sync

format:
	pre-commit run --all-files

run:
	python src/manage.py runserver

test:
	pytest -v

test-cov:
	pytest --cov=tenants --cov-report=html --cov-report=term

test-fast:
	pytest -x --ff

test-watch:
	ptw -- --testmon

venv:
	uv venv

sync:
	uv sync --group dev  # Install main dependencies with dev dependency group
