import enum
from dataclasses import dataclass
from typing import Dict, Generic

from meta_di.typing import Provider_T, ServiceId_T


class ServiceLifecycle(enum.Enum):
    TRANSIENT = enum.auto()
    SCOPED = enum.auto()
    SINGLETON = enum.auto()


@dataclass
class ServiceDescriptor(Generic[ServiceId_T]):
    """
    Holds information required to build a service
    """

    service_id: ServiceId_T
    provider: Provider_T
    dependency_kwargs: Dict[str, ServiceId_T]
    lifecycle: ServiceLifecycle

    @property
    def is_transient(self) -> bool:
        return self.lifecycle == ServiceLifecycle.TRANSIENT

    @property
    def is_scoped(self) -> bool:
        return self.lifecycle == ServiceLifecycle.SCOPED

    @property
    def is_singleton(self) -> bool:
        return self.lifecycle == ServiceLifecycle.SINGLETON
