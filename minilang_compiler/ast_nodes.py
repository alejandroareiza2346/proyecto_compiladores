from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union


# Expressions
@dataclass
class Expr:
    pass

@dataclass
class Number(Expr):
    value: int

@dataclass
class Var(Expr):
    name: str

@dataclass
class UnaryOp(Expr):
    op: str  # '-'
    expr: Expr

@dataclass
class BinaryOp(Expr):
    left: Expr
    op: str   # '+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>='
    right: Expr


# Statements
@dataclass
class Stmt:
    pass

@dataclass
class Read(Stmt):
    name: str

@dataclass
class Print(Stmt):
    expr: Expr

@dataclass
class Assign(Stmt):
    name: str
    expr: Expr

@dataclass
class IfElse(Stmt):
    cond: Expr
    then_body: List[Stmt]
    else_body: List[Stmt]

@dataclass
class While(Stmt):
    cond: Expr
    body: List[Stmt]


# Program
@dataclass
class Program:
    body: List[Stmt]
