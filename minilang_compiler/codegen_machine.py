from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


OPCODES: Dict[str, int] = {
    'LOAD': 1,
    'STORE': 2,
    'ADD': 3,
    'SUB': 4,
    'MUL': 5,
    'DIV': 6,
    'JMP': 7,
    'JLT': 8,
    'JGT': 9,
    'JLE': 10,
    'JGE': 11,
    'JEQ': 12,
    'JNE': 13,
    'IN': 14,
    'OUT': 15,
    'HALT': 16,
}


@dataclass
class MachineProgram:
    code: List[int]                 # Flattened list [opcode, operand, opcode, operand, ...]
    sym_addrs: Dict[str, int]       # Memory address per symbol
    mem_init: Dict[int, int]        # Memory initialization values (for constants)
    labels: Dict[str, int]          # Label to instruction address mapping


class Assembler:
    def __init__(self) -> None:
        self.instructions: List[Tuple[str, Optional[str]]] = []
        self.labels: Dict[str, int] = {}
        self.syms: Set[str] = set()

    def assemble(self, asm_lines: List[str]) -> Tuple[List[Tuple[str, Optional[str]]], Dict[str, int], Set[str]]:
        pc = 0
        for raw in asm_lines:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if parts[0].upper() == 'LABEL':
                if len(parts) != 2:
                    raise ValueError(f"Invalid LABEL syntax: {line}")
                label = parts[1]
                self.labels[label] = pc
                continue
            op = parts[0].upper()
            operand = parts[1] if len(parts) > 1 else None
            if operand and not operand.replace('-', '').isdigit():
                # it's a symbol or label; collect symbol (we'll resolve labels later)
                if op in ('LOAD','STORE','ADD','SUB','MUL','DIV','IN','OUT'):
                    self.syms.add(operand)
            self.instructions.append((op, operand))
            pc += 1
        return self.instructions, self.labels, self.syms

    def link(self, instrs: List[Tuple[str, Optional[str]]], labels: Dict[str, int], syms: Set[str], const_values: Dict[str, int]) -> MachineProgram:
        # Allocate memory addresses for symbols (including const_*)
        sym_addrs: Dict[str, int] = {}
        mem_init: Dict[int, int] = {}
        # First, ensure const_* symbols are allocated with value
        all_syms = set(syms)
        all_syms.update(const_values.keys())
        addr = 0
        for s in sorted(all_syms):
            sym_addrs[s] = addr
            if s in const_values:
                mem_init[addr] = const_values[s]
            addr += 1
        # Now translate instructions to opcodes
        code_pairs: List[int] = []
        for op, operand in instrs:
            if op not in OPCODES:
                raise ValueError(f"Unknown opcode: {op}")
            opcode = OPCODES[op]
            # Resolve operand: label -> instruction address; symbol -> memory address; int -> int
            operand_value = -1
            if operand is not None:
                if operand in labels:
                    operand_value = labels[operand]
                elif operand in sym_addrs:
                    operand_value = sym_addrs[operand]
                elif operand.replace('-', '').isdigit():
                    operand_value = int(operand)
                else:
                    # It may be a label not yet known; treat as error
                    raise ValueError(f"Unknown operand symbol/label: {operand}")
            code_pairs.extend([opcode, operand_value])
        return MachineProgram(code_pairs, sym_addrs, mem_init, labels)
