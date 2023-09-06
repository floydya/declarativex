# Testing DeclarativeX 🧪

## Introduction

Hey, Tester! So you're the kind of person who likes to make sure everything's working as it should, huh? Good on ya!
Testing is crucial, and DeclarativeX is no exception. This guide will walk you through how to set up and write tests for
your DeclarativeX project.

!!! note
    We'll be using pytest for our examples. If you're not familiar with it,
    you might wanna check it out. It's pretty rad.

## Setting Up your Test Environment

First things first, let's get your test environment up and running. You'll need to install pytest and any other
dependencies you might need.

```bash
pip install pytest
```

!!! tip
    You can also create a requirements-test.txt file to manage your test dependencies separately.
    Just run pip install -r requirements-test.txt to install them all in one go.

## Writing your first test

Alright, let's write our first test. Create a file named test_client.py in your tests directory.

```python
import pytest

from myapp.services.example import ExampleClient


class TestExampleClient:

    @pytest.fixture
    def client(self):
        return ExampleClient()

    def test_get_user(self, client):
        response = client.get_user(user_id=1)
        assert response.status_code == 200
        assert response.data == {"id": 1, "name": "John Doe"}
```

!!! warning
    Make sure you mock any external calls to prevent actual API requests during tests.
    E.g. you can mock them in `conftest.py` with patch context managers.

## Running Tests

To run your tests, simply execute the following command:

```bash
pytest
```

!!! success
    If everything's set up correctly, you should see a beautiful green line of dots indicating
    your tests have passed. If not, back to the drawing board!

## Advanced Testing

Feeling adventurous? You can also write more advanced tests, like testing exceptions, timeouts, and so on.

!!! info
    Check out the pytest documentation for more advanced features like parameterized testing, fixtures, and markers.

