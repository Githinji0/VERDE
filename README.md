# VERDE
### *Validation, Exploration & Research-driven Discovery Engine*
**WorldQuant BRAIN Alpha Research & Generation Platform**

---

## 1. Overview

**VERDE** is a professional quantitative alpha research, generation, preflight validation, simulation management, statistical evaluation, Pareto optimization, and adaptive research memory platform built specifically for WorldQuant BRAIN researchers.

The system's goal is to transform random formula guessing into disciplined, hypothesis-driven quantitative research:

$$\text{RESEARCH HYPOTHESIS} \longrightarrow \text{FIELD \& TEMPORAL INTELLIGENCE} \longrightarrow \text{PREFLIGHT VALIDATION} \longrightarrow \text{BRAIN SIMULATION} \longrightarrow \text{METRIC EXTRACTION} \longrightarrow \text{PARETO OPTIMIZATION} \longrightarrow \text{RESEARCH MEMORY}$$

---

## 2. Core Architectural Principles

1. **Strict Separation of Technical Failures vs. Alpha Failures**:
   - `PORTFOLIO_EMPTY` and missing metrics (`METRICS_MISSING`) are classified as `TECHNICAL_FAILURE` and never treated as Sharpe = 0 or Fitness = 0.
   - Missing metrics are displayed as `N/A` with explicit diagnostic causes.
2. **Multi-Stage Preflight Interception**:
   - Syntax, temporal incompatibility (e.g. quarterly capex with 5-day rolling operators), constant signal risk, and structural duplicates are intercepted before wasting BRAIN simulation quota.
3. **Multi-Objective Pareto Frontier**:
   - Tracks non-dominated candidates maximizing Sharpe and Fitness while minimizing Turnover and Margin.
4. **Persistent Research Memory**:
   - Continuously records empirical survival rates by family, field, and operator to adapt future generation weights.
5. **Vanilla Frontend**:
   - Pure HTML5, CSS3, and ES6+ JavaScript modules. Quicksand typography, White/Green visual identity, Lucide Icons, and ApexCharts.
6. **Optional & Safe AI Integration**:
   - AI assistant assists with hypothesis ideation and mutation tips, but can never alter thresholds or bypass deterministic preflight filters.

---

## 3. Technology Stack

- **Frontend**: Vanilla HTML5 / CSS3 / ES6+ JavaScript Modules (No React, Vue, or Angular)
- **UI & Visualization**: Quicksand Typography, Lucide Icons, ApexCharts
- **Backend API**: Python 3.12, FastAPI, Pydantic v2, Pydantic-Settings
- **Database Engine**: SQLAlchemy 2.0 (Async), SQLite (`verde.db`) local development fallback, PostgreSQL compatible
- **Security**: Cryptography (Fernet / AES-GCM) credential encryption, secret-redacting structured logging

---

## 4. Getting Started

### Prerequisites
- Python 3.10+
- Modern Web Browser (Chrome, Firefox, Safari, Edge)

### Installation
```bash
# 1. Clone repository
git clone https://github.com/Githinji0/VERDE.git
cd VERDE

# 2. Install dependencies
pip install -r requirements.txt

# 3. Environment configuration
cp .env.example .env

# 4. Start the VERDE platform
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at `http://127.0.0.1:8000` to access the VERDE Quantitative Research Dashboard.

---

## 5. Running Tests

```bash
python -m pytest
```

All 31+ unit and integration tests verify:
- Secret encryption and log redaction
- Payload schema validation and rejection of undocumented keys
- Response parser isolating empty portfolios from true alpha metrics
- AST compiler and safe division transformations
- Preflight temporal compatibility and constant-signal detectors
- Multi-objective Pareto dominance ranking
- Research memory empirical metric calculations
- Parameter robustness and walk-forward degradation analysis
