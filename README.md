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
# We register Config as a singleton, meaning that the same instance will be returned every time it is requested
builder.add_singleton(Config)

# We register AuthServiceProto as a transient, meaning that a new instance will be created every time it is requested
# We also specify that the provider for AuthServiceProto is FakeAuthService
builder.add_transient(AuthServiceProto, FakeAuthService)

# We build the container
container = builder.build()

auth_service = container.get(AuthServiceProto)
auth_service2 = container.get(AuthServiceProto)

assert auth_service is not auth_service2 # Different instances
assert auth_service._config is auth_service2._config # Same instance

assert auth_service.authenticate("admin", "admin") is True

# Alternatively you can build the container class
# This will generate a class that you can instantiate and use as a container
Container = builder.build_class()
container = Container()
container2 = Container()

assert container is not container2 # Different instances

# You can also simply get the code for the container class and use it as you wish
code = builder.get_code()
print(code)
```
