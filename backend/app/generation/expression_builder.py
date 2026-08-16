import math
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Set, Union
from backend.app.generation.field_registry import get_field_metadata
from backend.app.generation.operator_registry import get_operator_metadata


class ASTNode(ABC):
    """Abstract base class for all Alpha Expression AST nodes."""

    @abstractmethod
    def to_code(self) -> str:
        """Compile AST node into valid WorldQuant BRAIN FastExpr code."""
        pass

    @abstractmethod
    def get_fields(self) -> Set[str]:
        """Extract all referenced field names."""
        pass

    @abstractmethod
    def get_operators(self) -> Set[str]:
        """Extract all referenced operator names."""
        pass

    @abstractmethod
    def get_depth(self) -> int:
        """Compute maximum tree depth."""
        pass

    @abstractmethod
    def calculate_complexity(self) -> float:
        """Compute structural complexity score."""
        pass


class FieldNode(ASTNode):
    """Represents a data field (e.g., 'close', 'capex', 'volume')."""

    def __init__(self, name: str):
        self.name = name.lower().strip()

    def to_code(self) -> str:
        return self.name

    def get_fields(self) -> Set[str]:
        return {self.name}

    def get_operators(self) -> Set[str]:
        return set()

    def get_depth(self) -> int:
        return 1

    def calculate_complexity(self) -> float:
        return 1.0


class ConstantNode(ASTNode):
    """Represents a numeric constant (e.g., 0.5, 20, 1.0)."""

    def __init__(self, value: Union[int, float]):
        self.value = value

    def to_code(self) -> str:
        return str(self.value)

    def get_fields(self) -> Set[str]:
        return set()

    def get_operators(self) -> Set[str]:
        return set()

    def get_depth(self) -> int:
        return 1

    def calculate_complexity(self) -> float:
        return 0.5


class UnaryOpNode(ASTNode):
    """Represents unary operations (e.g., -x, log(x), abs(x), rank(x), zscore(x))."""

    def __init__(self, operator: str, operand: ASTNode):
        self.operator = operator.lower().strip()
        self.operand = operand

    def to_code(self) -> str:
        if self.operator == "-":
            return f"-({self.operand.to_code()})"
        return f"{self.operator}({self.operand.to_code()})"

    def get_fields(self) -> Set[str]:
        return self.operand.get_fields()

    def get_operators(self) -> Set[str]:
        return {self.operator}.union(self.operand.get_operators())

    def get_depth(self) -> int:
        return 1 + self.operand.get_depth()

    def calculate_complexity(self) -> float:
        op_meta = get_operator_metadata(self.operator)
        op_cost = op_meta["complexity_cost"] if op_meta else 1.0
        return op_cost + self.operand.calculate_complexity()


class BinaryOpNode(ASTNode):
    """Represents binary operations (e.g., x / y, x - y, x + y, max(x, y))."""

    def __init__(self, operator: str, left: ASTNode, right: ASTNode):
        self.operator = operator.lower().strip()
        self.left = left
        self.right = right

    def to_code(self) -> str:
        if self.operator in ("+", "-", "*", "/"):
            return f"({self.left.to_code()} {self.operator} {self.right.to_code()})"
        return f"{self.operator}({self.left.to_code()}, {self.right.to_code()})"

    def get_fields(self) -> Set[str]:
        return self.left.get_fields().union(self.right.get_fields())

    def get_operators(self) -> Set[str]:
        return {self.operator}.union(self.left.get_operators()).union(self.right.get_operators())

    def get_depth(self) -> int:
        return 1 + max(self.left.get_depth(), self.right.get_depth())

    def calculate_complexity(self) -> float:
        op_meta = get_operator_metadata(self.operator)
        op_cost = op_meta["complexity_cost"] if op_meta else 1.0
        return op_cost + self.left.calculate_complexity() + self.right.calculate_complexity()


class TimeSeriesOpNode(ASTNode):
    """Represents rolling time-series operators (e.g., ts_mean(x, 20), ts_delta(x, 5), ts_zscore(x, 10))."""

    def __init__(self, operator: str, operand: ASTNode, lookback: int):
        self.operator = operator.lower().strip()
        self.operand = operand
        self.lookback = lookback

    def to_code(self) -> str:
        return f"{self.operator}({self.operand.to_code()}, {self.lookback})"

    def get_fields(self) -> Set[str]:
        return self.operand.get_fields()

    def get_operators(self) -> Set[str]:
        return {self.operator}.union(self.operand.get_operators())

    def get_depth(self) -> int:
        return 1 + self.operand.get_depth()

    def calculate_complexity(self) -> float:
        op_meta = get_operator_metadata(self.operator)
        op_cost = op_meta["complexity_cost"] if op_meta else 1.2
        return op_cost + self.operand.calculate_complexity()


class GroupOpNode(ASTNode):
    """Represents grouping neutralization operations (e.g., group_neutralize(x, subindustry))."""

    def __init__(self, operator: str, operand: ASTNode, group: str = "subindustry"):
        self.operator = operator.lower().strip()
        self.operand = operand
        self.group = group.lower().strip()

    def to_code(self) -> str:
        return f"{self.operator}({self.operand.to_code()}, {self.group})"

    def get_fields(self) -> Set[str]:
        return self.operand.get_fields()

    def get_operators(self) -> Set[str]:
        return {self.operator}.union(self.operand.get_operators())

    def get_depth(self) -> int:
        return 1 + self.operand.get_depth()

    def calculate_complexity(self) -> float:
        op_meta = get_operator_metadata(self.operator)
        op_cost = op_meta["complexity_cost"] if op_meta else 1.5
        return op_cost + self.operand.calculate_complexity()


class SafeDivNode(ASTNode):
    """Safe division wrapper preventing zero-division anomalies: x / (y + 0.00001)."""

    def __init__(self, numerator: ASTNode, denominator: ASTNode, epsilon: float = 0.0001):
        self.numerator = numerator
        self.denominator = denominator
        self.epsilon = epsilon

    def to_code(self) -> str:
        return f"({self.numerator.to_code()} / ({self.denominator.to_code()} + {self.epsilon}))"

    def get_fields(self) -> Set[str]:
        return self.numerator.get_fields().union(self.denominator.get_fields())

    def get_operators(self) -> Set[str]:
        return {"divide", "add"}.union(self.numerator.get_operators()).union(self.denominator.get_operators())

    def get_depth(self) -> int:
        return 1 + max(self.numerator.get_depth(), self.denominator.get_depth())

    def calculate_complexity(self) -> float:
        return 1.5 + self.numerator.calculate_complexity() + self.denominator.calculate_complexity()
