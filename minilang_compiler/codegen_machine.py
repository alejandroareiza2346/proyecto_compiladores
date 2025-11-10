"""
================================================================================
Archivo: codegen_machine.py
--------------------------------------------------------------------------------
Este módulo implementa la traducción de código ensamblador a código máquina
para una máquina virtual simple, utilizada en el compilador MiniLang.

Su objetivo es transformar instrucciones ensamblador (ASM) en una representación
numérica que puede ser ejecutada directamente por la máquina virtual.

================================================================================

Estructura principal:
- Diccionario OPCODES: Asocia cada instrucción ASM con su código numérico.
- Clase MachineProgram: Representa el programa máquina final (memoria, código, labels).
- Clase Assembler: Encapsula la lógica de ensamblado y vinculación.

Ejemplo de uso:
    assembler = Assembler()
    instrs, labels, syms = assembler.assemble(asm_lines)
    program = assembler.link(instrs, labels, syms, const_values)
    # program.code contiene el código máquina listo para ejecutar
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


# Diccionario que asocia cada instrucción ASM con su código numérico
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
    code: List[int]                 # Lista de enteros: [opcode, operando, ...]
    sym_addrs: Dict[str, int]       # Dirección de memoria por símbolo
    mem_init: Dict[int, int]        # Valores iniciales de memoria (constantes)
    labels: Dict[str, int]          # Mapeo de etiquetas a direcciones de instrucción


class Assembler:
    def __init__(self) -> None:
        # Lista de instrucciones ensamblador (op, operando)
        self.instructions: List[Tuple[str, Optional[str]]] = []
        # Mapeo de etiquetas a posición en el código
        self.labels: Dict[str, int] = {}
        # Conjunto de símbolos usados
        self.syms: Set[str] = set()

    def assemble(self, asm_lines: List[str]) -> Tuple[List[Tuple[str, Optional[str]]], Dict[str, int], Set[str]]:
        """
        Convierte líneas de ASM en tuplas (op, operando), detecta etiquetas y símbolos.
        Retorna:
            - Lista de instrucciones (op, operando)
            - Mapeo de etiquetas
            - Conjunto de símbolos
        """
        pc = 0  # Contador de programa (posición)
        for raw in asm_lines:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue  # Ignora líneas vacías o comentarios
            parts = line.split()
            if parts[0].upper() == 'LABEL':
                if len(parts) != 2:
                    raise ValueError(f"Sintaxis inválida de LABEL: {line}")
                label = parts[1]
                self.labels[label] = pc
                continue
            op = parts[0].upper()
            operand = parts[1] if len(parts) > 1 else None
            if operand and not operand.replace('-', '').isdigit():
                # Si es símbolo o etiqueta, lo agrega al conjunto
                if op in ('LOAD','STORE','ADD','SUB','MUL','DIV','IN','OUT'):
                    self.syms.add(operand)
            self.instructions.append((op, operand))
            pc += 1
        return self.instructions, self.labels, self.syms

    def link(self, instrs: List[Tuple[str, Optional[str]]], labels: Dict[str, int], syms: Set[str], const_values: Dict[str, int]) -> MachineProgram:
        """
        Asigna direcciones de memoria a símbolos y constantes, y traduce instrucciones
        ASM a código máquina (lista de enteros).
        Retorna un objeto MachineProgram listo para ejecutar.
        """
        # Asignación de direcciones de memoria
        sym_addrs: Dict[str, int] = {}
        mem_init: Dict[int, int] = {}
        # Incluye símbolos y constantes
        all_syms = set(syms)
        all_syms.update(const_values.keys())
        addr = 0
        for s in sorted(all_syms):
            sym_addrs[s] = addr
            if s in const_values:
                mem_init[addr] = const_values[s]
            addr += 1
        # Traducción de instrucciones a pares [opcode, operando]
        code_pairs: List[int] = []
        for op, operand in instrs:
            if op not in OPCODES:
                raise ValueError(f"Opcode desconocido: {op}")
            opcode = OPCODES[op]
            # Resolución de operandos: etiqueta, símbolo o entero
            operand_value = -1
            if operand is not None:
                if operand in labels:
                    operand_value = labels[operand]
                elif operand in sym_addrs:
                    operand_value = sym_addrs[operand]
                elif operand.replace('-', '').isdigit():
                    operand_value = int(operand)
                else:
                    raise ValueError(f"Operando desconocido: {operand}")
            code_pairs.extend([opcode, operand_value])
        return MachineProgram(code_pairs, sym_addrs, mem_init, labels)
# FIN DEL ARCHIVO
