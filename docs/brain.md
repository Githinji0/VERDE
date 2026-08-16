# WorldQuant BRAIN Integration Guide

## 1. Authentication & Security
- The backend owns all BRAIN communications.
- Credentials and session cookies are encrypted with AES-256 (`AES-GCM` / `Fernet`).
- Logs redact passwords, cookies, and tokens automatically.
- `BRAIN_DEBUG=true` enables safe inspection of HTTP status codes and latency.

## 2. Simulation Payload Builder
All simulations pass through `backend/app/brain/payloads.py`:
- Enforces strict validation of `universe`, `region`, `delay`, `decay`, `neutralization`, `truncation`, and `pasteurization`.
- Rejects unlisted or unsupported parameters before hitting the remote API.

## 3. Simulation State Machine
States supported:
- `CREATED`, `PREFLIGHT`, `QUEUED`, `SUBMITTING`, `SUBMITTED`, `RUNNING`, `COMPLETE`, `PORTFOLIO_EMPTY`, `METRICS_AVAILABLE`, `METRICS_MISSING`, `TECHNICAL_FAILURE`, `EVALUATED`, `REJECTED`, `PARETO`, `CANDIDATE_READY`.

## 4. Technical vs. Alpha Failures
- If a simulation yields no trades or empty PnL, it is flagged as `TECHNICAL_FAILURE` with `portfolio_status = "EMPTY"`.
- Sharpe and Fitness are recorded as `null` (`N/A`), preserving the statistical integrity of true alpha scores.
