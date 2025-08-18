.PHONY: format tests run

format:
	pre-commit run --all-files

test:
	python manage.py test  --parallel auto --keepdb --settings=config.settings_test tests

run:
	python manage.py runserver
