.PHONY: test flake8 pylint mypy pytest

test: flake8 pylint mypy pytest

flake8:
	flake8 .

pylint:
	pylint src/declarativex

mypy:
	mypy src/declarativex

pytest:
	pytest .
