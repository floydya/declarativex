.PHONY: test black flake8 pylint mypy pytest

test: flake8 pylint mypy pytest

black:
	black .

flake8:
	flake8 src/declarativex

pylint:
	pylint src/declarativex

mypy:
	mypy src/declarativex

pytest:
	pytest -n 6 tests/
