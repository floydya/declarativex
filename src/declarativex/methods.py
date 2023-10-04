from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Type,
    Sequence,
)

from .auth import Auth
from .executors import AsyncExecutor, SyncExecutor
from .middlewares import Middleware
from .models import (
    ClientConfiguration,
    EndpointConfiguration,
    GraphQLConfiguration,
)
from .utils import Decorator


class _Declaration(Decorator):
    client_configuration: ClientConfiguration
    endpoint_configuration: EndpointConfiguration

    async def _decorate_async(self, func: Callable, *args, **kwargs):
        return await AsyncExecutor(
            endpoint_configuration=self.endpoint_configuration
        ).execute(func, *args, **kwargs)

    def _decorate_sync(self, func: Callable, *args, **kwargs):
        return SyncExecutor(
            endpoint_configuration=self.endpoint_configuration
        ).execute(func, *args, **kwargs)


class http(_Declaration):
    def __init__(
        self,
        method: str,
        path: str,
        *,
        timeout: Optional[float] = None,
        base_url: str = "",
        auth: Optional[Auth] = None,
        default_query_params: Optional[Dict[str, Any]] = None,
        default_headers: Optional[Dict[str, str]] = None,
        middlewares: Optional[Sequence[Middleware]] = None,
        error_mappings: Optional[Dict[int, Type]] = None,
    ):
        self.client_configuration = ClientConfiguration.create(
            base_url=base_url,
            auth=auth,
            default_query_params=default_query_params,
            default_headers=default_headers,
            middlewares=middlewares,
            error_mappings=error_mappings,
        )

        self.endpoint_configuration = EndpointConfiguration(
            method=method,
            path=path,
            timeout=timeout,
            client_configuration=self.client_configuration,
        )


class gql(_Declaration):
    def __init__(
        self,
        query: str,
        *,
        base_url: str = "",
        timeout: Optional[float] = None,
        auth: Optional[Auth] = None,
        default_query_params: Optional[Dict[str, Any]] = None,
        default_headers: Optional[Dict[str, str]] = None,
        middlewares: Optional[Sequence[Middleware]] = None,
        error_mappings: Optional[Dict[int, Type]] = None,
    ):
        try:
            from graphql.parser import GraphQLParser  # type: ignore  # noqa: F401, E501
        except ImportError:  # pragma: no cover
            raise ImportError(
                "Please install extra using 'pip install "
                "declarativex[graphql]' to use gql decorator"
            )

        self.client_configuration = ClientConfiguration.create(
            base_url=base_url,
            auth=auth,
            default_query_params=default_query_params,
            default_headers=default_headers,
            middlewares=middlewares,
            error_mappings=error_mappings,
        )

        self.endpoint_configuration = EndpointConfiguration(
            method="POST",
            path="",
            timeout=timeout,
            client_configuration=self.client_configuration,
            gql=GraphQLConfiguration(
                query=query,
            ),
        )
