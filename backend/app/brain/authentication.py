import time
from typing import Any, Dict, Optional, Tuple
import httpx
from backend.app.config import settings
from backend.app.core.logging import verde_logger
from backend.app.core.security import vault


class BrainAuthManager:
    """Manages authentication lifecycle and session credentials for WorldQuant BRAIN."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.BRAIN_API_BASE_URL).rstrip("/")

    async def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Attempts authentication with WorldQuant BRAIN API.
        Returns a structured diagnostic dict with status_code, session_cookies, and safe diagnostic status.
        """
        endpoint = f"{self.base_url}/authentication"
        start_time = time.time()
        
        verde_logger.log_event(
            event="BRAIN_AUTH_START",
            severity="INFO",
            component="BRAIN_AUTH",
            message=f"Initiating authentication test for user: {username[:3]}***"
        )

        try:
            async with httpx.AsyncClient(timeout=settings.BRAIN_TIMEOUT, follow_redirects=True) as client:
                # WorldQuant BRAIN uses HTTP Basic Auth or POST credentials on /authentication endpoint
                response = await client.post(
                    endpoint,
                    auth=(username, password),
                    json={"username": username, "password": password},
                    headers={"Accept": "application/json"}
                )
                latency = round((time.time() - start_time) * 1000, 2)

                if settings.BRAIN_DEBUG:
                    verde_logger.log_event(
                        event="BRAIN_AUTH_DEBUG",
                        severity="DEBUG",
                        component="BRAIN_AUTH",
                        message=f"POST {endpoint} -> Status: {response.status_code} ({latency}ms)",
                        metadata={"status_code": response.status_code, "latency_ms": latency}
                    )

                if response.status_code in (200, 201):
                    # Extract session cookies or authorization tokens
                    cookies = dict(response.cookies)
                    verde_logger.log_event(
                        event="BRAIN_AUTH_SUCCESS",
                        severity="INFO",
                        component="BRAIN_AUTH",
                        message="WorldQuant BRAIN authentication successful."
                    )
                    return {
                        "status": "BRAIN_AUTH_SUCCESS",
                        "status_code": response.status_code,
                        "cookies": cookies,
                        "raw_data": response.json() if response.headers.get("content-type", "").startswith("application/json") else {},
                        "latency_ms": latency
                    }
                elif response.status_code in (401, 403):
                    verde_logger.log_event(
                        event="BRAIN_AUTH_FAILURE",
                        severity="WARNING",
                        component="BRAIN_AUTH",
                        message=f"Invalid BRAIN credentials (Status {response.status_code})"
                    )
                    return {
                        "status": "BRAIN_AUTH_INVALID_CREDENTIALS" if response.status_code == 401 else "BRAIN_AUTH_FORBIDDEN",
                        "status_code": response.status_code,
                        "error_message": "Invalid email or password.",
                        "latency_ms": latency
                    }
                elif response.status_code == 429:
                    verde_logger.log_event(
                        event="BRAIN_AUTH_RATE_LIMITED",
                        severity="WARNING",
                        component="BRAIN_AUTH",
                        message="WorldQuant BRAIN authentication rate limit reached."
                    )
                    return {
                        "status": "BRAIN_AUTH_RATE_LIMITED",
                        "status_code": 429,
                        "error_message": "Rate limit exceeded. Please wait before retrying.",
                        "latency_ms": latency
                    }
                else:
                    return {
                        "status": "BRAIN_AUTH_NETWORK_ERROR",
                        "status_code": response.status_code,
                        "error_message": f"Unexpected BRAIN API status code: {response.status_code}",
                        "latency_ms": latency
                    }

        except httpx.TimeoutException:
            verde_logger.log_event(
                event="BRAIN_AUTH_TIMEOUT",
                severity="ERROR",
                component="BRAIN_AUTH",
                message="WorldQuant BRAIN API authentication request timed out."
            )
            return {
                "status": "BRAIN_AUTH_TIMEOUT",
                "status_code": 408,
                "error_message": "Authentication timed out. WorldQuant server did not respond in time.",
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }
        except Exception as e:
            verde_logger.log_event(
                event="BRAIN_NETWORK_ERROR",
                severity="ERROR",
                component="BRAIN_AUTH",
                message=f"Network error during BRAIN authentication: {str(e)}"
            )
            return {
                "status": "BRAIN_AUTH_NETWORK_ERROR",
                "status_code": 500,
                "error_message": f"Connection error: {str(e)}",
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }


brain_auth = BrainAuthManager()
