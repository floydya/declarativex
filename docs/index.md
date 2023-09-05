# Welcome to DeclarativeX 🚀

## Introduction

Hey there! Welcome to the official documentation of DeclarativeX. If you're tired of writing boilerplate code for HTTP
clients and want a more declarative approach, you're in the right place. DeclarativeX is designed to make your life
easier, letting you focus on what really matters—your application logic.

## Installation

Getting started with DeclarativeX is a breeze. Just run the following command:

```bash
pip install declarativex
```

And boom! You're good to go.

## Quick Start Guide

Ready to dive in? Here's a quick example to get you started:

```{.python title="my_client.py"}
from declarativex import BaseClient, get


class MyClient(BaseClient):
    @get("/users/{user_id}")
    def get_user(self, user_id: int):
        pass


client = MyClient(base_url="https://api.example.com")
response = client.get_user(user_id=1)
print(response.json())
```
???+ success "You should see the following output:"
    ```json
    {
      "id": 1,
      "name": "John Doe"
    }
    ```

See? No fuss, just clean and straightforward code.

## Why DeclarativeX?

- **Less Boilerplate**: No more repetitive code for HTTP methods.
- **Type-Safe**: Built with type annotations for better code quality.
- **Flexible**: Easily extendable to fit your specific needs.

## What's Next?

Feel free to explore the documentation to get a deeper understanding of DeclarativeX. Whether you're looking to understand the core concepts, decorators, or how to set up parameters, we've got you covered.

- [BaseClient](Core_Concepts/BaseClient.md)
- [Decorators](Core_Concepts/Decorators.md)
- [Parameters](Core_Concepts/Parameters.md)

## Contributing

Love DeclarativeX and want to contribute? Awesome! Check out our [Contribution Guidelines](Contributing.md).

