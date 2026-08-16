from typing import Any, Dict, List, Optional


def build_hypothesis_prompt(
    family_code: str,
    available_fields: List[str],
    memory_context: Optional[Dict[str, Any]] = None
) -> str:
    """Builds structured prompt containing domain context for AI hypothesis generation."""
    mem_str = ""
    if memory_context:
        mem_str = f"\nEmpirical Performance Context:\n- Best Fields: {memory_context.get('top_fields', [])}\n- High Empty Rate Fields: {memory_context.get('empty_fields', [])}\n"

    return f"""You are an expert quantitative researcher for WorldQuant BRAIN.
Generate 3 distinct, mathematically rigorous, and economically justifiable alpha research hypotheses for the '{family_code}' research family.

Available Fields:
{', '.join(available_fields)}
{mem_str}
Constraints:
- Must avoid constant-signal risks (e.g. dividing identical rolling windows).
- Must respect temporal frequencies (do not apply short rolling lookbacks to slow-moving quarterly balance sheet metrics).
- Propose concise AST-compatible expression structures with group neutralization where appropriate.

Return structured JSON format with 'title', 'rationale', 'suggested_fields', and 'suggested_operators'.
"""
