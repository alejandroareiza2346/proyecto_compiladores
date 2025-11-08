from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


@dataclass
class VMResult:
    outputs: List[int]
    trace: List[dict] | None = None


class VM:
    def __init__(self, code: List[int], memory_size: int, mem_init: Dict[int, int], input_provider: Optional[Callable[[], int]] = None, trace: bool = False) -> None:
        # code is flattened [opcode, operand, ...]
        self.code = code
        self.pc = 0
        self.acc = 0
        self.mem = [0] * max(memory_size, 1)
        for addr, val in mem_init.items():
            if 0 <= addr < len(self.mem):
                self.mem[addr] = val
        self.outputs: List[int] = []
        self.trace_enabled = trace
        self.trace: List[dict] | None = [] if trace else None
        self.input_provider = input_provider if input_provider else self._stdin_input

    def _stdin_input(self) -> int:
        return int(input().strip())

    def run(self) -> VMResult:
        while self.pc < len(self.code):
            op = self.code[self.pc]
            arg = self.code[self.pc + 1] if self.pc + 1 < len(self.code) else -1
            self.pc += 2
            if op == 1:       # LOAD
                self.acc = self.mem[arg]
            elif op == 2:     # STORE
                self.mem[arg] = self.acc
            elif op == 3:     # ADD
                self.acc = self.acc + self.mem[arg]
            elif op == 4:     # SUB
                self.acc = self.acc - self.mem[arg]
            elif op == 5:     # MUL
                self.acc = self.acc * self.mem[arg]
            elif op == 6:     # DIV
                # integer division, handle div by zero
                if self.mem[arg] == 0:
                    raise ZeroDivisionError("Division by zero in VM")
                self.acc = int(self.acc / self.mem[arg])
            elif op == 7:     # JMP
                self.pc = arg * 2
            elif op == 8:     # JLT (acc < 0)
                if self.acc < 0:
                    self.pc = arg * 2
            elif op == 9:     # JGT (acc > 0)
                if self.acc > 0:
                    self.pc = arg * 2
            elif op == 10:    # JLE (acc <= 0)
                if self.acc <= 0:
                    self.pc = arg * 2
            elif op == 11:    # JGE (acc >= 0)
                if self.acc >= 0:
                    self.pc = arg * 2
            elif op == 12:    # JEQ (acc == 0)
                if self.acc == 0:
                    self.pc = arg * 2
            elif op == 13:    # JNE (acc != 0)
                if self.acc != 0:
                    self.pc = arg * 2
            elif op == 14:    # IN
                self.mem[arg] = self.input_provider()
            elif op == 15:    # OUT
                self.outputs.append(self.mem[arg])
            elif op == 16:    # HALT
                break
            else:
                raise ValueError(f"Unknown opcode {op} at pc={self.pc}")
            # collect trace after executing instruction
            if self.trace_enabled and self.trace is not None:
                # record small snapshot
                self.trace.append({
                    'pc': self.pc,
                    'op': op,
                    'arg': arg,
                    'acc': self.acc,
                    # only snapshot first 32 memory cells to avoid huge dumps
                    'mem': self.mem[:32],
                })
        return VMResult(self.outputs, self.trace)
