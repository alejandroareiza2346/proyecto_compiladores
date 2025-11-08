from __future__ import annotations
from typing import List, Union
from .ast_nodes import *


def fold_constants_expr(expr: Expr) -> Expr:
    if isinstance(expr, Number) or isinstance(expr, Var):
        return expr
    if isinstance(expr, UnaryOp):
        inner = fold_constants_expr(expr.expr)
        if isinstance(inner, Number) and expr.op == '-':
            return Number(-inner.value)
        return UnaryOp(expr.op, inner)
    if isinstance(expr, BinaryOp):
        left = fold_constants_expr(expr.left)
        right = fold_constants_expr(expr.right)
        if isinstance(left, Number) and isinstance(right, Number):
            a, b = left.value, right.value
            if expr.op == '+': return Number(a + b)
            if expr.op == '-': return Number(a - b)
            if expr.op == '*': return Number(a * b)
            if expr.op == '/': return Number(a // b)  # integer division
            if expr.op == '==': return Number(1 if a == b else 0)
            if expr.op == '!=': return Number(1 if a != b else 0)
            if expr.op == '<': return Number(1 if a < b else 0)
            if expr.op == '>': return Number(1 if a > b else 0)
            if expr.op == '<=': return Number(1 if a <= b else 0)
            if expr.op == '>=': return Number(1 if a >= b else 0)
        return BinaryOp(left, expr.op, right)
    raise RuntimeError(f"Unknown expression type: {type(expr)}")


def fold_constants_prog(program: Program) -> Program:
    def fold_stmt(stmt: Stmt) -> Stmt:
        if isinstance(stmt, Read):
            return stmt
        if isinstance(stmt, Print):
            return Print(fold_constants_expr(stmt.expr))
        if isinstance(stmt, Assign):
            return Assign(stmt.name, fold_constants_expr(stmt.expr))
        if isinstance(stmt, IfElse):
            cond = fold_constants_expr(stmt.cond)
            then_body = [fold_stmt(s) for s in stmt.then_body]
            else_body = [fold_stmt(s) for s in stmt.else_body]
            # Optional: if condition is constant, select branch
            if isinstance(cond, Number):
                if cond.value != 0:
                    return Block(then_body)
                else:
                    return Block(else_body)
            return IfElse(cond, then_body, else_body)
        if isinstance(stmt, While):
            cond = fold_constants_expr(stmt.cond)
            body = [fold_stmt(s) for s in stmt.body]
            return While(cond, body)
        if isinstance(stmt, Block):
            return Block([fold_stmt(s) for s in stmt.stmts])
        return stmt

    # Introduce a simple Block node to allow branch selection
    @dataclass
    class Block(Stmt):
        stmts: List[Stmt]

    new_body: List[Stmt] = []
    for s in program.body:
        s2 = fold_stmt(s)
        if isinstance(s2, Block):
            new_body.extend(s2.stmts)
        else:
            new_body.append(s2)
    return Program(new_body)
