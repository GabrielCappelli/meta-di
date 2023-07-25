from typing import Type

from meta_di import ContainerProto
from tests.conftest import IScopedService, ISingletonService, ITransientService


def test_get_singleton__when_same_container__must_be_same_instance(
    container: ContainerProto,
):
    singleton1 = container.get(ISingletonService)
    singleton2 = container.get(ISingletonService)

    assert singleton1 is singleton2


def test_get_singleton__when_different_container__must_be_different_instance(
    container_class: Type[ContainerProto],
):
    container1 = container_class()
    container2 = container_class()

    singleton1 = container1.get(ISingletonService)
    singleton2 = container2.get(ISingletonService)

    assert singleton1 is not singleton2


def test_singleton__when_injected__must_be_same_instance(container: ContainerProto):
    transient1 = container.get(ITransientService)
    transient2 = container.get(ITransientService)

    assert transient1.singleton is transient2.singleton
    assert transient1 is not transient2


def test_get_scoped__when_same_scope__must_be_same_instance(container: ContainerProto):
    with container as scoped_container:
        scoped1 = scoped_container.get(IScopedService)
        scoped2 = scoped_container.get(IScopedService)

        assert scoped1 is scoped2


def test_get_scoped__when_different_scope__must_be_different_instance(
    container: ContainerProto,
):
    with container as scoped_container1:
        scoped1 = scoped_container1.get(IScopedService)

    with container as scoped_container2:
        scoped2 = scoped_container2.get(IScopedService)

    assert scoped1 is not scoped2


def test_scoped__when_injected__must_be_same_instance(container: ContainerProto):
    with container as scoped_container:
        transient1 = scoped_container.get(ITransientService)
        transient2 = scoped_container.get(ITransientService)

        assert transient1.scoped is transient2.scoped
        assert transient1 is not transient2


def test_get_transient__must_be_different_instance(container: ContainerProto):
    transient1 = container.get(ITransientService)
    transient2 = container.get(ITransientService)

    assert transient1 is not transient2
