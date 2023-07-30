import inspect
from typing import Any, Dict, Protocol

from meta_di.exceptions import CannotReferenceError
from meta_di.typing import Provider_T, ServiceId_T


class InspectorProto(Protocol[ServiceId_T]):
    """
    Inspects objects to get required information for code generation
    """

    def requires_import(self, obj: Any) -> bool:
        """
        Returns true if the given object requires an import
        """
        ...

    def get_reference(self, obj: Any) -> str:
        """
        Get a string reference we can use to import or reference the given svc_id or provider

        Raises CannotReferenceError if we cannot get a reference to the given svc_id or provider
        """
        ...

    def get_module_name(self, obj: Any) -> str:
        """
        Get the module name of the given object.
        If replace_main is True, and the module name is __main__, we will return the name of the file instead

        Raises CannotReferenceError if we cannot get a reference to the given svc_id or provider
        """
        ...

    def get_full_name(self, obj: Any) -> str:
        """
        Get the full name of the given object.
        If replace_main is True, and the module name is __main__, we will return the name of the file instead

        Raises CannotReferenceError if we cannot get a reference to the given svc_id or provider
        """
        ...

    def get_dependencies(self, provider: Provider_T) -> Dict[str, ServiceId_T]:
        """
        Extracts dependencies from a provider and returns them as a dict
        where the keys are the name of the func arguments
        and the values are the ServiceId_T of the dependencies
        """
        ...


class BaseInspector(InspectorProto[ServiceId_T]):
    def requires_import(self, obj: Any) -> bool:
        if isinstance(obj, type):
            return True
        return False

    def get_reference(self, obj: Any) -> str:
        if isinstance(obj, str):
            return f'"{obj}"'
        return self.get_full_name(obj)

    def get_module_name(self, obj: Any) -> str:
        module = inspect.getmodule(obj)

        if not module or not getattr(module, "__name__", None):
            raise CannotReferenceError(obj)

        return module.__name__

    def get_full_name(self, obj: Any) -> str:
        return f"{self.get_module_name(obj)}.{obj.__qualname__}"

    def get_dependencies(self, provider: Provider_T) -> Dict[str, ServiceId_T]:
        raise NotImplementedError()


class TypeHintInspector(BaseInspector[type]):
    """
    DependencyResolver that uses the types extracted from type hints as ServiceId_T
    """

    def get_dependencies(self, provider: Provider_T) -> Dict[str, type]:
        return {
            arg_name: arg_type
            for arg_name, arg_type in inspect.getfullargspec(
                provider
            ).annotations.items()
            if arg_name != "self" and arg_type
        }


class ArgNameInspector(BaseInspector[str]):
    """
    DependencyResolver that uses the names of args as ServiceId_T
    """

    def get_dependencies(self, provider: Provider_T) -> Dict[str, str]:
        return {
            arg_name: arg_name
            for arg_name, arg in inspect.signature(provider).parameters.items()
            if arg_name != "self"
            and arg.kind
            not in (inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL)
        }
