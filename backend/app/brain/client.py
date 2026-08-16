import asyncio
import time
from typing import Any, Dict, Optional, Tuple
import httpx
from backend.app.brain.payloads import build_simulation_payload
from backend.app.config import settings
from backend.app.core.exceptions import BrainPayloadException, BrainSimulationException
from backend.app.core.logging import verde_logger


class BrainClient:
    """
    WorldQuant BRAIN HTTP API client with automatic session management,
    retries, rate limiting, and structured diagnostics.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.BRAIN_API_BASE_URL).rstrip("/")

    async def submit_simulation(
        self,
        expression: str,
        settings_dict: Optional[Dict[str, Any]] = None,
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Submits an alpha candidate simulation to WorldQuant BRAIN API.
        Validates payload using strict schema before sending.
        """
        # Build and validate payload
        payload = build_simulation_payload(expression, settings_dict)
        endpoint = f"{self.base_url}/simulations"

        req_headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if headers:
            req_headers.update(headers)

        start_time = time.time()
        verde_logger.log_event(
            event="SIMULATION_SUBMITTING",
            severity="INFO",
            component="BRAIN_CLIENT",
            message=f"Submitting simulation to BRAIN API: {endpoint}",
            metadata={"universe": payload["settings"]["universe"], "region": payload["settings"]["region"]}
        )

        for attempt in range(1, settings.BRAIN_MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.BRAIN_TIMEOUT, cookies=cookies) as client:
                    response = await client.post(endpoint, json=payload, headers=req_headers)
                    latency = round((time.time() - start_time) * 1000, 2)

                    if settings.BRAIN_DEBUG:
                        verde_logger.log_event(
                            event="BRAIN_SIM_DEBUG",
                            severity="DEBUG",
                            component="BRAIN_CLIENT",
                            message=f"POST {endpoint} -> {response.status_code} ({latency}ms)",
                            metadata={"status_code": response.status_code, "attempt": attempt}
                        )

                    if response.status_code in (200, 201, 202):
                        # Extract simulation location or ID
                        sim_id = None
                        location = response.headers.get("Location")
                        if location:
                            sim_id = location.strip("/").split("/")[-1]
                        
                        data = {}
                        if response.headers.get("content-type", "").startswith("application/json"):
                            data = response.json()
                            if not sim_id and "id" in data:
                                sim_id = data["id"]

                        verde_logger.log_event(
                            event="SIMULATION_SUBMITTED",
                            severity="INFO",
                            component="BRAIN_CLIENT",
                            message=f"Simulation submitted successfully with BRAIN ID: {sim_id}",
                            metadata={"brain_sim_id": sim_id, "status_code": response.status_code}
                        )

                        return {
                            "status": "SUBMITTED",
                            "brain_sim_id": sim_id,
                            "location": location,
                            "raw_response": data,
                            "status_code": response.status_code
                        }

                    elif response.status_code == 400:
                        err_json = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                        err_text = err_json.get("message") or response.text
                        verde_logger.log_event(
                            event="SIMULATION_PAYLOAD_ERROR",
                            severity="ERROR",
                            component="BRAIN_CLIENT",
                            message=f"BRAIN rejected payload with 400: {err_text}",
                            metadata={"status_code": 400, "error": err_text}
                        )
                        return {
                            "status": "SUBMISSION_ERROR",
                            "error_code": "API_ERROR_400",
                            "error_message": f"BRAIN rejected payload: {err_text}",
                            "raw_response": err_json,
                            "status_code": 400
                        }

                    elif response.status_code == 429:
                        wait_seconds = 2 ** attempt
                        verde_logger.log_event(
                            event="SIMULATION_RATE_LIMITED",
                            severity="WARNING",
                            component="BRAIN_CLIENT",
                            message=f"Rate limited by BRAIN (429). Retrying in {wait_seconds}s (Attempt {attempt}/{settings.BRAIN_MAX_RETRIES})"
                        )
                        if attempt < settings.BRAIN_MAX_RETRIES:
                            await asyncio.sleep(wait_seconds)
                            continue
                        return {
                            "status": "RATE_LIMITED",
                            "error_code": "API_ERROR_429",
                            "error_message": "Rate limit exceeded on BRAIN simulation endpoint.",
                            "status_code": 429
                        }

                    elif response.status_code in (401, 403):
                        verde_logger.log_event(
                            event="SIMULATION_AUTH_ERROR",
                            severity="ERROR",
                            component="BRAIN_CLIENT",
                            message=f"Authentication failed during simulation submission (Status {response.status_code})"
                        )
                        return {
                            "status": "TECHNICAL_FAILURE",
                            "error_code": f"AUTH_ERROR_{response.status_code}",
                            "error_message": "BRAIN session is unauthorized or expired.",
                            "status_code": response.status_code
                        }

                    else:
                        verde_logger.log_event(
                            event="SIMULATION_REMOTE_ERROR",
                            severity="ERROR",
                            component="BRAIN_CLIENT",
                            message=f"BRAIN returned error status {response.status_code}: {response.text[:200]}"
                        )
                        if attempt < settings.BRAIN_MAX_RETRIES and response.status_code >= 500:
                            await asyncio.sleep(1.5 * attempt)
                            continue
                        return {
                            "status": "TECHNICAL_FAILURE",
                            "error_code": f"REMOTE_ERROR_{response.status_code}",
                            "error_message": f"Server error from BRAIN API (Status {response.status_code})",
                            "status_code": response.status_code
                        }

            except httpx.TimeoutException:
                verde_logger.log_event(
                    event="SIMULATION_TIMEOUT",
                    severity="WARNING",
                    component="BRAIN_CLIENT",
                    message=f"Timeout on simulation submission (Attempt {attempt}/{settings.BRAIN_MAX_RETRIES})"
                )
                if attempt < settings.BRAIN_MAX_RETRIES:
                    await asyncio.sleep(1.5 * attempt)
                    continue
                return {
                    "status": "TIMEOUT",
                    "error_code": "NETWORK_TIMEOUT",
                    "error_message": "BRAIN simulation submission timed out.",
                    "status_code": 408
                }
            except Exception as e:
                verde_logger.log_event(
                    event="SIMULATION_NETWORK_ERROR",
                    severity="ERROR",
                    component="BRAIN_CLIENT",
                    message=f"Network error during simulation submission: {str(e)}"
                )
                return {
                    "status": "TECHNICAL_FAILURE",
                    "error_code": "NETWORK_ERROR",
                    "error_message": str(e),
                    "status_code": 500
                }

        return {
            "status": "TECHNICAL_FAILURE",
            "error_code": "MAX_RETRIES_EXCEEDED",
            "error_message": "Maximum retries exceeded during simulation submission."
        }

    async def poll_simulation_status(
        self,
        brain_sim_id: str,
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Polls the status of an ongoing simulation on WorldQuant BRAIN API.
        """
        endpoint = f"{self.base_url}/simulations/{brain_sim_id}"
        req_headers = {"Accept": "application/json"}
        if headers:
            req_headers.update(headers)

        try:
            async with httpx.AsyncClient(timeout=settings.BRAIN_TIMEOUT, cookies=cookies) as client:
                response = await client.get(endpoint, headers=req_headers)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "").upper()
                    # BRAIN status can be: PENDING, RUNNING, COMPLETE, ERROR, CANCELLED
                    return {
                        "status": status if status else "COMPLETE",
                        "data": data,
                        "status_code": 200
                    }
                elif response.status_code == 404:
                    return {
                        "status": "TECHNICAL_FAILURE",
                        "error_code": "SIM_NOT_FOUND",
                        "error_message": f"Simulation {brain_sim_id} not found on BRAIN.",
                        "status_code": 404
                    }
                else:
                    return {
                        "status": "TECHNICAL_FAILURE",
                        "error_code": f"POLL_ERROR_{response.status_code}",
                        "error_message": f"Poll failed with status {response.status_code}",
                        "status_code": response.status_code
                    }
        except Exception as e:
            return {
                "status": "TECHNICAL_FAILURE",
                "error_code": "POLL_EXCEPTION",
                "error_message": str(e),
                "status_code": 500
            }


brain_client = BrainClient()
