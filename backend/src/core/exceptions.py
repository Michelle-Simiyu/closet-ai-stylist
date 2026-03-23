class NotFoundError(Exception):
    def __init__(self, resource: str, resource_id: str = ""):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} not found: {resource_id}")


class ValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class AuthorizationError(Exception):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message)


class AIServiceError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
