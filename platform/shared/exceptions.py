"""Shared exception classes for all services."""

from typing import Optional


class BaseApplicationException(Exception):
    """Base application exception."""
    
    def __init__(self, message: str, code: int = 500, details: Optional[dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class DomainException(BaseApplicationException):
    """Domain layer exception."""
    pass


class InfrastructureException(BaseApplicationException):
    """Infrastructure layer exception."""
    pass


class ValidationException(BaseApplicationException):
    """Validation exception."""
    def __init__(self, message: str, field: str, code: int = 400, details: Optional[dict] = None):
        self.field = field
        super().__init__(message, code, details or {"field": field})


class NotFoundException(BaseApplicationException):
    """Resource not found exception."""
    def __init__(self, resource: str, identifier: str, code: int = 404):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, code)


class ConflictException(BaseApplicationException):
    """Conflict exception (e.g., duplicate resource)."""
    def __init__(self, message: str, code: int = 409):
        super().__init__(message, code)


class UnauthorizedException(BaseApplicationException):
    """Unauthorized access exception."""
    def __init__(self, message: str = "Unauthorized", code: int = 401):
        super().__init__(message, code)


class ForbiddenException(BaseApplicationException):
    """Forbidden access exception."""
    def __init__(self, message: str = "Forbidden", code: int = 403):
        super().__init__(message, code)


class RateLimitExceededException(BaseApplicationException):
    """Rate limit exceeded exception."""
    def __init__(self, message: str = "Rate limit exceeded", code: int = 429):
        super().__init__(message, code)