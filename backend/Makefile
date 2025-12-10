.PHONY: format tests run test test-cov test-fast

format:
	pre-commit run --all-files

test:
	python manage.py test  --parallel auto --keepdb --settings=config.settings_test tests

run:
	python manage.py runserver

test:
	pytest -v

test-cov:
	pytest --cov=tenants --cov-report=html --cov-report=term

test-fast:
	pytest -x --ff

test-watch:
	ptw -- --testmon
