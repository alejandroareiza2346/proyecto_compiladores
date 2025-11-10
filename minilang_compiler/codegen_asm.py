"""
================================================================================
Archivo: codegen_asm.py
--------------------------------------------------------------------------------
Este módulo implementa la generación de código ensamblador para una máquina
acumuladora, a partir de instrucciones intermedias (IR) del compilador MiniLang.

Su objetivo es traducir el código intermedio (TAC) a instrucciones de bajo nivel
que pueden ser ejecutadas por una máquina virtual simple.

================================================================================

Estructura principal:
- Clase ASMGenerator: Encapsula toda la lógica de traducción IR -> ASM.
- Métodos privados para gestión de símbolos y constantes.
- Método generate() que realiza la traducción principal.

Ejemplo de uso:
    asmgen = ASMGenerator()
    asm_lines, symbols, consts = asmgen.generate(ir_instructions)
    # asm_lines contiene el código ensamblador generado
"""

from __future__ import annotations
from typing import List, Set, Tuple
from .ir import IRInstr


class ASMGenerator:
    def __init__(self) -> None:
        # Lista de líneas de código ensamblador generado
        self.lines: List[str] = []
        # Conjunto de símbolos (variables temporales y nombres)
        self.syms: Set[str] = set()
        # Conjunto de constantes utilizadas
        self.consts: Set[int] = set()
        # Flags para saber si se usan las constantes 0 y 1
        self.need_const0 = False
        self.need_const1 = False

    def _sym_for_const(self, v: int) -> str:
        """
        Devuelve el nombre simbólico para una constante.
        Ejemplo: Si v=5, retorna 'const_5'.
        """
        self.consts.add(v)
        return f"const_{v}"

    def _use_sym(self, name: str | None) -> str:
        """
        Normaliza el uso de símbolos y constantes.
        Si el nombre es un número, lo trata como constante.
        Si es variable, la agrega al conjunto de símbolos.
        """
        assert name is not None, "Error interno: nombre de símbolo es None"
        if name.replace('-', '').isdigit():
            return self._sym_for_const(int(name))
        self.syms.add(name)
        return name

    def _emit(self, line: str) -> None:
        """
        Agrega una línea al código ensamblador generado.
        """
        self.lines.append(line)

    def generate(self, ir: List[IRInstr]) -> Tuple[List[str], Set[str], Set[int]]:
        """
        Traduce una lista de instrucciones IR a código ensamblador.
        Retorna:
            - Lista de líneas ASM
            - Conjunto de símbolos usados
            - Conjunto de constantes usadas
        """
        # Recorre cada instrucción IR y la traduce a ASM
        for ins in ir:
            op = ins.op
            # Asignación simple: dst = src
            if op == 'assign':
                src = self._use_sym(ins.a1)
                dst = self._use_sym(ins.res)
                self._emit(f"LOAD {src}")
                self._emit(f"STORE {dst}")
            # Negación unaria: dst = -val
            elif op == 'uminus':
                val = self._use_sym(ins.a1)
                dst = self._use_sym(ins.res)
                zero = self._sym_for_const(0)
                self._emit(f"LOAD {zero}")
                self._emit(f"SUB {val}")
                self._emit(f"STORE {dst}")
            # Operaciones aritméticas: +, -, *, /
            elif op in ['+','-','*','/']:
                l = self._use_sym(ins.a1)
                r = self._use_sym(ins.a2)
                dst = self._use_sym(ins.res)
                self._emit(f"LOAD {l}")
                if op == '+':
                    self._emit(f"ADD {r}")
                elif op == '-':
                    self._emit(f"SUB {r}")
                elif op == '*':
                    self._emit(f"MUL {r}")
                else:
                    self._emit(f"DIV {r}")
                self._emit(f"STORE {dst}")
            # Operaciones relacionales: ==, !=, <, >, <=, >=
            elif op in ['==','!=','<','>','<=','>=']:
                l = self._use_sym(ins.a1)
                r = self._use_sym(ins.a2)
                dst = self._use_sym(ins.res)
                l_true = f"LBL_TRUE_{dst}"
                l_end = f"LBL_END_{dst}"
                self._emit(f"LOAD {l}")
                self._emit(f"SUB {r}")
                # El acumulador ahora tiene l - r
                if op == '==':
                    self._emit(f"JEQ {l_true}")
                elif op == '!=':
                    self._emit(f"JNE {l_true}")
                elif op == '<':
                    self._emit(f"JLT {l_true}")
                elif op == '>':
                    self._emit(f"JGT {l_true}")
                elif op == '<=':
                    self._emit(f"JLE {l_true}")
                elif op == '>=':
                    self._emit(f"JGE {l_true}")
                # Si la condición es falsa, asigna 0
                zero = self._sym_for_const(0)
                one = self._sym_for_const(1)
                self._emit(f"LOAD {zero}")
                self._emit(f"STORE {dst}")
                self._emit(f"JMP {l_end}")
                # Si la condición es verdadera, asigna 1
                self._emit(f"LABEL {l_true}")
                self._emit(f"LOAD {one}")
                self._emit(f"STORE {dst}")
                self._emit(f"LABEL {l_end}")
            # Salto condicional: if cond != 0 goto target
            elif op == 'ifnz':
                cond = self._use_sym(ins.a1)
                target = ins.a2
                self._emit(f"LOAD {cond}")
                self._emit(f"JNE {target}")
            # Salto incondicional
            elif op == 'goto':
                self._emit(f"JMP {ins.a1}")
            # Definición de etiqueta
            elif op == 'label':
                self._emit(f"LABEL {ins.a1}")
                if ins.a1 == 'END':
                    self._emit("HALT")
            # Lectura de variable desde entrada
            elif op == 'read':
                var = self._use_sym(ins.a1)
                self._emit(f"IN {var}")
            # Impresión de variable
            elif op == 'print':
                src = self._use_sym(ins.a1)
                self._emit(f"OUT {src}")
            else:
                raise RuntimeError(f"Operación IR no soportada: {op}")
        return self.lines, self.syms, self.consts
# FIN DEL ARCHIVO
