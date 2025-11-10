"""
================================================================================
Archivo: runtime_vm.py
--------------------------------------------------------------------------------
Este módulo implementa la Máquina Virtual (VM) para el compilador MiniLang.
La VM ejecuta el código máquina generado, simulando la arquitectura de un
procesador simple. Permite la ejecución, depuración y trazado de programas
compilados.

================================================================================

Estructura principal:
- VM: Clase que representa la máquina virtual.
- VMResult: Resultado de la ejecución (salidas y trazas).

Instrucciones soportadas:
LOAD, STORE, ADD, SUB, MUL, DIV, JMP, JLT, JGT, JLE, JGE, JEQ, JNE, IN, OUT, HALT
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

# Resultado de la ejecución de la VM: incluye salidas y traza opcional
@dataclass
class VMResult:
    outputs: List[int]
    trace: List[dict] | None = None

# Máquina Virtual para ejecutar código máquina generado por el compilador
class VM:
    def __init__(self, code: List[int], memory_size: int, mem_init: Dict[int, int], input_provider: Optional[Callable[[], int]] = None, trace: bool = False) -> None:
        """
        Inicializa la VM con el código, tamaño de memoria, valores iniciales y proveedor de entrada.
        - code: Lista de enteros [opcode, operand, ...]
        - memory_size: Cantidad de celdas de memoria
        - mem_init: Diccionario {direccion: valor} para inicializar memoria
        - input_provider: Función para leer entrada (por defecto stdin)
        - trace: Si es True, guarda la traza de ejecución
        """
        self.code = code
        self.pc = 0  # Program Counter
        self.acc = 0 # Acumulador
        self.mem = [0] * max(memory_size, 1)
        for addr, val in mem_init.items():
            if 0 <= addr < len(self.mem):
                self.mem[addr] = val
        self.outputs: List[int] = []
        self.trace_enabled = trace
        self.trace: List[dict] | None = [] if trace else None
        self.input_provider = input_provider if input_provider else self._stdin_input

    def _stdin_input(self) -> int:
        """
        Método por defecto para leer entrada desde el usuario (stdin).
        """
        return int(input().strip())

    def run(self) -> VMResult:
        """
        Ejecuta el programa cargado en la VM.
        Recorre el código máquina, interpreta cada instrucción y actualiza el estado.
        Devuelve un objeto VMResult con las salidas y la traza si está habilitada.
        """
        while self.pc < len(self.code):
            op = self.code[self.pc]
            arg = self.code[self.pc + 1] if self.pc + 1 < len(self.code) else -1
            self.pc += 2
            # Decodificación y ejecución de instrucciones
            if op == 1:       # LOAD: Carga valor de memoria en el acumulador
                self.acc = self.mem[arg]
            elif op == 2:     # STORE: Guarda acumulador en memoria
                self.mem[arg] = self.acc
            elif op == 3:     # ADD: Suma valor de memoria al acumulador
                self.acc = self.acc + self.mem[arg]
            elif op == 4:     # SUB: Resta valor de memoria al acumulador
                self.acc = self.acc - self.mem[arg]
            elif op == 5:     # MUL: Multiplica acumulador por valor de memoria
                self.acc = self.acc * self.mem[arg]
            elif op == 6:     # DIV: Divide acumulador por valor de memoria (entero)
                if self.mem[arg] == 0:
                    raise ZeroDivisionError("Division by zero in VM")
                self.acc = int(self.acc / self.mem[arg])
            elif op == 7:     # JMP: Salto incondicional
                self.pc = arg * 2
            elif op == 8:     # JLT: Salta si acc < 0
                if self.acc < 0:
                    self.pc = arg * 2
            elif op == 9:     # JGT: Salta si acc > 0
                if self.acc > 0:
                    self.pc = arg * 2
            elif op == 10:    # JLE: Salta si acc <= 0
                if self.acc <= 0:
                    self.pc = arg * 2
            elif op == 11:    # JGE: Salta si acc >= 0
                if self.acc >= 0:
                    self.pc = arg * 2
            elif op == 12:    # JEQ: Salta si acc == 0
                if self.acc == 0:
                    self.pc = arg * 2
            elif op == 13:    # JNE: Salta si acc != 0
                if self.acc != 0:
                    self.pc = arg * 2
            elif op == 14:    # IN: Lee entrada y la guarda en memoria
                self.mem[arg] = self.input_provider()
            elif op == 15:    # OUT: Agrega valor de memoria a salidas
                self.outputs.append(self.mem[arg])
            elif op == 16:    # HALT: Finaliza ejecución
                break
            else:
                raise ValueError(f"Unknown opcode {op} at pc={self.pc}")
            # Si la traza está habilitada, guarda el estado actual
            if self.trace_enabled and self.trace is not None:
                self.trace.append({
                    'pc': self.pc,
                    'op': op,
                    'arg': arg,
                    'acc': self.acc,
                    'mem': self.mem[:32], # Solo las primeras 32 celdas
                })
        return VMResult(self.outputs, self.trace)
# FIN DEL ARCHIVO
