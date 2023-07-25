from dataclasses import dataclass
from typing import Protocol

import pytest

from meta_di.builder import ContainerBuilder


class ISingletonService(Protocol):
    ...


class SingletonService(ISingletonService):
    ...


class IScopedService(Protocol):
    ...


@dataclass
class ScopedService(IScopedService):
    singleton: ISingletonService


class ITransientService(Protocol):
    ...


@dataclass
class TransientService(ITransientService):
    singleton: ISingletonService
    scoped: IScopedService


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
