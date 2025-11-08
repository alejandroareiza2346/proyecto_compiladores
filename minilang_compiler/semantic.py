from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
from .ast_nodes import *


class SemanticError(Exception):
    pass


@dataclass
class SymbolInfo:
    name: str
    initialized: bool = False


@dataclass
class SymbolTable:
    symbols: Dict[str, SymbolInfo] = field(default_factory=dict)

    def declare(self, name: str) -> None:
        if name not in self.symbols:
            self.symbols[name] = SymbolInfo(name=name, initialized=False)

    def set_initialized(self, name: str) -> None:
        self.declare(name)
        self.symbols[name].initialized = True

    def is_initialized(self, name: str) -> bool:
        return self.symbols.get(name, SymbolInfo(name)).initialized


@dataclass
class SemanticResult:
    table: SymbolTable
    warnings: List[str]


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.table = SymbolTable()
        self.warnings: List[str] = []

    def analyze(self, program: Program) -> SemanticResult:
        init: Set[str] = set()
        init = self._analyze_block(program.body, init, allow_init_out=True)
        # Update table initialized flags
        for name in init:
            self.table.set_initialized(name)
        return SemanticResult(self.table, self.warnings)

    def _analyze_block(self, body: List[Stmt], in_init: Set[str], allow_init_out: bool) -> Set[str]:
        current = set(in_init)
        for stmt in body:
            current = self._analyze_stmt(stmt, current)
        return current if allow_init_out else in_init

    def _analyze_stmt(self, stmt: Stmt, init: Set[str]) -> Set[str]:
        if isinstance(stmt, Read):
            self.table.declare(stmt.name)
            init.add(stmt.name)
            return init
        if isinstance(stmt, Print):
            self._check_expr(stmt.expr, init)
            return init
        if isinstance(stmt, Assign):
            self._check_expr(stmt.expr, init)
            self.table.declare(stmt.name)
            init.add(stmt.name)
            return init
        if isinstance(stmt, IfElse):
            self._check_expr(stmt.cond, init)
            then_init = set(init)
            else_init = set(init)
            then_out = self._analyze_block(stmt.then_body, then_init, allow_init_out=True)
            else_out = self._analyze_block(stmt.else_body, else_init, allow_init_out=True)
            # Solo las variables inicializadas en AMBAS ramas están garantizadas después
            guaranteed = then_out.intersection(else_out)
            return guaranteed
        if isinstance(stmt, While):
            self._check_expr(stmt.cond, init)
            # No propago inits del while hacia afuera porque puede no ejecutarse nunca
            _ = self._analyze_block(stmt.body, set(init), allow_init_out=True)
            return init
        raise SemanticError(f"Unknown statement type: {type(stmt)}")

    def _check_expr(self, expr: Expr, init: Set[str]) -> None:
        if isinstance(expr, Number):
            return
        if isinstance(expr, Var):
            self.table.declare(expr.name)
            if expr.name not in init:
                self.warnings.append(f"Warning: variable '{expr.name}' may be used before initialization")
            return
        if isinstance(expr, UnaryOp):
            if expr.op != '-':
                raise SemanticError(f"Unsupported unary operator '{expr.op}'")
            self._check_expr(expr.expr, init)
            return
        if isinstance(expr, BinaryOp):
            if expr.op not in ['+','-','*','/','==','!=','<','>','<=','>=']:
                raise SemanticError(f"Unsupported binary operator '{expr.op}'")
            self._check_expr(expr.left, init)
            self._check_expr(expr.right, init)
            return
        raise SemanticError(f"Unknown expression type: {type(expr)}")
