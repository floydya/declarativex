Declare parameters

This table outlines the arguments you can pass to the decorator, detailing their type, 
whether they're required or optional, and what each argument is for.

#### Positional arguments

|           Name           |       Type       |           Required            |    Arg type    | Description                                                       |
|:------------------------:|:----------------:|:-----------------------------:|:--------------:|-------------------------------------------------------------------|
|         `method`         |  `#!python str`  |              Yes              |    Position    | Specifies the HTTP method (e.g., GET, POST, PUT) you want to use. |
|          `path`          |  `#!python str`  |              Yes              |   Position    | Defines the API endpoint path you're hitting.                     |

!!! danger "Required parameters"
    If you don't specify `method` or `path` in decorator, you will get `#!python ValueError` exception at the runtime.

#### Keyword-only arguments

|           Name           |                      Type                      |              Required               |    Arg type    | Description                                                                      |
|:------------------------:|:----------------------------------------------:|:-----------------------------------:|:--------------:|----------------------------------------------------------------------------------|
|        `base_url`        |                 `#!python str`                 | [Not always](#base_url "See below") |    Keyword     | Sets the base URL for the request.                                               |
|        `timeout`         |                 `#!python int`                 |    No, default: `#!python None`     |    Keyword     | The timeout to use.                                                              |
|    `default_headers`     |                `#!python dict`                 |    No, default: `#!python None`     |    Keyword     | The headers to use with every request.                                           |
|  `default_query_params`  |                `#!python dict`                 |    No, default: `#!python None`     |    Keyword     | The params to use with every request.                                            |
| `middlewares` | `#!python list`  |    No, default: `#!python None`     |    Keyword     | The [middlewares](middlewares.md) to use with every request.       |
| `error_mappings` | `#!python dict`  |    No, default: `#!python None`     |    Keyword     | The [error mappings](error-mappings.md) to use with every request. |

<div id="base_url" markdown>
!!! danger "`base_url`"
    This is necessary if the method is not part of a class that already specifies it.

    If you don't specify `base_url` in function-based declaration, you will get `#!python ValueError` exception at the runtime.
</div>