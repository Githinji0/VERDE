import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Regex patterns for sensitive data redaction
SENSITIVE_PATTERNS = [
    (re.compile(r'(?i)(password|secret|token|authorization|api[_-]?key|cookie)["\']?\s*[:=]\s*["\']?([^"\'\s&,]+)'), r'\1: [REDACTED]'),
    (re.compile(r'(?i)Bearer\s+([A-Za-z0-9\-\._~\+\/]+=*)'), 'Bearer [REDACTED]'),
    (re.compile(r'(?i)Basic\s+([A-Za-z0-9\+\/]+=*)'), 'Basic [REDACTED]'),
]


def redact_sensitive_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    for pattern, repl in SENSITIVE_PATTERNS:
        text = pattern.sub(repl, text)
    return text


def redact_dict(data: Any) -> Any:
    if isinstance(data, dict):
        redacted = {}
        for k, v in data.items():
            k_lower = str(k).lower()
            if any(s in k_lower for s in ['password', 'secret', 'token', 'authorization', 'api_key', 'apikey', 'cookie']):
                redacted[k] = '[REDACTED]'
            else:
                redacted[k] = redact_dict(v)
        return redacted
    elif isinstance(data, list):
        return [redact_dict(item) for item in data]
    elif isinstance(data, str):
        return redact_sensitive_text(data)
    return data


class StructuredLogger:
    """Centralized structured logger for VERDE system events and research audits."""

    def __init__(self, name: str = "VERDE"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_event(
        self,
        event: str,
        severity: str = "INFO",
        component: str = "SYSTEM",
        candidate_id: Optional[str] = None,
        simulation_id: Optional[str] = None,
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        safe_meta = redact_dict(metadata or {})
        safe_message = redact_sensitive_text(message)

        log_entry = {
            "timestamp": timestamp,
            "severity": severity.upper(),
            "component": component.upper(),
            "event": event,
            "candidate_id": candidate_id,
            "simulation_id": simulation_id,
            "message": safe_message,
            "metadata": safe_meta
        }

        log_str = f"[{component}] {event} - {safe_message}"
        if candidate_id:
            log_str += f" (Candidate: {candidate_id})"
        if simulation_id:
            log_str += f" (Simulation: {simulation_id})"

        sev = severity.upper()
        if sev == "DEBUG":
            self.logger.debug(log_str)
        elif sev == "INFO":
            self.logger.info(log_str)
        elif sev == "WARNING":
            self.logger.warning(log_str)
        elif sev == "ERROR":
            self.logger.error(log_str)
        elif sev == "CRITICAL":
            self.logger.critical(log_str)
        else:
            self.logger.info(log_str)

        return log_entry


verde_logger = StructuredLogger("VERDE")
