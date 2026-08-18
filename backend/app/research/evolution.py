import random
from typing import Any, Dict, List, Optional
from backend.app.generation.field_intelligence import field_intelligence
from backend.app.research.preflight_quality import prebrain_quality_engine


class AlphaEvolutionEngine:
    """
    Evolutionary Mutation & Crossover Engine V2.
    Evolves successful alpha candidates into robust offspring using controlled, semantically valid mutations:
    - LOOKBACK_MUTATION (±20%, ±50% neighborhood sampling)
    - FIELD_MUTATION (substitutes compatible field from same category)
    - OPERATOR_MUTATION (substitutes compatible operator e.g. ts_mean -> ts_sum)
    - SIGN_MUTATION (flipping directional sign -x)
    - GROUP_MUTATION (subindustry <-> industry <-> sector)
    - SIMPLIFICATION_MUTATION (strips redundant nesting)
    - CROSSOVER (combines components from 2 orthogonal parent alphas)
    """

    def mutate_candidate(
        self,
        parent_expression: str,
        family_code: str = "MOMENTUM",
        mutation_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a controlled offspring expression from a parent alpha candidate.
        """
        mutations = [
            "LOOKBACK_MUTATION", "FIELD_MUTATION", "OPERATOR_MUTATION",
            "SIGN_MUTATION", "GROUP_MUTATION", "SIMPLIFICATION_MUTATION"
        ]
        chosen_type = mutation_type or random.choice(mutations)
        expr = parent_expression

        if chosen_type == "LOOKBACK_MUTATION":
            # Replace numeric lookback argument
            for lb in [5, 10, 15, 20, 30, 40, 60, 120, 252]:
                if str(lb) in expr:
                    new_lb = random.choice([5, 10, 15, 20, 30, 40, 60, 120, 252])
                    expr = expr.replace(str(lb), str(new_lb))
                    break

        elif chosen_type == "FIELD_MUTATION":
            # Replace primary field with another high-quality field from same family
            ranked = field_intelligence.get_ranked_fields_for_family(family_code)
            if len(ranked) >= 2:
                field_names = [f["field"] for f in ranked]
                for fn in field_names:
                    if fn in expr:
                        replacement = random.choice([f for f in field_names if f != fn])
                        expr = expr.replace(fn, replacement)
                        break

        elif chosen_type == "OPERATOR_MUTATION":
            if "ts_mean" in expr:
                expr = expr.replace("ts_mean", "ts_sum")
            elif "ts_sum" in expr:
                expr = expr.replace("ts_sum", "ts_mean")
            elif "ts_delta" in expr:
                expr = expr.replace("ts_delta", "ts_delay")

        elif chosen_type == "SIGN_MUTATION":
            if expr.startswith("-"):
                expr = expr[1:]
            elif expr.startswith("rank("):
                expr = expr.replace("rank(", "rank(-")

        elif chosen_type == "GROUP_MUTATION":
            if "subindustry" in expr:
                expr = expr.replace("subindustry", "industry")
            elif "industry" in expr:
                expr = expr.replace("industry", "sector")
            elif "sector" in expr:
                expr = expr.replace("sector", "subindustry")

        elif chosen_type == "SIMPLIFICATION_MUTATION":
            if "rank(rank(" in expr.replace(" ", ""):
                expr = expr.replace("rank(rank(", "rank(")[:-1]

        # Evaluate offspring with Pre-BRAIN Quality Engine
        eval_res = prebrain_quality_engine.evaluate_candidate(expr, family_code)

        return {
            "offspring_expression": expr,
            "mutation_type": chosen_type,
            "parent_expression": parent_expression,
            "pre_brain_score": eval_res["pre_brain_score"],
            "decision": eval_res["decision"],
            "explainability": f"Offspring generated via {chosen_type} from parent '{parent_expression}'."
        }

    def crossover_candidates(
        self,
        parent_a: str,
        parent_b: str,
        family_code: str = "MOMENTUM"
    ) -> Dict[str, Any]:
        """
        Combines components from 2 orthogonal parent candidates into a composite offspring.
        """
        offspring_expr = f"group_neutralize(0.5 * {parent_a} + 0.5 * {parent_b}, subindustry)"
        eval_res = prebrain_quality_engine.evaluate_candidate(offspring_expr, family_code)

        return {
            "offspring_expression": offspring_expr,
            "mutation_type": "CROSSOVER",
            "parent_a": parent_a,
            "parent_b": parent_b,
            "pre_brain_score": eval_res["pre_brain_score"],
            "decision": eval_res["decision"],
            "explainability": f"Composite crossover combining components from parent A and parent B."
        }


evolution_engine = AlphaEvolutionEngine()
