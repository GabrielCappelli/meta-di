from typing import Any, Callable, TypeVar, Union

T = TypeVar("T")
ServiceId_T = TypeVar("ServiceId_T", bound=Union[str, type])
Provider_T = Union[type, Callable[..., Any]]
