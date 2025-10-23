class DomainError(Exception):
    """Base class for all domain-level errors."""


class ValidationError(DomainError):
    """Raised when validation rules are broken."""
