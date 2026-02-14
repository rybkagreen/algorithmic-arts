"""Auth service exceptions."""

from shared.exceptions import BaseApplicationException


class InvalidCredentialsError(BaseApplicationException):
    """Invalid credentials error."""
    def __init__(self, message: str = "Invalid credentials", code: int = 401):
        super().__init__(message, code)


class UserNotFoundError(BaseApplicationException):
    """User not found error."""
    def __init__(self, message: str = "User not found", code: int = 404):
        super().__init__(message, code)


class UserAlreadyExistsError(BaseApplicationException):
    """User already exists error."""
    def __init__(self, message: str = "User already exists", code: int = 409):
        super().__init__(message, code)


class EmailVerificationRequiredError(BaseApplicationException):
    """Email verification required error."""
    def __init__(self, message: str = "Email verification required", code: int = 403):
        super().__init__(message, code)


class RateLimitExceededError(BaseApplicationException):
    """Rate limit exceeded error."""
    def __init__(self, message: str = "Rate limit exceeded", code: int = 429):
        super().__init__(message, code)


class PasswordResetTokenExpiredError(BaseApplicationException):
    """Password reset token expired error."""
    def __init__(self, message: str = "Password reset token expired", code: int = 400):
        super().__init__(message, code)


class InvalidTokenError(BaseApplicationException):
    """Invalid token error."""
    def __init__(self, message: str = "Invalid token", code: int = 401):
        super().__init__(message, code)