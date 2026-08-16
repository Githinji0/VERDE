# Debugging & Diagnostics Guide

## 1. Structured Log Taxonomy
Every event in VERDE records:
- `timestamp`: UTC ISO timestamp
- `severity`: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- `component`: `PREFLIGHT`, `BRAIN_AUTH`, `BRAIN_CLIENT`, `SIMULATION_ENGINE`, `RESEARCH_WORKER`
- `event`: e.g., `SIMULATION_PORTFOLIO_EMPTY`, `PREFLIGHT_REJECTED`
- `message`: Diagnostic description
- `metadata`: Redacted diagnostic parameters

## 2. Common Diagnostic Events
- `SIMULATION_PORTFOLIO_EMPTY`: Simulation completed on BRAIN, but produced zero positions across instruments. Indicates constant or uniform signal distribution.
- `PREFLIGHT_REJECTED`: Candidate violated temporal compatibility (e.g. short-window rolling averages on slow balance-sheet metrics) or duplicate check.
- `BRAIN_AUTH_INVALID_CREDENTIALS`: Authentication rejection from BRAIN API (401/403).
