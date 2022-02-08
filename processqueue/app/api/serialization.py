from typing import Type
from typing import TypeVar

T = TypeVar('T')


def serialize(data: T) -> str:
    return type(data).schema().dumps(data)


def deserialize(data_type: Type[T], json_data: str) -> T:
    return data_type.schema().loads(json_data)
