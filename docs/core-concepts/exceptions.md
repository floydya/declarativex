# Exceptions

DeclarativeX provides a set of exceptions that can be used to handle errors.

## Types of Exceptions

### DeclarativeException

Base exception for all exceptions. It is inherited from `Exception`.

### MisconfiguredException

Inherited from `DeclarativeException`. Raised when the client is misconfigured.

For example, when the client is missing the `base_url` attribute.

### DependencyValidationError

Raised when the dependency validation fails. 

For example, when the value you pass to the function argument is not valid for the type hint.

### TimeoutException

Raised when the request times out.

Can be raised when the `timeout` is declared.

### HTTPException

Inherited from `DeclarativeException`. Raised when the response status code is not 2xx.

Has the following attributes:

- `status_code` - response status code
- `response` - parsed response object
- `request` - request object
- `raw_request` - raw request object (dictionary with all the data, passed to httpx)
