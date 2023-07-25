import inspect
from typing import Any, Protocol

from meta_di.exceptions import CannotReferenceError


class InspectorProto(Protocol):
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


class Inspector(InspectorProto):
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


DEFAULT_INSPECTOR = Inspector()
