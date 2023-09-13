from src.declarativex.middlewares import (
    Middleware,
    AsyncMiddleware,
    ReturnType,
)
from src.declarativex.models import RawRequest


class SyncDummyMiddleware(Middleware):
    def modify_request(self, request: RawRequest) -> RawRequest:
        assert isinstance(request, RawRequest)
        request.query_params["userId"] = 1
        return request

    def modify_response(self, response: ReturnType) -> ReturnType:
        assert response is not None
        return response


class AsyncDummyMiddleware(AsyncMiddleware):
    async def modify_request(self, request: RawRequest) -> RawRequest:
        assert isinstance(request, RawRequest)
        request.query_params["userId"] = 2
        return request

    async def modify_response(self, response: ReturnType) -> ReturnType:
        assert response is not None
        return response


class SyncInvalidDummyMiddleware(Middleware):
    def modify_request(self, request: 'RawRequest') -> 'RawRequest':
        assert isinstance(request, RawRequest)
        return None

    def modify_response(self, response: ReturnType) -> ReturnType:
        return response


class AsyncInvalidDummyMiddleware(AsyncMiddleware):
    async def modify_request(self, request: 'RawRequest') -> 'RawRequest':
        assert isinstance(request, RawRequest)
        return None

    async def modify_response(self, response: ReturnType) -> ReturnType:
        return response
