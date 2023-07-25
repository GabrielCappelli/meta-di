from typing import Any


class MetaDIException(Exception):
    pass


class MissingServiceError(MetaDIException):
    def __init__(self, service: Any):
        self.message = f"Missing service {service}"
        super().__init__(self.message)


class CannotInferProvider(MetaDIException):
    def __init__(self, service: Any):
        self.message = f"Cannot infer provider for service {service}"
        super().__init__(self.message)


class CannotReferenceError(MetaDIException):
    def __init__(self, service_or_provider: Any):
        self.message = f"Cannot create code reference for {service_or_provider}"
        super().__init__(self.message)
