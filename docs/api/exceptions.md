<!-- markdownlint-disable -->

# <kbd>module</kbd> `exceptions.py`

**Global Variables**
---------------

- **TYPE_CHECKING**

---

## <kbd>class</kbd> `AnnotationException`

Raised when an unsupported annotation is used.

**Parameters:**

- <b>`annotation`</b> (`Type`):  The annotation that was used.

### <kbd>function</kbd> `__init__`

```python
__init__(annotation: Type)
```

---

## <kbd>class</kbd> `DeclarativeException`

Base class for all declarativex exceptions.





---

## <kbd>class</kbd> `DependencyValidationError`

Raised when a dependency cannot be validated.

**Parameters:**

- <b>`expected_type`</b> (`Union[Type, Sequence[Type]]`):  The dependency that failed validation.
- <b>`received_type`</b> (`Type`):  The type that was received.

### <kbd>function</kbd> `__init__`

```python
__init__(expected_type: Union[Type, Sequence[Type]], received_type: Type)
```

---

## <kbd>class</kbd> `HTTPException`

Raised when a request fails with HTTP status code.

**Parameters:**

- <b>`request`</b> (`httpx.Request`):  The request that failed.
- <b>`response`</b> (`httpx.Response`):  The response that was received.
- <b>`raw_request`</b> ([`RawRequest`](./models.md#class-rawrequest)):  The raw request that was sent.
- <b>`error_mappings`</b> (`Mapping[int, Type]`):  A mapping of status codes to error models.

### <kbd>function</kbd> `__init__`

```python
__init__(
    request: Request,
    response: Response,
    raw_request: 'RawRequest',
    error_mappings: Optional[Mapping[int, Type]] = None
)
```

---

#### <kbd>property</kbd> response

The response that was received. If a model is specified, the response will be parsed and returned as an instance of that
model. :return: httpx.Response or Instance of self._model




---

## <kbd>class</kbd> `MisconfiguredException`

Raised when a client is misconfigured.





---

## <kbd>class</kbd> `TimeoutException`

Raised when a request times out.

**Parameters:**

- <b>`timeout`</b> (`Optional[float]`):  The timeout in seconds.
- <b>`request`</b> (`httpx.Request`):  The request that timed out.

### <kbd>function</kbd> `__init__`

```python
__init__(timeout: Optional[float], request: Request)
```

---

## <kbd>class</kbd> `UnprocessableEntityException`

Raised when a request fails when parsing of the response fails.

**Parameters:**

- <b>`response`</b> (`httpx.Response`):  The response that was received.

### <kbd>function</kbd> `__init__`

```python
__init__(response: Response)
```

---

## <kbd>class</kbd> `RateLimitExceeded`

Raised when a request fails due to rate limiting.

