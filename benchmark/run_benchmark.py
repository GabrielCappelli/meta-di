import inspect
import time
from timeit import timeit

import services
from dependency_injector import containers, providers
from rodi import Container as RodiContainer
from services import BarService, Cache, Config, Database, FooService, HTTPClient

from meta_di import ContainerBuilder


class SimpleContaner:
    def __init__(
        self,
        transient_services: dict[type, type],
        singleton_services: dict[type, type],
    ):
        self._transient_services = transient_services or {}
        self._singleton_services = singleton_services or {}
        self._singleton_instances: dict[type, type] = {}

    def _get_dependencies(self, service_id: type):
        return inspect.getfullargspec(service_id.__init__).annotations

    def get(self, service_id: type):
        if service_id in self._singleton_services:
            if service_id in self._singleton_instances:
                return self._singleton_instances[service_id]

            deps = self._get_dependencies(self._singleton_services[service_id])

            instance = self._singleton_services[service_id](
                **{
                    dep_arg: self.get(dep_type)
                    for dep_arg, dep_type in deps.items()
                    if dep_arg not in ("self", "return")
                }
            )

            self._singleton_instances[service_id] = instance
            return instance

        if service_id in self._transient_services:
            deps = self._get_dependencies(self._transient_services[service_id])
            return self._transient_services[service_id](
                **{
                    dep_arg: self.get(dep_type)
                    for dep_arg, dep_type in deps.items()
                    if dep_arg not in ("self", "return")
                }
            )

        else:
            raise Exception(f"Service {service_id} not found")


class Benchmark:
    def __init__(self):
        self._setup_meta_di_container()
        self._setup_rodi_container()
        self._setup_dependency_injector_container()
        self._setup_simple_container()

        # Create singletons for Direct Creation
        self.config = Config()
        self.cache = Cache(self.config)
        self.http_client = HTTPClient(self.config)

    def _get_foo_service(self):
        return FooService(
            config=self.config,
            database=services.Database(self.config),
            cache=self.cache,
            http_client=self.http_client,
            bar_service=services.BarService(
                config=self.config,
                database=services.Database(self.config),
                cache=self.cache,
                http_client=self.http_client,
            ),
        )

    def _setup_meta_di_container(self):
        self.meta_di_container = (
            ContainerBuilder()
            .add_transient(FooService)
            .add_transient(BarService)
            .add_transient(Database)
            .add_singleton(Cache)
            .add_singleton(HTTPClient)
            .add_singleton(Config)
            .build()
        )

    def _setup_simple_container(self):
        self._simple_container = SimpleContaner(
            transient_services={FooService: FooService, BarService: BarService},
            singleton_services={
                Database: Database,
                Cache: Cache,
                HTTPClient: HTTPClient,
                Config: Config,
            },
        )

    def _setup_rodi_container(self):
        self.rodi_container = RodiContainer()
        self.rodi_container.register(FooService)
        self.rodi_container.register(BarService)
        self.rodi_container.register(Database)

        config_instance = Config()
        self.rodi_container.register(Config, instance=config_instance)
        self.rodi_container.register(Cache, instance=Cache(config_instance))
        self.rodi_container.register(HTTPClient, instance=HTTPClient(config_instance))

    def _setup_dependency_injector_container(self):
        class DependencyInjectorContainer(containers.DeclarativeContainer):
            config = providers.Singleton(
                Config,
            )
            cache = providers.Singleton(
                Cache,
                config=config,
            )
            http_client = providers.Singleton(
                HTTPClient,
                config=config,
            )
            database = providers.Factory(
                Database,
                config=config,
            )

            bar_service = providers.Factory(
                BarService,
                config=config,
                database=database,
                cache=cache,
                http_client=http_client,
            )
            foo_service = providers.Factory(
                FooService,
                config=config,
                database=database,
                cache=cache,
                http_client=http_client,
                bar_service=bar_service,
            )

        self.dependency_injector_container = DependencyInjectorContainer()

    def direct_create(self):
        return self._get_foo_service()

    def meta_di(self):
        return self.meta_di_container.get(FooService)

    def rodi(self):
        return self.rodi_container.resolve(FooService)

    def simple_container(self):
        self._simple_container.get(FooService)

    def dependency_injector(self):
        return self.dependency_injector_container.foo_service()


if __name__ == "__main__":
    b = Benchmark()

    N = 1_000_000
    CLOCK = time.perf_counter_ns

    print(
        "Direct (No Framework)",
        (timeit(b.direct_create, number=N, timer=CLOCK)) / N,
        "ns",
    )
    print(
        "MetaDI Container (Pure Python)",
        (timeit(b.meta_di, number=N, timer=CLOCK)) / N,
        "ns",
    )
    print(
        "Dependency Injector Container (Cython)",
        (timeit(b.dependency_injector, number=N, timer=CLOCK)) / N,
        "ns",
    )
    print(
        "Rodi Container (Pure Python)",
        (timeit(b.rodi, number=N, timer=CLOCK)) / N,
        "ns",
    )
