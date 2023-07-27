import pytest

from meta_di import ContainerBuilder, ContainerProto, MetaDIException
from tests.conftest import ISingletonService, SingletonService, TransientService


def test_build_container__when_no_provider_specified__then_service_id_is_used_as_provider():
    container = ContainerBuilder().add_singleton(SingletonService).build()

    assert isinstance(container.get(SingletonService), SingletonService)


def test_build_container__when_no_provider_specified_and_service_id_is_not_a_type__then_error_is_raised():
    with pytest.raises(MetaDIException):
        ContainerBuilder().add_singleton("test").build_class()


def test_build_container__when_provider_specified__then_provider_is_used():
    container = (
        ContainerBuilder().add_singleton(ISingletonService, SingletonService).build()
    )

    assert isinstance(container.get(ISingletonService), SingletonService)


def test_build_container__when_using_str_as_service_identifier__get_str_should_work():
    container = ContainerBuilder().add_singleton("singleton", SingletonService).build()

    assert isinstance(container.get("singleton"), SingletonService)


def test_build_container__when_getting_unregistered_service__exception_is_raised():
    container = ContainerBuilder().build()

    with pytest.raises(MetaDIException):
        container.get(ISingletonService)


def test_build_container__when_building_with_missing_dependencies__then_error_is_raised():
    with pytest.raises(MetaDIException):
        ContainerBuilder().add_transient(TransientService).build_class()


def get_123():
    return 123


def test_build_container__when_passing_function_as_provider__then_the_function_is_used():
    container = ContainerBuilder().add_singleton("123", get_123).build()

    assert container.get("123") == 123


def get_container(container: ContainerProto):
    return container


def test_build_container__container_is_injected_as_singleton():
    container = (
        ContainerBuilder().add_singleton(SingletonService, get_container).build()
    )

    assert container.get(SingletonService) is container
    assert container.get(SingletonService) is container.get(SingletonService)


def test_build_container__scoped_container_is_injected_as_singleton():
    container = (
        ContainerBuilder().add_transient(SingletonService, get_container).build()
    )

    with container as scoped_container:
        assert scoped_container.get(SingletonService) is scoped_container
        assert scoped_container.get(SingletonService) is scoped_container.get(
            SingletonService
        )
