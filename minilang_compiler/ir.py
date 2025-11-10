"""
================================================================================
Archivo: ir.py
--------------------------------------------------------------------------------
Este módulo implementa la generación de código intermedio (IR) para el compilador
MiniLang. El IR (Intermediate Representation) es una forma simplificada y lineal
del programa, que facilita la traducción a ensamblador y máquina.


================================================================================

Estructura principal:
- Clase IRInstr: Representa una instrucción intermedia (op, a1, a2, res).
- Clase IRGenerator: Encapsula la lógica para transformar el AST en IR.

Ejemplo de uso:
    irgen = IRGenerator()
    ir_instructions = irgen.generate(program_ast)
    # ir_instructions es una lista de instrucciones IR
"""

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
        # Representación legible de la instrucción IR
        parts = [self.op]
        if self.a1 is not None: parts.append(str(self.a1))
        if self.a2 is not None: parts.append(str(self.a2))
        if self.res is not None: parts.append(str(self.res))
        return ' '.join(parts)


class IRGenerator:
    def __init__(self) -> None:
        # Contadores para temporales y etiquetas
        self.temp_counter = 0
        self.label_counter = 0
        # Lista de instrucciones IR generadas
        self.ir: List[IRInstr] = []

    def new_temp(self) -> str:
        """
        Genera un nombre de variable temporal único (t1, t2, ...)
        """
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self, base: str = 'L') -> str:
        """
        Genera un nombre de etiqueta único (L1, L2, ...)
        """
        self.label_counter += 1
        return f"{base}{self.label_counter}"

    def generate(self, program: Program) -> List[IRInstr]:
        """
        Recibe el AST del programa y genera la lista de instrucciones IR.
        """
        self.ir = []
        for stmt in program.body:
            self._emit_stmt(stmt)
        # Marca el final del programa
        self.ir.append(IRInstr('label', 'END'))
        return self.ir

    def _emit_stmt(self, stmt: Stmt) -> None:
        """
        Traduce una sentencia del AST a instrucciones IR.
        """
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
            # if cond != 0 goto l_true else ejecuta else
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
            raise RuntimeError(f"Tipo de sentencia desconocido: {type(stmt)}")

    def _emit_expr(self, expr: Expr) -> str:
        """
        Traduce una expresión del AST a instrucciones IR y retorna el nombre del
        temporal donde queda el resultado.
        """
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
            raise RuntimeError(f"Operador unario no soportado {expr.op}")
        if isinstance(expr, BinaryOp):
            l = self._emit_expr(expr.left)
            r = self._emit_expr(expr.right)
            t = self.new_temp()
            self.ir.append(IRInstr(expr.op, l, r, t))
            return t
        raise RuntimeError(f"Tipo de expresión desconocido: {type(expr)}")
# FIN DEL ARCHIVO

