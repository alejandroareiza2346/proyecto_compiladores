from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
from .ast_nodes import *


@dataclass
class IRInstr:
    op: str
    a1: Optional[str] = None
    a2: Optional[str] = None
    res: Optional[str] = None

    def __repr__(self) -> str:
        parts = [self.op]
        if self.a1 is not None: parts.append(str(self.a1))
        if self.a2 is not None: parts.append(str(self.a2))
        if self.res is not None: parts.append(str(self.res))
        return ' '.join(parts)


class IRGenerator:
    def __init__(self) -> None:
        self.temp_counter = 0
        self.label_counter = 0
        self.ir: List[IRInstr] = []

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self, base: str = 'L') -> str:
        self.label_counter += 1
        return f"{base}{self.label_counter}"

    def generate(self, program: Program) -> List[IRInstr]:
        self.ir = []
        for stmt in program.body:
            self._emit_stmt(stmt)
        self.ir.append(IRInstr('label', 'END'))
        return self.ir

    def _emit_stmt(self, stmt: Stmt) -> None:
        if isinstance(stmt, Read):
            self.ir.append(IRInstr('read', stmt.name))
        elif isinstance(stmt, Print):
            val = self._emit_expr(stmt.expr)
            self.ir.append(IRInstr('print', val))
        elif isinstance(stmt, Assign):
            val = self._emit_expr(stmt.expr)
            self.ir.append(IRInstr('assign', val, None, stmt.name))
        elif isinstance(stmt, IfElse):
            cond_val = self._emit_expr(stmt.cond)
            l_true = self.new_label('L')
            l_end = self.new_label('L')
            # if cond != 0 goto l_true else fallthrough to else
            self.ir.append(IRInstr('ifnz', cond_val, l_true))
            # else body
            for s in stmt.else_body:
                self._emit_stmt(s)
            self.ir.append(IRInstr('goto', l_end))
            # then body
            self.ir.append(IRInstr('label', l_true))
            for s in stmt.then_body:
                self._emit_stmt(s)
            self.ir.append(IRInstr('label', l_end))
        elif isinstance(stmt, While):
            l_start = self.new_label('L')
            l_body = self.new_label('L')
            l_end = self.new_label('L')
            self.ir.append(IRInstr('label', l_start))
            cond_val = self._emit_expr(stmt.cond)
            self.ir.append(IRInstr('ifnz', cond_val, l_body))
            self.ir.append(IRInstr('goto', l_end))
            self.ir.append(IRInstr('label', l_body))
            for s in stmt.body:
                self._emit_stmt(s)
            self.ir.append(IRInstr('goto', l_start))
            self.ir.append(IRInstr('label', l_end))
        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt)}")

    def _emit_expr(self, expr: Expr) -> str:
        if isinstance(expr, Number):
            t = self.new_temp()
            self.ir.append(IRInstr('assign', str(expr.value), None, t))
            return t
        if isinstance(expr, Var):
            return expr.name
        if isinstance(expr, UnaryOp):
            val = self._emit_expr(expr.expr)
            if expr.op == '-':
                t = self.new_temp()
                self.ir.append(IRInstr('uminus', val, None, t))
                return t
            raise RuntimeError(f"Unsupported unary operator {expr.op}")
        if isinstance(expr, BinaryOp):
            l = self._emit_expr(expr.left)
            r = self._emit_expr(expr.right)
            t = self.new_temp()
            self.ir.append(IRInstr(expr.op, l, r, t))
            return t
        raise RuntimeError(f"Unknown expression type: {type(expr)}")

#4. Generador de Código Intermedio (IR / TAC)

#· Traduce el AST a código intermedio en formato de tres direcciones (TAC).

#· Implementa el control de flujo mediante etiquetas (L1, L2, etc.) y temporales (t1, t2, ...).

#· Representa instrucciones de asignación, salto condicional, entrada y salida.

#· Opcional: aplica optimizaciones independientes de máquina como:

#o Constant folding (evaluación de expresiones constantes).

#o Dead code elimination (eliminación de código no utilizado).