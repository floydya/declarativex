.PHONY: test black flake8 pylint mypy pytest

test: black flake8 pylint mypy pytest

black:
	black .

flake8:
	flake8 .

pylint:
	pylint src/declarativex

mypy:
	mypy src/declarativex

pytest:
	pytest .
