from typing import Any, Type, TypeVar, Union

try:
    import pydantic as original_pydantic

    try:
        import pydantic.version as pydantic_version

        if isinstance(
            pydantic_version.VERSION, str
        ) and pydantic_version.VERSION.startswith("2"):
            ...
        else:
            raise ImportError()
    except ImportError:
        version = 1
    else:
        version = 2

    M = TypeVar("M", bound=original_pydantic.BaseModel)
    T = TypeVar("T")

    class Pydantic:
        BaseModel = original_pydantic.BaseModel

        @staticmethod
        def parse_obj(model: Type[M], obj: Any) -> M:
            if version == 1:
                return model.parse_obj(obj)
            return model.model_validate(obj)

        @staticmethod
        def parse_raw(model: Type[M], json_data: Union[str, bytes]) -> M:
            if version == 1:
                return model.parse_raw(json_data)
            return model.model_validate(json_data)

        @staticmethod
        def to_dict(model: M, **kwargs) -> dict:
            if version == 1:
                return model.dict(**kwargs)
            return model.model_dump(**kwargs)

        @staticmethod
        def parse_obj_as(type_: Type[T], obj: Any) -> T:
            if version == 1:
                return original_pydantic.parse_obj_as(type_, obj)
            return original_pydantic.TypeAdapter(type_).validate_python(obj)

    pydantic = Pydantic()
except ImportError:
    pydantic = None  # type: ignore[assignment]
