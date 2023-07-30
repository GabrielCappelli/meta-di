from typing import Any, Mapping, Optional, Set, Type, Union

from meta_di.code_formatter import CodeFormatterProto
from meta_di.container_proto import ContainerProto
from meta_di.exceptions import MissingServiceError
from meta_di.inspector import InspectorProto
from meta_di.service_descriptor import ServiceDescriptor
from meta_di.typing import ServiceId_T


class CodeGenerator:
    """
    Dynamically generates a container class from a set of service descriptors
    """

    _singleton_instances_attr = "self._singleton_instances"
    _scoped_instances_attr = "self._scoped_instances"
    _service_getter_map_attr = "self._service_getter_map"

    def __init__(
        self,
        code_formatter: Optional[CodeFormatterProto],
        inspector: InspectorProto[Any],
        preload_singleton_instances: bool,
        container_svc_ids: Optional[Set[Any]],
    ) -> None:
        self._code_formatter = code_formatter
        self._inspector = inspector
        self._preload_singleton_instances = preload_singleton_instances
        self._container_svc_ids = container_svc_ids or {ContainerProto, "di_container"}

    def _get_getter_method_name(self, svc_desc: ServiceDescriptor[Any]) -> str:
        """
        Get the name of the getter method for the given service
        """
        if isinstance(svc_desc.service_id, str):
            return f"get_{svc_desc.service_id}"
        return f"get_{self._inspector.get_reference(svc_desc.service_id)}".replace(
            ".", "_"
        )

    def _is_container_reference(self, svc_id: Union[str, type]) -> bool:
        """
        Returns true if the service identifier identifies our container
        """
        return svc_id in self._container_svc_ids

    def _gen_imports_code(
        self,
        service_descriptors_map: Mapping[ServiceId_T, ServiceDescriptor[ServiceId_T]],
    ) -> str:
        """
        Generates the code that imports all necessary services and providers
        """
        imports = set()
        for svc_desc in service_descriptors_map.values():
            if self._inspector.requires_import(svc_desc.service_id):
                imports.add(
                    f"import {self._inspector.get_module_name(svc_desc.service_id)}"
                )
            imports.add(f"import {self._inspector.get_module_name(svc_desc.provider)}")

        imports.add(f"import {self._inspector.get_module_name(MissingServiceError)}")
        imports.add(f"import {self._inspector.get_module_name(ContainerProto)}")

        return "\n".join(imports)

    def _gen_create_instance_code(
        self,
        svc_desc: ServiceDescriptor[ServiceId_T],
        service_descriptors_map: Mapping[ServiceId_T, ServiceDescriptor[ServiceId_T]],
    ) -> str:
        """
        Generates the code that is capable of instantiating the given service

        For transient dependencies we will recursively call this function in order to "inline"
        and minimize the amount of function calls

        For scoped/singleton dependencies we will call the container method that gets that service, which
        will be responsible for checking if we need to create a new instance or not

        For container references will simply use `self`
        """
        deps_kwargs = []

        for kwarg, dep in svc_desc.dependency_kwargs.items():
            if self._is_container_reference(dep):
                deps_kwargs.append(f"\n{kwarg}=self,")
                continue

            if dep not in service_descriptors_map:
                raise MissingServiceError(dep)

            dep_svc_desc = service_descriptors_map[dep]
            if dep_svc_desc.is_transient:
                # For transient dependencies we will recursively call this function in order to "inline"
                deps_kwargs.append(
                    f"\n{kwarg}={self._gen_create_instance_code(dep_svc_desc, service_descriptors_map)},"
                )
            elif (
                self._preload_singleton_instances
                and dep_svc_desc.is_singleton
                and not svc_desc.is_singleton
            ):
                # When singletons deps are preloaded we can inline them
                # by getting them directly from the instances dict
                deps_kwargs.append(
                    f"\n{kwarg}={self._singleton_instances_attr}[{self._inspector.get_reference(dep_svc_desc.service_id)}],"
                )
            else:
                deps_kwargs.append(
                    f"\n{kwarg}=self.{self._get_getter_method_name(dep_svc_desc)}(),"
                )

        deps_kwargs_str = "".join(deps_kwargs)
        return (
            f"{self._inspector.get_reference(svc_desc.provider)}({deps_kwargs_str}\n)"
        )

    def _gen_getter_method_code(
        self,
        svc_desc: ServiceDescriptor[ServiceId_T],
        service_descriptors_map: Mapping[ServiceId_T, ServiceDescriptor[ServiceId_T]],
    ) -> str:
        """
        Generates the getter method code.

        For transient services we simply create a new instance and return it

        For singleton/scoped services we first check if we already have an isntance to decide if
        we will create a new instance or not.

        To see how we instantiate services see _gen_create_instance_code
        """
        new_instance_code = self._gen_create_instance_code(
            svc_desc, service_descriptors_map
        )
        method_name = self._get_getter_method_name(svc_desc)

        if svc_desc.is_transient:
            return f"""
    def {method_name}(self):
        return {new_instance_code}
"""
        service_reference = self._inspector.get_reference(svc_desc.service_id)
        instances_attribute = self._singleton_instances_attr
        if svc_desc.is_scoped:
            instances_attribute = self._scoped_instances_attr

        return f"""
    def {method_name}(self):
        if {service_reference} in {instances_attribute}:
            return {instances_attribute}[{service_reference}]

        instance = {new_instance_code}
        {instances_attribute}[{service_reference}] = instance
        return instance
"""

    def _gen_class_code(
        self,
        service_descriptors_map: Mapping[ServiceId_T, ServiceDescriptor[ServiceId_T]],
        class_name: str,
    ) -> str:
        """
        Generates class code

        Uses the given class_name and inherit from ContainerProto

        Inits `self._service_getter_map_attr` to be a map for service_id to the container getter methods
        for that service id
        """
        container_proto_reference = self._inspector.get_reference(ContainerProto)
        class_code = f"""
class {class_name}({container_proto_reference}):

    def __init__(
        self,
        singleton_instances = None,
    ) -> None:
        self._scoped_instances = {{}}
        self._singleton_instances = singleton_instances or {{}}
        {self._service_getter_map_attr} = {{
            {", ".join(f"{self._inspector.get_reference(svc_desc.service_id)}: self.{self._get_getter_method_name(svc_desc)}" for svc_desc in service_descriptors_map.values())}
        }}
"""

        if self._preload_singleton_instances:
            class_code += f"""
        if not singleton_instances:
            self._preload_singletons()

    def _preload_singletons(self):
        {self._singleton_instances_attr}.update({{
            {", ".join(f"{self._inspector.get_reference(svc_desc.service_id)}: self.{self._get_getter_method_name(svc_desc)}()" for svc_desc in service_descriptors_map.values() if svc_desc.is_singleton)}
        }})
"""

        class_code += f"""
    def get(self, service_id):
        if service_id not in {self._service_getter_map_attr}:
            raise {self._inspector.get_full_name(MissingServiceError)}(service_id)
        return {self._service_getter_map_attr}[service_id]()

    def create_scope(self):
        return self.__class__(singleton_instances=self._singleton_instances)

    def __getitem__(self, service_id):
        return self.get(service_id)

    def __enter__(self):
        return self.create_scope()

    def __exit__(self, exc_type, exc_value, traceback):
        pass
"""

        return class_code

    def get_code(
        self,
        service_descriptors_map: Mapping[ServiceId_T, ServiceDescriptor[ServiceId_T]],
        class_name: str = "Container",
    ):
        """
        Generates and returns the code for a Container class with the services in `service_descriptors_map`
        """

        imports_code = self._gen_imports_code(service_descriptors_map)
        class_code = self._gen_class_code(service_descriptors_map, class_name)

        getter_methods_code = ""
        for svc_desc in service_descriptors_map.values():
            getter_methods_code += self._gen_getter_method_code(
                svc_desc, service_descriptors_map
            )

        code = f"""
{imports_code}
{class_code}
{getter_methods_code}
"""

        if self._code_formatter:
            code = self._code_formatter.format(code)

        return code

    def create_class(
        self,
        service_descriptors_map: Mapping[ServiceId_T, ServiceDescriptor[ServiceId_T]],
        class_name: str = "Container",
    ) -> Type[ContainerProto]:
        """
        Generates and executes the code for a Container class with the services in `service_descriptors_map`
        Returns the Type of the newly generated Container class
        """
        code = self.get_code(service_descriptors_map, class_name)

        globs = {}
        exec(code, globs)  # pylint: disable=exec-used
        return globs[class_name]
