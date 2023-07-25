from typing import Any, Protocol, Type

from meta_di.typing import T


class ContainerProto(Protocol):
    def get(self, service_id: Type[T]) -> T:
        """
        Returns an instance of the service identified by `service_id`.
        """
        ...

    def create_scope(self) -> "ContainerProto":
        """
        Creates and return a new scoped container instance.

        During the lifetime of the scoped container, scoped instances will be
        shared between calls to `get` for the same service id.

        Singleton instances will be shared between any other container instances created
        from the same base container.
        """
        ...

    def __enter__(self) -> "ContainerProto":
        """Syntax sugar for `create_scope`"""
        ...

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any):
        """Syntax sugar for `create_scope`"""
        ...

    def __getitem__(self, service_id: Type[T]) -> T:
        """Syntax sugar for `get`"""
        ...
