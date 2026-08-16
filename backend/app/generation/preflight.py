import re
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.config import settings
from backend.app.core.logging import verde_logger
from backend.app.database.models import AlphaCandidate
from backend.app.generation.field_registry import FIELD_REGISTRY, get_field_metadata
from backend.app.generation.operator_registry import OPERATOR_REGISTRY, get_operator_metadata
from backend.app.generation.similarity import compute_expression_hash, compute_structure_hash


class PreflightEngine:
    """
    Comprehensive Pre-Simulation Preflight Validation Engine.
    Intercepts constant-signal risks, temporal mismatches, invalid syntax,
    and structural duplicates before simulation resources are wasted.
    """

    @staticmethod
    def validate_syntax(expression: str) -> Tuple[bool, Optional[str]]:
        """Checks bracket balance and basic token validity."""
        if not expression or not expression.strip():
            return False, "Expression is empty."

        # Balance check for parentheses
        stack = []
        for char in expression:
            if char == '(':
                stack.append(char)
            elif char == ')':
                if not stack:
                    return False, "Mismatched closing parenthesis ')'"
                stack.pop()
        if stack:
            return False, "Unclosed open parenthesis '('"

        return True, None

    @staticmethod
    def extract_fields_and_operators(expression: str) -> Tuple[Set[str], Set[str]]:
        """Parses identifiers from expression string."""
        tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expression)
        fields = set()
        operators = set()

        for t in tokens:
            t_low = t.lower()
            if t_low in OPERATOR_REGISTRY:
                operators.add(t_low)
            elif t_low in FIELD_REGISTRY:
                fields.add(t_low)
            elif t_low in ("subindustry", "industry", "sector", "market"):
                pass  # Group identifier
            else:
                # Potential unlisted field
                fields.add(t_low)

        return fields, operators

    @classmethod
    def check_temporal_compatibility(cls, expression: str, fields: Set[str], operators: Set[str]) -> Tuple[float, List[str]]:
        """
        Evaluates compatibility between field temporal behaviors and operators/lookbacks.
        Identifies structural risks such as short-term rolling means on quarterly fundamentals.
        Returns (compatibility_score: 0.0-1.0, issues: list).
        """
        score = 1.0
        issues = []

        # Find time series patterns: ts_operator(field, lookback)
        ts_matches = re.findall(r'(ts_[a-zA-Z0-9_]+)\s*\(\s*([a-zA-Z0-9_]+)\s*,\s*(\d+)\s*\)', expression)
        for op, field_name, lookback_str in ts_matches:
            lookback = int(lookback_str)
            meta = get_field_metadata(field_name)
            
            if meta["temporal_behavior"] == "SLOW":
                if lookback < 20:
                    score -= 0.4
                    issues.append(f"High structural risk: Slow-moving fundamental '{field_name}' with short lookback {lookback}d in {op}.")
                elif lookback < 60:
                    score -= 0.2
                    issues.append(f"Moderate risk: Slow field '{field_name}' with lookback {lookback}d.")

            if op in meta.get("discouraged_operators", []):
                score -= 0.3
                issues.append(f"Operator '{op}' is discouraged for field '{field_name}'.")

        return max(0.0, min(1.0, round(score, 2))), issues

    @classmethod
    def check_constant_signal_risk(cls, expression: str) -> Tuple[float, List[str]]:
        """
        Detects structural patterns prone to constant signals and empty portfolios.
        Returns (risk_score: 0.0-1.0, warnings: list).
        """
        risk = 0.0
        warnings = []

        # Check for ratio of identical rolling windows
        if re.search(r'ts_mean\(([^,]+),\s*(\d+)\)\s*/\s*ts_mean\(\1,\s*\2\)', expression):
            risk = 1.0
            warnings.append("Expression divides rolling mean by itself, collapsing to constant 1.0.")

        # Check for excessive sign() operations
        if expression.count("sign(") >= 2:
            risk += 0.4
            warnings.append("Multiple sign() operators risk collapsing signal into discrete low-variation buckets.")

        # Check for subindustry neutralization on very slow moving fields with small universe
        if "group_neutralize" in expression and "capex" in expression and "ts_mean" in expression:
            if "subindustry" in expression:
                risk += 0.3
                warnings.append("Subindustry neutralization on rolling capex may produce empty portfolios due to flat cross-sectional variance.")

        return min(1.0, round(risk, 2)), warnings

    @classmethod
    async def run_preflight(
        cls,
        expression: str,
        family_code: str,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Executes full preflight pipeline on candidate expression.
        Returns comprehensive preflight result dictionary.
        """
        expr_clean = expression.strip()
        
        # 1. Syntax Validation
        is_valid_syntax, syntax_err = cls.validate_syntax(expr_clean)
        if not is_valid_syntax:
            verde_logger.log_event(
                event="PREFLIGHT_REJECTED",
                severity="WARNING",
                component="PREFLIGHT",
                message=f"Syntax error: {syntax_err}",
                metadata={"expression": expr_clean}
            )
            return {
                "decision": "REJECT",
                "reason": "SYNTAX_ERROR",
                "compatibility_score": 0.0,
                "constant_signal_risk": 1.0,
                "complexity_score": 1.0,
                "diagnostic_details": {"syntax_error": syntax_err}
            }

        # 2. Extract AST components
        fields, operators = cls.extract_fields_and_operators(expr_clean)

        # 3. Temporal Compatibility
        compat_score, compat_issues = cls.check_temporal_compatibility(expr_clean, fields, operators)

        # 4. Constant Signal Risk
        const_risk, const_warnings = cls.check_constant_signal_risk(expr_clean)

        # 5. Complexity Estimation
        complexity_score = round(1.0 + len(operators) * 0.8 + len(fields) * 0.5 + expr_clean.count("(") * 0.3, 2)

        # 6. Duplicate Detection (if DB session provided)
        expr_hash = compute_expression_hash(expr_clean)
        struct_hash = compute_structure_hash(expr_clean)
        duplicate_risk = 0.0

        if session:
            dup_stmt = select(AlphaCandidate).where(AlphaCandidate.expression_hash == expr_hash)
            dup_res = await session.execute(dup_stmt)
            if dup_res.scalars().first():
                duplicate_risk = 1.0

        # 7. Final Decision Routing
        if duplicate_risk >= 1.0:
            decision = "REJECT"
            reason = "EXACT_DUPLICATE"
        elif const_risk >= settings.PREFLIGHT_CONSTANT_TOLERANCE:
            decision = "REJECT"
            reason = "HIGH_CONSTANT_RISK"
        elif compat_score < 0.3:
            decision = "REJECT"
            reason = "TEMPORAL_INCOMPATIBILITY"
        elif const_risk >= 0.5 or compat_score < 0.6:
            decision = "REGENERATE"
            reason = "STRUCTURAL_WEAKNESS"
        else:
            decision = "PASS"
            reason = "PREFLIGHT_PASSED"

        result = {
            "decision": decision,
            "reason": reason,
            "compatibility_score": compat_score,
            "constant_signal_risk": const_risk,
            "complexity_score": complexity_score,
            "duplicate_risk": duplicate_risk,
            "fields_used": list(fields),
            "operators_used": list(operators),
            "diagnostic_details": {
                "compatibility_issues": compat_issues,
                "constant_warnings": const_warnings,
                "expression_hash": expr_hash,
                "structure_hash": struct_hash
            }
        }

        verde_logger.log_event(
            event=f"PREFLIGHT_{decision}",
            severity="INFO" if decision == "PASS" else "WARNING",
            component="PREFLIGHT",
            message=f"Preflight decision: {decision} ({reason})",
            metadata=result
        )

        return result


preflight_engine = PreflightEngine()
