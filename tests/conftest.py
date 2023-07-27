from typing import Protocol

import pytest

from meta_di.builder import ContainerBuilder


class ISingletonService(Protocol):
    ...


class SingletonService(ISingletonService):
    ...


class IScopedService(Protocol):
    ...


class ScopedService:
    def __init__(self, singleton: ISingletonService) -> None:
        self.singleton = singleton


class ITransientService(Protocol):
    ...


class TransientService:
    def __init__(self, singleton: ISingletonService, scoped: IScopedService) -> None:
        self.singleton = singleton
        self.scoped = scoped


@pytest.fixture
def container_class():
    return (
        ContainerBuilder()
        .add_singleton(ISingletonService, SingletonService)
        .add_scoped(IScopedService, ScopedService)
        .add_transient(ITransientService, TransientService)
        .build_class()
    )


@pytest.fixture
def container(container_class):
    return container_class()
