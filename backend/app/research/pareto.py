from typing import Any, Dict, List, Optional


class ParetoFrontierEngine:
    """
    Computes multi-objective Pareto Frontier across Sharpe, Fitness, and Turnover.
    Candidate A dominates Candidate B if A is at least as good in all objectives
    and strictly better in at least one.
    Objectives:
      - Maximize Sharpe
      - Maximize Fitness
      - Minimize Turnover (or maximize -Turnover)
      - Maximize Margin
    """

    @staticmethod
    def dominates(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
        """Checks if candidate dictionary 'a' dominates candidate 'b'."""
        # Ensure valid metrics exist in both
        if a.get("sharpe") is None or a.get("fitness") is None:
            return False
        if b.get("sharpe") is None or b.get("fitness") is None:
            return True  # Valid candidate dominates invalid candidate

        s_a, s_b = a["sharpe"], b["sharpe"]
        f_a, f_b = a["fitness"], b["fitness"]
        t_a = a.get("turnover") or 0.5
        t_b = b.get("turnover") or 0.5
        m_a = a.get("margin_bps") or 0.0
        m_b = b.get("margin_bps") or 0.0

        # Conditions for dominance:
        # Sharpe: >=, Fitness: >=, Turnover: <=, Margin: >=
        at_least_as_good = (
            s_a >= s_b and
            f_a >= f_b and
            t_a <= t_b and
            m_a >= m_b
        )
        strictly_better = (
            s_a > s_b or
            f_a > f_b or
            t_a < t_b or
            m_a > m_b
        )

        return at_least_as_good and strictly_better

    @classmethod
    def compute_pareto_front(cls, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculates dominance count, dominated_by count, and pareto_optimal flag
        for a list of candidates.
        """
        n = len(candidates)
        results = []

        for i in range(n):
            cand_i = candidates[i]
            if cand_i.get("sharpe") is None or cand_i.get("fitness") is None:
                results.append({
                    "id": cand_i.get("id"),
                    "is_pareto_optimal": False,
                    "pareto_rank": 999,
                    "dominance_count": 0,
                    "dominated_by_count": 999
                })
                continue

            dominated_by = 0
            dominates_count = 0

            for j in range(n):
                if i == j:
                    continue
                cand_j = candidates[j]
                if cls.dominates(cand_j, cand_i):
                    dominated_by += 1
                elif cls.dominates(cand_i, cand_j):
                    dominates_count += 1

            is_optimal = (dominated_by == 0)
            pareto_rank = 1 if is_optimal else (1 + dominated_by)

            results.append({
                "id": cand_i.get("id"),
                "is_pareto_optimal": is_optimal,
                "pareto_rank": pareto_rank,
                "dominance_count": dominates_count,
                "dominated_by_count": dominated_by
            })

        return results

    @classmethod
    async def update_pareto_front_db(cls, session):
        """Asynchronously updates is_pareto and pareto_rank for all candidates with valid metrics."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from backend.app.database.models import AlphaCandidate, Simulation, SimulationMetric

        stmt = select(AlphaCandidate).join(Simulation).join(SimulationMetric).where(
            SimulationMetric.has_valid_metrics == True
        ).options(
            selectinload(AlphaCandidate.simulations).selectinload(Simulation.metrics)
        )
        res = await session.execute(stmt)
        candidates = res.scalars().unique().all()
        if not candidates:
            return

        cand_dicts = []
        cand_map = {}
        for c in candidates:
            cand_map[c.id] = c
            latest_metric = None
            if c.simulations:
                for s in reversed(c.simulations):
                    if s.metrics and s.metrics.has_valid_metrics:
                        latest_metric = s.metrics
                        break
            if latest_metric:
                cand_dicts.append({
                    "id": c.id,
                    "sharpe": latest_metric.sharpe,
                    "fitness": latest_metric.fitness,
                    "turnover": latest_metric.turnover,
                    "margin_bps": latest_metric.margin_bps
                })

        pareto_results = cls.compute_pareto_front(cand_dicts)
        for r in pareto_results:
            c = cand_map.get(r["id"])
            if c:
                c.is_pareto = r["is_pareto_optimal"]
                c.pareto_rank = r["pareto_rank"]


pareto_engine = ParetoFrontierEngine()
