# Meta DI - A DI Container for Python using meta-programming (source generation)

This is a DI Container for Python using meta-programming (source generation). Since we know the dependencies and their lifecycles when generating the source code, we can optimize the generated code to avoid unnecessary lookups and function calls, achieving very good performance.

## Installation

```bash
pip install meta-di
```

## Quickstart

```python
from meta_di import ContainerBuilder

class Config:
    USER: str = "admin"
    PASSWORD: str = "admin"

class AuthServiceProto:
    def authenticate(self, user: str, password: str) -> bool:
        """Returns true if user/password is valid"""
        ...

class FakeAuthService(AuthServiceProto):
    def __init__(self, config: Config):
        self._config = config

    def authenticate(self, user: str, password: str) -> bool:
        if self._config.USER == user and self._config.PASSWORD == password:
            return True
        return False

builder = ContainerBuilder()

# We register AuthServiceProto with transient, meaning that a new instance will be created every time it is requested
# We also specify that the provider for AuthServiceProto is FakeAuthService
builder.add_transient(AuthServiceProto, FakeAuthService)

# FakeAuthService has a dependency on Config, so we must register it as well
# We register Config as a singleton, meaning that the same instance will be returned every time it is requested
builder.add_singleton(Config)

# We build the container
container = builder.build()

# We can now request AuthServiceProto from the container
# The container will create a new instance of FakeAuthService and inject it with the singleton instance of Config
auth_service = container.get(AuthServiceProto)
auth_service2 = container.get(AuthServiceProto)

assert isinstance(auth_service, FakeAuthService)
assert auth_service is not auth_service2 # Auth service is transient, so we get a new instance every time
assert auth_service._config is auth_service2._config # Config is singleton, so we get the same instance every time
assert auth_service.authenticate("admin", "admin") is True
```

## Other features

### Scoped lifetime

```python
from meta_di import ContainerBuilder

class Service:
    pass

container = ContainerBuilder().add_scoped(Service).build()

with container as scoped_container:
    service1 = scoped_container.get(Service)
    service2 = scoped_container.get(Service)
    # Scoped lifetime, so we get the same instance within the scope
    assert service1 is service2 

# Alterntively, we can create a scope with create_scope()
scoped_container = container.create_scope()
service3 = scoped_container.get(Service)
service4 = scoped_container.get(Service)

# Scoped lifetime, so we get the same instance within the scope
assert service3 is service4
# Different scopes, so we get different instances
assert service1 is not service3
```

### Function providers

```python
from meta_di import ContainerBuilder, ContainerProto

class Dependency:
    pass

class Service:
    def __init__(self, dependency: Dependency, value: str):
        self.dependency = dependency
        self.value = value

# We can use this function to provide Service
# container will be injected by the container (as itself)
def service_provider(container: ContainerProto):
    return Service(
        dependency=container.get(Dependency),
        value="from function provider",
    )

# Alternatively, we could write the function this way
# Dependency will be injected by the container
def service_provider(dependency: Dependency):
    return Service(
        dependency=dependency,
        value="from function provider",
    )

container = ContainerBuilder().add_transient(Dependency).add_transient(Service, service_provider).build()
assert container.get(Service).value == "from function provider"
```

### Building Container class or getting the generated source code

```python
from meta_di import ContainerBuilder

class Service:
    pass

builder = ContainerBuilder().add_singleton(Service)

# This will return the generated source code for the Container class
# You can use this to inspect the generated code or save it to a file
source_code = builder.get_code()

# This will generate the Container class and return it
ContainerClass = builder.build_class()
# You can use this class to create any number of container instances
container = ContainerClass()
container2 = ContainerClass()

# NOTE, each container instance will have its own singleton instances
assert container.get(Service) is not container2.get(Service)
```