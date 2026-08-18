from typing import Any, Dict, List, Optional
from backend.app.generation.field_registry import FIELD_REGISTRY
from backend.app.generation.operator_registry import OPERATOR_REGISTRY


class FieldIntelligenceEngine:
    """
    Field Intelligence Layer for VERDE Alpha Quality Engine V2.
    Provides metadata, empirical behavior profiling, field quality scoring (0-100),
    and intelligent field selection for research hypotheses instead of random sampling.
    """

    CATEGORIES = [
        "PRICE", "RETURN", "VOLUME", "VOLATILITY", "FUNDAMENTAL",
        "VALUATION", "GROWTH", "QUALITY", "PROFITABILITY", "LEVERAGE",
        "LIQUIDITY", "SENTIMENT", "TECHNICAL", "MOMENTUM", "RISK", "GROUP"
    ]

    def __init__(self):
        self._registry = FIELD_REGISTRY
        self._enriched_metadata = self._build_enriched_metadata()

    def _build_enriched_metadata(self) -> Dict[str, Dict[str, Any]]:
        enriched = {}
        for name, meta in self._registry.items():
            cat = meta.get("category", "PRICE").upper()
            temp = meta.get("temporal_behavior", "MEDIUM").upper()
            
            # Map default empirical stats
            coverage = meta.get("data_quality", 1.0)
            missing_ratio = round(1.0 - coverage, 4)
            zero_ratio = 0.05 if cat in ["VOLUME", "LIQUIDITY"] else 0.01
            cross_std = 0.35 if temp == "FAST" else (0.25 if temp == "MEDIUM" else 0.15)
            temp_std = 0.30 if temp == "FAST" else (0.20 if temp == "MEDIUM" else 0.10)

            # Compute Field Quality Score (0 - 100)
            # Weights: Coverage (20), Cross-sectional var (20), Temporal var (15), Stability (15), Compatibility (15), Historical (15)
            cov_score = min(20.0, coverage * 20.0)
            cs_score = min(20.0, cross_std * 50.0)
            temp_score = min(15.0, temp_std * 45.0)
            stab_score = max(0.0, 15.0 - (zero_ratio * 100.0) - (missing_ratio * 100.0))
            comp_score = min(15.0, len(meta.get("preferred_operators", [])) * 2.5)
            hist_score = 15.0 if coverage >= 0.95 else 10.0

            quality_score = round(cov_score + cs_score + temp_score + stab_score + comp_score + hist_score, 1)
            quality_score = max(10.0, min(100.0, quality_score))

            enriched[name] = {
                "field": name,
                "category": cat,
                "data_type": "CONTINUOUS",
                "temporal_behavior": temp,
                "expected_variation": "HIGH" if temp in ["FAST", "MEDIUM"] else "MODERATE",
                "lookback_profile": {
                    "short": temp in ["FAST", "MEDIUM"],
                    "medium": True,
                    "long": temp in ["SLOW", "MEDIUM"]
                },
                "compatible_operators": meta.get("preferred_operators", ["rank", "ts_mean"]),
                "discouraged_operators": meta.get("discouraged_operators", []),
                "coverage": coverage,
                "missing_ratio": missing_ratio,
                "zero_ratio": zero_ratio,
                "cross_sectional_std": cross_std,
                "temporal_std": temp_std,
                "quality_score": quality_score,
                "supported_families": meta.get("supported_families", [])
            }
        return enriched

    def get_field_profile(self, field_name: str) -> Optional[Dict[str, Any]]:
        """Returns metadata and quality score for a field."""
        return self._enriched_metadata.get(field_name)

    def get_ranked_fields_for_family(
        self,
        family_code: str,
        category: Optional[str] = None,
        min_quality_score: float = 50.0
    ) -> List[Dict[str, Any]]:
        """
        Ranks and filters fields for a specific alpha research family using Field Quality Score.
        Replaces random field selection.
        """
        candidates = []
        for name, profile in self._enriched_metadata.items():
            if profile["quality_score"] < min_quality_score:
                continue
            if family_code and family_code not in profile["supported_families"]:
                continue
            if category and profile["category"] != category.upper():
                continue
            candidates.append(profile)

        # Sort descending by Field Quality Score
        candidates.sort(key=lambda x: x["quality_score"], reverse=True)
        return candidates

    def calculate_field_quality_score(
        self,
        coverage: float = 1.0,
        cross_sectional_std: float = 0.3,
        temporal_std: float = 0.2,
        zero_ratio: float = 0.01,
        missing_ratio: float = 0.0,
        compatible_operator_count: int = 5
    ) -> float:
        """Calculates configurable Field Quality Score (0-100)."""
        cov_score = min(20.0, coverage * 20.0)
        cs_score = min(20.0, cross_sectional_std * 50.0)
        temp_score = min(15.0, temporal_std * 45.0)
        stab_score = max(0.0, 15.0 - (zero_ratio * 100.0) - (missing_ratio * 100.0))
        comp_score = min(15.0, compatible_operator_count * 2.5)
        hist_score = 15.0 if coverage >= 0.95 else 10.0

        total = round(cov_score + cs_score + temp_score + stab_score + comp_score + hist_score, 1)
        return max(10.0, min(100.0, total))


field_intelligence = FieldIntelligenceEngine()
