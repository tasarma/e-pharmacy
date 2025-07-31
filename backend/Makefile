.PHONY: format tests

format:
	pre-commit run --all-files

tests:
	python manage.py test --parallel 2 tests/*