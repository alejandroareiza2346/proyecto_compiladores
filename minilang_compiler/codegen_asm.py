from __future__ import annotations
from typing import List, Set, Tuple
from .ir import IRInstr


class ASMGenerator:
    def __init__(self) -> None:
        self.lines: List[str] = []
        self.syms: Set[str] = set()
        self.consts: Set[int] = set()
        self.need_const0 = False
        self.need_const1 = False

    def _sym_for_const(self, v: int) -> str:
        self.consts.add(v)
        return f"const_{v}"

    def _use_sym(self, name: str | None) -> str:
        assert name is not None, "Internal error: symbol name is None"
        if name.replace('-', '').isdigit():
            return self._sym_for_const(int(name))
        self.syms.add(name)
        return name

    def _emit(self, line: str) -> None:
        self.lines.append(line)

    def generate(self, ir: List[IRInstr]) -> Tuple[List[str], Set[str], Set[int]]:
        # Map IR to assembly for an accumulator machine
        for ins in ir:
            op = ins.op
            if op == 'assign':
                src = self._use_sym(ins.a1)
                dst = self._use_sym(ins.res)
                self._emit(f"LOAD {src}")
                self._emit(f"STORE {dst}")
            elif op == 'uminus':
                val = self._use_sym(ins.a1)
                dst = self._use_sym(ins.res)
                # dst = 0 - val
                zero = self._sym_for_const(0)
                self._emit(f"LOAD {zero}")
                self._emit(f"SUB {val}")
                self._emit(f"STORE {dst}")
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
            elif op in ['==','!=','<','>','<=','>=']:
                l = self._use_sym(ins.a1)
                r = self._use_sym(ins.a2)
                dst = self._use_sym(ins.res)
                l_true = f"LBL_TRUE_{dst}"
                l_end = f"LBL_END_{dst}"
                self._emit(f"LOAD {l}")
                self._emit(f"SUB {r}")
                # ACC now is l - r
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
                # false -> 0
                zero = self._sym_for_const(0)
                one = self._sym_for_const(1)
                self._emit(f"LOAD {zero}")
                self._emit(f"STORE {dst}")
                self._emit(f"JMP {l_end}")
                # true -> 1
                self._emit(f"LABEL {l_true}")
                self._emit(f"LOAD {one}")
                self._emit(f"STORE {dst}")
                self._emit(f"LABEL {l_end}")
            elif op == 'ifnz':
                cond = self._use_sym(ins.a1)
                target = ins.a2
                self._emit(f"LOAD {cond}")
                self._emit(f"JNE {target}")
            elif op == 'goto':
                self._emit(f"JMP {ins.a1}")
            elif op == 'label':
                self._emit(f"LABEL {ins.a1}")
                if ins.a1 == 'END':
                    self._emit("HALT")
            elif op == 'read':
                var = self._use_sym(ins.a1)
                self._emit(f"IN {var}")
            elif op == 'print':
                src = self._use_sym(ins.a1)
                self._emit(f"OUT {src}")
            else:
                raise RuntimeError(f"Unsupported IR op: {op}")
        return self.lines, self.syms, self.consts
