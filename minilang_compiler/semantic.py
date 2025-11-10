"""
================================================================================
Archivo: semantic.py
--------------------------------------------------------------------------------
Este módulo implementa el análisis semántico para el compilador MiniLang.
El análisis semántico verifica el uso correcto de variables, inicialización y
operadores, detectando posibles errores y generando advertencias educativas.


================================================================================

Estructura principal:
- SemanticAnalyzer: Clase que realiza el análisis semántico.
- SymbolTable: Tabla de símbolos para variables.
- SemanticResult: Resultado del análisis (tabla y advertencias).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
from .ast_nodes import *


# Excepción para errores semánticos
class SemanticError(Exception):
    pass


# Información de cada símbolo (variable)
@dataclass
class SymbolInfo:
    name: str
    initialized: bool = False


# Tabla de símbolos: gestiona declaración e inicialización de variables
@dataclass
class SymbolTable:
    symbols: Dict[str, SymbolInfo] = field(default_factory=dict)

    def declare(self, name: str) -> None:
        """
        Declara una variable en la tabla de símbolos si no existe.
        """
        if name not in self.symbols:
            self.symbols[name] = SymbolInfo(name=name, initialized=False)

    def set_initialized(self, name: str) -> None:
        """
        Marca una variable como inicializada.
        """
        self.declare(name)
        self.symbols[name].initialized = True

    def is_initialized(self, name: str) -> bool:
        """
        Verifica si una variable está inicializada.
        """
        return self.symbols.get(name, SymbolInfo(name)).initialized


# Resultado del análisis semántico: tabla y advertencias
@dataclass
class SemanticResult:
    table: SymbolTable
    warnings: List[str]


# Analizador semántico principal
class SemanticAnalyzer:
    def __init__(self) -> None:
        self.table = SymbolTable()
        self.warnings: List[str] = []

    def analyze(self, program: Program) -> SemanticResult:
        """
        Analiza el programa completo (AST).
        Verifica inicialización de variables y uso correcto de operadores.
        """
        init: Set[str] = set()
        init = self._analyze_block(program.body, init, allow_init_out=True)
        # Actualiza la tabla de símbolos con las variables inicializadas
        for name in init:
            self.table.set_initialized(name)
        return SemanticResult(self.table, self.warnings)

    def _analyze_block(self, body: List[Stmt], in_init: Set[str], allow_init_out: bool) -> Set[str]:
        """
        Analiza un bloque de sentencias, propagando el estado de inicialización.
        """
        current = set(in_init)
        for stmt in body:
            current = self._analyze_stmt(stmt, current)
        return current if allow_init_out else in_init

    def _analyze_stmt(self, stmt: Stmt, init: Set[str]) -> Set[str]:
        """
        Analiza una sentencia individual y actualiza el estado de inicialización.
        """
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
            # No propaga inicialización fuera del while (puede no ejecutarse)
            _ = self._analyze_block(stmt.body, set(init), allow_init_out=True)
            return init
        raise SemanticError(f"Unknown statement type: {type(stmt)}")

    def _check_expr(self, expr: Expr, init: Set[str]) -> None:
        """
        Verifica una expresión: inicialización y operadores válidos.
        """
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
# FIN DEL ARCHIVO
