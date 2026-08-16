# Optional AI Lab Integration

## 1. Design Philosophy
- AI is **strictly optional**. The core quantitative platform functions completely offline with deterministic algorithms without any API keys.
- AI is **advisory only**. AI assistants generate research hypotheses and suggest mutations.
- AI **cannot bypass** preflight validation, mutate validation thresholds, or fabricate performance metrics.

## 2. Supported Providers
- **OpenAI** (`GPT-4o`)
- **Anthropic** (`Claude 3.5 Sonnet`)
- **Google** (`Gemini 1.5 Pro`)

## 3. Secret Security
- Keys are encrypted at rest with AES-256 (`Fernet`).
- Frontends and API GET responses receive only safe non-revealing key hints (e.g. `sk-...a1b2`).
