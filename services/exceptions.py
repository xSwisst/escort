"""
Domain-level exceptions for business rule violations.

These exceptions represent business logic errors that should be handled
at the API route level and returned as meaningful HTTP responses to clients.
"""


class DomainError(Exception):
    """Base exception for all domain-level business rule violations."""

    pass


class FormNotFoundError(DomainError):
    """Raised when a form is not found."""

    def __init__(self, form_code: str):
        self.form_code = form_code
        super().__init__(f"Form not found: {form_code}")


class FormUnavailableError(DomainError):
    """Raised when attempting to book a form that is not available."""

    def __init__(self, form_code: str, reason: str):
        self.form_code = form_code
        self.reason = reason
        super().__init__(f"Form {form_code} is unavailable: {reason}")


class ClientNotFoundError(DomainError):
    """Raised when a client is not found."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"Client not found: {user_id}")


class ClientBannedError(DomainError):
    """Raised when a banned client attempts an action."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"Client {user_id} is banned")


class AgreementNotAcceptedError(DomainError):
    """Raised when a client attempts an action without accepting the agreement."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"Client {user_id} has not accepted the agreement")


class OrderValidationError(DomainError):
    """Raised when order validation fails."""

    def __init__(self, message: str):
        super().__init__(f"Order validation failed: {message}")


class InsufficientBalanceError(DomainError):
    """Raised when a client doesn't have sufficient balance for an operation."""

    def __init__(self, user_id: int, required: int, available: int):
        self.user_id = user_id
        self.required = required
        self.available = available
        super().__init__(f"Insufficient balance: required {required}, available {available}")


class InvalidTimeSlotError(DomainError):
    """Raised when an invalid time slot is provided."""

    def __init__(self, message: str):
        super().__init__(f"Invalid time slot: {message}")
