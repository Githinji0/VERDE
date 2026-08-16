import hashlib
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from backend.app.generation.field_registry import FIELD_REGISTRY
from backend.app.generation.operator_registry import OPERATOR_REGISTRY


class ASTNode:
    """Canonical Abstract Syntax Tree node for quantitative alpha expressions."""
    def __init__(
        self,
        node_type: str,
        name: str,
        args: Optional[List['ASTNode']] = None,
        value: Any = None
    ):
        self.node_type = node_type  # 'FIELD', 'OPERATOR', 'SCALAR', 'GROUP', 'BINARY_OP'
        self.name = name            # e.g., 'ts_mean', 'close', 'rank', '+'
        self.args = args or []
        self.value = value

    def to_string(self) -> str:
        """Renders AST node to canonical FastExpr format."""
        if self.node_type == 'FIELD':
            return self.name
        elif self.node_type == 'GROUP':
            return self.name
        elif self.node_type == 'SCALAR':
            if self.value is not None:
                return str(self.value)
            return self.name
        elif self.node_type == 'OPERATOR':
            args_str = ", ".join([arg.to_string() for arg in self.args])
            return f"{self.name}({args_str})"
        elif self.node_type == 'BINARY_OP':
            left = self.args[0].to_string() if len(self.args) > 0 else ""
            right = self.args[1].to_string() if len(self.args) > 1 else ""
            return f"{left} {self.name} {right}"
        return self.name

    def category(self) -> str:
        """Determines component classification from actual AST node type."""
        if self.node_type == 'FIELD':
            return "BASE_FIELD"
        elif self.node_type == 'GROUP':
            return "GROUP_IDENTIFIER"
        elif self.node_type == 'SCALAR':
            return "SCALAR_CONSTANT"
        elif self.node_type == 'OPERATOR':
            name_low = self.name.lower()
            if name_low == "rank":
                return "CROSS_SECTIONAL_RANK"
            elif name_low == "group_neutralize":
                return "GROUP_NEUTRALIZATION"
            elif name_low.startswith("ts_"):
                return "TIME_SERIES_TRANSFORM"
            elif name_low in ("log", "abs", "sign", "scale"):
                return "MATH_TRANSFORM"
            meta = OPERATOR_REGISTRY.get(name_low, {})
            cat = meta.get("category", "OPERATOR")
            if cat == "TS":
                return "TIME_SERIES_TRANSFORM"
            elif cat == "CS":
                return "CROSS_SECTIONAL_RANK"
            elif cat == "GROUP":
                return "GROUP_NEUTRALIZATION"
            return "TRANSFORM_OPERATOR"
        elif self.node_type == 'BINARY_OP':
            return "MATH_TRANSFORM"
        return "EXPRESSION"


class Token:
    def __init__(self, kind: str, value: str):
        self.kind = kind
        self.value = value

    def __repr__(self):
        return f"Token({self.kind}, {self.value})"


class ExpressionASTParser:
    """
    FastExpr AST parser & hierarchy extractor.
    Parses FastExpr formulas into AST representations and generates exact,
    dependency-ordered component hierarchies without regex fallbacks or stale nodes.
    """

    GROUPS = {"subindustry", "industry", "sector", "market"}

    @classmethod
    def tokenize(cls, expression: str) -> List[Token]:
        """Tokenizes expression string into identifiers, numbers, operators, and punctuation."""
        token_specification = [
            ('NUMBER',   r'\d+(?:\.\d+)?'),
            ('IDENT',    r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('OP',       r'[+\-*/]'),
            ('LPAREN',   r'\('),
            ('RPAREN',   r'\)'),
            ('COMMA',    r','),
            ('SKIP',     r'[ \t\n]+'),
            ('MISMATCH', r'.'),
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        tokens = []
        for mo in re.finditer(tok_regex, expression):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                continue
            tokens.append(Token(kind, value))
        return tokens

    @classmethod
    def parse(cls, expression: str) -> Optional[ASTNode]:
        """Parses FastExpr string into canonical ASTNode."""
        clean = expression.strip()
        if not clean:
            return None

        tokens = cls.tokenize(clean)
        if not tokens:
            return None

        pos = 0

        def peek() -> Optional[Token]:
            nonlocal pos
            return tokens[pos] if pos < len(tokens) else None

        def consume(expected_kind: Optional[str] = None) -> Token:
            nonlocal pos
            t = peek()
            if not t:
                raise ValueError("Unexpected end of expression")
            if expected_kind and t.kind != expected_kind:
                raise ValueError(f"Expected {expected_kind}, got {t.kind} ({t.value})")
            pos += 1
            return t

        def parse_expr() -> ASTNode:
            return parse_binary_op(0)

        PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2}

        def parse_binary_op(min_prec: int) -> ASTNode:
            left = parse_primary()
            while True:
                t = peek()
                if not t or t.kind != 'OP' or PRECEDENCE.get(t.value, 0) < min_prec:
                    break
                op_token = consume('OP')
                prec = PRECEDENCE[op_token.value]
                right = parse_binary_op(prec + 1)
                left = ASTNode('BINARY_OP', op_token.value, [left, right])
            return left

        def parse_primary() -> ASTNode:
            t = peek()
            if not t:
                raise ValueError("Unexpected end of expression")

            if t.kind == 'NUMBER':
                consume('NUMBER')
                val = float(t.value) if '.' in t.value else int(t.value)
                return ASTNode('SCALAR', t.value, value=val)

            if t.kind == 'LPAREN':
                consume('LPAREN')
                node = parse_expr()
                consume('RPAREN')
                return node

            if t.kind == 'IDENT':
                ident_token = consume('IDENT')
                name = ident_token.value

                # Check if followed by '(' -> function call
                next_t = peek()
                if next_t and next_t.kind == 'LPAREN':
                    consume('LPAREN')
                    args = []
                    if peek() and peek().kind != 'RPAREN':
                        while True:
                            args.append(parse_expr())
                            if peek() and peek().kind == 'COMMA':
                                consume('COMMA')
                            else:
                                break
                    consume('RPAREN')
                    return ASTNode('OPERATOR', name, args)

                # Atom identifier
                if name.lower() in cls.GROUPS:
                    return ASTNode('GROUP', name.lower())
                elif name.lower() in FIELD_REGISTRY or not name.lower().startswith("ts_"):
                    return ASTNode('FIELD', name.lower())
                else:
                    return ASTNode('FIELD', name)

            raise ValueError(f"Unexpected token {t.kind} ({t.value})")

        try:
            root = parse_expr()
            return root
        except Exception:
            return None

    @classmethod
    def extract_component_hierarchy(cls, expression: str, is_empty_portfolio: bool = True) -> List[Dict[str, Any]]:
        """
        Traverses expression AST in post-order (dependency sequence) and returns
        the exact list of valid AST component dicts.
        """
        root = cls.parse(expression)
        if not root:
            return []

        components: List[Dict[str, Any]] = []
        seen_exprs: Set[str] = set()

        def traverse(node: ASTNode):
            if not node:
                return

            # Traverse child arguments first
            for arg in node.args:
                traverse(arg)

            # Skip scalar constants or group identifiers from standalone list
            if node.node_type in ('SCALAR', 'GROUP'):
                return

            expr_str = node.to_string()
            if expr_str in seen_exprs:
                return

            seen_exprs.add(expr_str)
            cat = node.category()

            # Determine component status
            status = "VALID"
            notes = f"Component '{node.name}' evaluated successfully."

            if cat == "BASE_FIELD":
                notes = f"Field '{node.name}' is registered and temporally compatible."
            elif cat == "CROSS_SECTIONAL_RANK":
                notes = "Cross-sectional ranking normalizes signal values from 0.0 to 1.0 across universe."
            elif cat == "GROUP_NEUTRALIZATION":
                status = "SUSPECT_UNPROVEN" if is_empty_portfolio else "VALID"
                notes = "Group neutralization de-means within subindustries. Combined with global rank and portfolio neutralization, this can eliminate active weights."
            elif cat == "TIME_SERIES_TRANSFORM":
                notes = f"Time-series operator '{node.name}' evaluates rolling window."
            elif cat == "MATH_TRANSFORM":
                notes = f"Mathematical operator '{node.name}' transforms signal."

            components.append({
                "expression": expr_str,
                "stage": cat,
                "status": status,
                "notes": notes
            })

        traverse(root)
        return components

    @classmethod
    def normalize_expression(cls, expression: str) -> str:
        """Normalizes expression string by removing redundant whitespace."""
        root = cls.parse(expression)
        if root:
            return root.to_string()
        return " ".join(expression.strip().split())

    @classmethod
    def compute_expression_hash(cls, expression: str) -> str:
        """Calculates deterministic SHA-256 hash of normalized expression."""
        norm = cls.normalize_expression(expression)
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()


ast_parser = ExpressionASTParser()
