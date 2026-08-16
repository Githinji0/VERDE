from typing import Any, Dict
from backend.app.config import settings


class PriorityEngine:
    """Manages the research generation resource allocation across PROVEN, EXPLORED, and NOVEL candidate streams."""

    def __init__(self):
        self.proven_ratio = settings.PROVEN_RATIO
        self.explored_ratio = settings.EXPLORED_RATIO
        self.novel_ratio = settings.NOVEL_RATIO

    def get_allocation_ratios(self) -> Dict[str, float]:
        """Returns normalized exploration ratios."""
        total = self.proven_ratio + self.explored_ratio + self.novel_ratio
        if total <= 0:
            return {"PROVEN": 0.70, "EXPLORED": 0.20, "NOVEL": 0.10}
        return {
            "PROVEN": round(self.proven_ratio / total, 3),
            "EXPLORED": round(self.explored_ratio / total, 3),
            "NOVEL": round(self.novel_ratio / total, 3)
        }

    def set_allocation_ratios(self, proven: float, explored: float, novel: float):
        """Updates allocation ratios."""
        self.proven_ratio = max(0.0, proven)
        self.explored_ratio = max(0.0, explored)
        self.novel_ratio = max(0.0, novel)


priority_engine = PriorityEngine()
