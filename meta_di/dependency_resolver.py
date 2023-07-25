import inspect
from typing import Dict, Protocol

from meta_di.typing import Provider_T, ServiceId_T


class ServiceResolverProto(Protocol[ServiceId_T]):
    def __init__(self) -> None:
        """
        We require a constructor without args so it can be instantied by the container
        """
        ...

    def get_dependencies(self, provider: Provider_T) -> Dict[str, ServiceId_T]:
        """
        Extracts dependencies from a  returns them as a dict
        where the keys are the name of the func arguments
        and the values are the ServiceId_T of the dependencies
        """
        ...


class ArgNameServiceResolver(ServiceResolverProto[str]):
    """
    ServiceResolver that uses the names of args as ServiceId_T
    """

    def get_dependencies(self, provider: Provider_T) -> Dict[str, str]:
        return {
            arg_name: arg_name
            for arg_name, arg in inspect.signature(provider).parameters.items()
            if arg_name != "self"
            and arg.kind
            not in (inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL)
        }


class TypeHintServiceResolver(ServiceResolverProto[type]):
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
