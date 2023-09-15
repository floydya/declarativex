<!-- markdownlint-disable -->

# <kbd>module</kbd> `models`

**Global Variables**
---------------

- **SUPPORTED_METHODS**

---

## <kbd>class</kbd> `Response`

Wrapper around httpx.Response that provides a method to convert the response to a specific type.

**Parameters:**

- <b>`response`</b>:  The response to wrap.

Methods:

- <b>`as_type`</b>:  Convert the response to a specific type.
- <b>`as_type_for_func`</b>:  Convert the response to the return type of function.

### <kbd>method</kbd> `__init__`

```python
__init__(response: Response) → None
```

---

### <kbd>method</kbd> `as_type`

```python
as_type(type_hint: Type)
```

Convert the response to a specific type. Supports dataclasses, pydantic models, dictionaries and lists of them.

---

### <kbd>method</kbd> `as_type_for_func`

```python
as_type_for_func(func: Callable[, ~ReturnType]) → ~ReturnType
```

Convert the response to the return type of function.


---

## <kbd>class</kbd> `ClientConfiguration`

Configuration for a client. This class is used to configure the client with default values for query parameters,
headers, middlewares and error mappings. The configuration can be passed to the client as a parameter or as a class
attribute.

### <kbd>method</kbd> `__init__`

```python
__init__(
    base_url: Optional[str] = None,
    default_query_params: Dict[str, Any] = < factory >,
    default_headers: Dict[str, str] = < factory >,
    middlewares: Sequence[Union[Middleware, AsyncMiddleware]] = < factory >,
    error_mappings: Dict[int, Type] = < factory >
) → None
```

---

### <kbd>classmethod</kbd> `create`

```python
create(**values) → ClientConfiguration
```

Create a configuration from a dictionary. The dictionary can contain any of the attributes of the configuration. If an
attribute is not present in the dictionary, the default value will be used.

---

### <kbd>classmethod</kbd> `extract_from_func_kwargs`

```python
extract_from_func_kwargs(
    self_: Optional[BaseClient],
    cls_: Optional[BaseClient]
) → Optional[ForwardRef('ClientConfiguration')]
```

Extract the configuration from the function bounded to class. If function is not bounded to class, return None.

---

### <kbd>method</kbd> `merge`

```python
merge(other: 'ClientConfiguration') → ClientConfiguration
```

Merge two configurations. The values of the other configuration take precedence over the values of this configuration.


---

## <kbd>class</kbd> `EndpointConfiguration`

Configuration for an endpoint. This class is used to configure the endpoint with a method, path, timeout and client
configuration.

### <kbd>method</kbd> `__init__`

```python
__init__(
    client_configuration: ClientConfiguration,
    method: str,
    path: str,
    timeout: Optional[float] = 5.0
) → None
```

---

#### <kbd>property</kbd> url_template

The URL template for the endpoint. The URL template is the base URL of the client configuration joined with the path of
the endpoint configuration.




---

## <kbd>class</kbd> `RawRequest`

A raw request. This class is used to configure a request with a method, URL template, path parameters, query parameters,
headers, cookies, JSON body and timeout. The request can be prepared with a function and arguments. The function
signature is used to modify the request before it is sent.

### <kbd>method</kbd> `__init__`

```python
__init__(
    method: str,
    url_template: str,
    path_params: Dict[str, str] = < factory >,
    query_params: Dict[str, Any] = < factory >,
    headers: Dict[str, str] = < factory >,
    cookies: Dict[str, str] = < factory >,
    json: Dict[str, Any] = < factory >,
    timeout: Optional[float] = None
) → None
```

---

### <kbd>classmethod</kbd> `initialize`

```python
initialize(endpoint_configuration: EndpointConfiguration) → RawRequest
```

Initialize a request from an endpoint configuration. The request will be initialized with the default query parameters
and headers of the client configuration.

---

### <kbd>method</kbd> `prepare`

```python
prepare(func: Callable, ** values) → RawRequest
```

Prepare the request with a function and arguments. The function signature is used to modify the request before it is
sent.

---

### <kbd>method</kbd> `to_httpx_request`

```python
to_httpx_request() → Request
```

Convert the request to a httpx.Request. 
