# Preflight Validation Engine

The preflight engine intercepts flawed formulas locally before they consume BRAIN simulation quota.

## Validation Stages
1. **Syntax Integrity**: Verifies balanced parentheses and valid tokens.
2. **Field & Operator Registry Check**: Confirms operators and data fields exist and match arities.
3. **Temporal Compatibility Filter**: Flags slow-moving fundamental metrics (e.g. quarterly Capex) improperly paired with short-horizon rolling operators (`ts_mean(capex, 10)`).
4. **Constant Signal Risk Detector**: Identifies expressions that collapse cross-sectional variance (e.g., dividing identical rolling windows or excessive `sign()` calls).
5. **Exact & Structural Duplicate Detection**: Hashes canonical expressions to prevent redundant simulations.
6. **Complexity Estimation**: Penalizes deeply nested, overly convoluted AST expressions.
