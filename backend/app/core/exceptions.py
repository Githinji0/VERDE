from typing import Any, Dict, Optional


class VerdeException(Exception):
    """Base exception for all VERDE system errors."""

    def __init__(self, message: str, code: str = "VERDE_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class BrainAuthException(VerdeException):
    """Raised when WorldQuant BRAIN authentication fails."""

    def __init__(self, message: str, code: str = "BRAIN_AUTH_FAILURE", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class BrainPayloadException(VerdeException):
    """Raised when simulation payload validation fails."""

    def __init__(self, message: str, code: str = "PAYLOAD_VALIDATION_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class BrainSimulationException(VerdeException):
    """Raised when simulation submission or remote execution fails."""

    def __init__(self, message: str, code: str = "SIMULATION_FAILED", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class PreflightException(VerdeException):
    """Raised during pre-simulation preflight validation failure."""

    def __init__(self, message: str, code: str = "PREFLIGHT_REJECTED", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class AIProviderException(VerdeException):
    """Raised when external AI provider validation or generation fails."""

    def __init__(self, message: str, code: str = "AI_PROVIDER_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)
