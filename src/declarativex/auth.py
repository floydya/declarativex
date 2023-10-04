import abc
import base64
from typing import TYPE_CHECKING

from .dependencies import Location

if TYPE_CHECKING:
    from .models import RawRequest


class Auth(abc.ABC):
    location: Location
    key: str
    value: str

    def apply_auth(self, request: 'RawRequest') -> 'RawRequest':
        obj = getattr(request, self.location.value)
        obj[self.key] = self.value
        setattr(request, self.location.value, obj)
        return request


class QueryParamsAuth(Auth):
    location = Location.query_params

    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value


class HeaderAuth(Auth):
    location = Location.headers

    def __init__(self, header_name: str, value: str):
        self.key = header_name
        self.value = value


class BasicAuth(Auth):
    location = Location.headers
    key = "Authorization"

    def __init__(self, username: str, password: str):
        self.value = base64.b64encode(
            f"{username}:{password}".encode("utf-8")
        ).decode("utf-8")


class BearerAuth(Auth):
    location = Location.headers
    key = "Authorization"

    def __init__(self, token: str):
        self.value = f"Bearer {token}"
