import hashlib
import re
from typing import Set


def normalize_expression_text(expr: str) -> str:
    """Removes non-essential whitespace and normalizes case."""
    expr = expr.lower().strip()
    # Collapse multiple whitespaces
    expr = re.sub(r'\s+', '', expr)
    return expr


def compute_expression_hash(expr: str) -> str:
    """Computes exact SHA-256 hash of normalized expression string."""
    normalized = normalize_expression_text(expr)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_structure_hash(expr: str) -> str:
    """
    Computes structural hash by masking numbers and field identifiers to canonical tokens,
    allowing detection of structurally identical formulas.
    """
    s = normalize_expression_text(expr)
    # Replace numeric constants with $NUM
    s = re.sub(r'\b\d+(\.\d+)?\b', '$NUM', s)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def compute_field_overlap(fields_a: Set[str], fields_b: Set[str]) -> float:
    """Jaccard similarity between two sets of fields."""
    if not fields_a and not fields_b:
        return 1.0
    if not fields_a or not fields_b:
        return 0.0
    intersection = fields_a.intersection(fields_b)
    union = fields_a.union(fields_b)
    return len(intersection) / len(union)


def compute_operator_overlap(ops_a: Set[str], ops_b: Set[str]) -> float:
    """Jaccard similarity between two sets of operators."""
    if not ops_a and not ops_b:
        return 1.0
    if not ops_a or not ops_b:
        return 0.0
    intersection = ops_a.intersection(ops_b)
    union = ops_a.union(ops_b)
    return len(intersection) / len(union)
