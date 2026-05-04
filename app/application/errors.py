from __future__ import annotations


class ApplicationError(Exception):
    """Base class for application-layer errors."""


class InvalidCredentialsError(ApplicationError):
    """Raised when user credentials are invalid."""


class InvalidTokenError(ApplicationError):
    """Raised when a token cannot be validated."""


class AuthUserNotFoundError(ApplicationError):
    """Raised when token subject does not resolve to a user."""


class EmailNotVerifiedError(ApplicationError):
    """Raised when user email is not verified yet."""


class EmailDeliveryError(ApplicationError):
    """Raised when a verification email cannot be delivered."""
