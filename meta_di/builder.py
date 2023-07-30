from typing import Any, Dict, Generic, Optional, Set, Type

from meta_di.code_formatter import DEFAULT_CODE_FORMATTER, CodeFormatterProto
from meta_di.code_generator import CodeGenerator
from meta_di.container_proto import ContainerProto
from meta_di.exceptions import CannotInferProvider
from meta_di.inspector import InspectorProto, TypeHintInspector
from meta_di.service_descriptor import ServiceDescriptor, ServiceLifecycle
from meta_di.typing import Provider_T, ServiceId_T


class ContainerBuilder(Generic[ServiceId_T]):
    """
    Builder to help generate a container class from a set of services
    """

    def __init__(
        self,
        inspector: InspectorProto[ServiceId_T] = TypeHintInspector(),
        code_formatter: Optional[CodeFormatterProto] = DEFAULT_CODE_FORMATTER,
        preload_singleton_instances: bool = True,
        container_svc_ids: Optional[Set[Any]] = None,
    ) -> None:
        """
        inspector: InspectorProto to use to inspect the dependencies of services. Defaults to TypeHintInspector
        code_formatter: CodeFormatterProto to use to format the generated code. Defaults to black if installed
        preload_singleton_instances: If true, singleton instances will be created when the container is instantiated. Defaults to True
        container_svc_ids: Set of service identifiers that identify the container. Defaults to {ContainerProto, "di_container"}
        """
        self._service_descriptors_map: Dict[
            ServiceId_T, ServiceDescriptor[ServiceId_T]
        ] = {}

        self._inspector = inspector

        self._code_generator = CodeGenerator(
            inspector=inspector,
            code_formatter=code_formatter,
            preload_singleton_instances=preload_singleton_instances,
            container_svc_ids=container_svc_ids,
        )

    def _add_service(
        self,
        service_id: ServiceId_T,
        provider: Optional[Provider_T] = None,
        lifecycle: ServiceLifecycle = ServiceLifecycle.TRANSIENT,
    ) -> "ContainerBuilder[ServiceId_T]":
        if provider is None:
            if not isinstance(service_id, type):
                raise CannotInferProvider(service_id)

            provider = service_id

        dependency_kwargs = self._inspector.get_dependencies(provider)
        self._service_descriptors_map[service_id] = ServiceDescriptor(
            service_id=service_id,
            provider=provider,
            dependency_kwargs=dependency_kwargs,
            lifecycle=lifecycle,
        )

        return self

    def add_transient(
        self, service_id: ServiceId_T, provider: Optional[Provider_T] = None
    ):
        """
        Register service_id as a transient service.
        This means that a new instance of this service will be created every time it is requested.
        """
        return self._add_service(service_id, provider, ServiceLifecycle.TRANSIENT)

    def add_scoped(
        self, service_id: ServiceId_T, provider: Optional[Provider_T] = None
    ):
        """
        Register service_id as a scoped service.
        This means that an instance of this container will only have one instance of this service within the same scope.
        """
        return self._add_service(service_id, provider, ServiceLifecycle.SCOPED)

    def add_singleton(
        self, service_id: ServiceId_T, provider: Optional[Provider_T] = None
    ):
        """
        Register service_id as a singleton.
        This means that an instance of this container will only have one instance of this service.
        """
        return self._add_service(service_id, provider, ServiceLifecycle.SINGLETON)

    def build_class(self) -> Type[ContainerProto]:
        """
        Returns a new container *class* with all the services registered in this builder.
        """
        return self._code_generator.create_class(self._service_descriptors_map)

    def build(self) -> ContainerProto:
        """
        Returns a new container *instance* with all the services registered in this builder.
        NOTE: This method will generate a new class every time it is called.
        """
        return self.build_class()()

    def get_code(self) -> str:
        """
        Returns the code to generate the container class.
        You can use this to save the generated code to a file or print it out.
        """
        return self._code_generator.get_code(self._service_descriptors_map)
