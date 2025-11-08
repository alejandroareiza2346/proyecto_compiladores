from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import List

from .lexer import Lexer, LexError
from .tokens import Token
from .parser import Parser, ParseError
from .optimizer import fold_constants_prog
from .semantic import SemanticAnalyzer, SemanticError
from .ir import IRGenerator
from .codegen_asm import ASMGenerator
from .codegen_machine import Assembler
from .runtime_vm import VM


def compile_pipeline(source_code: str, optimize: bool = True, run: bool = False, inputs: List[int] | None = None, emit: str | None = None, trace_ir: bool = False, trace_asm: bool = False, trace_vm: bool = False, out_dir: Path | None = None):
    # Lexing
    lexer = Lexer(source_code)
    tokens: List[Token] = lexer.tokenize()

    # Parsing
    parser = Parser(tokens, source=source_code)
    program = parser.parse()

    # Optimize (AST-level)
    if optimize:
        program = fold_constants_prog(program)

    # Semantic analysis
    sema = SemanticAnalyzer()
    sem_res = sema.analyze(program)

    # IR generation
    irgen = IRGenerator()
    ir = irgen.generate(program)
    if trace_ir:
        # attach IR trace to results (also printed)
        for ins in ir:
            print(ins)

    # ASM generation
    asmgen = ASMGenerator()
    asm_lines, syms, consts = asmgen.generate(ir)
    if trace_asm:
        for l in asm_lines:
            print(l)

    # Machine code generation
    assembler = Assembler()
    instrs, labels, collected_syms = assembler.assemble(asm_lines)
    # Merge constants mapping values
    const_values = {f"const_{v}": v for v in consts}
    mprog = assembler.link(instrs, labels, collected_syms, const_values)

    results = {
        'tokens': tokens,
        'ast': program,
        'sem_warnings': sem_res.warnings,
        'ir': ir,
        'asm': asm_lines,
        'machine': mprog,
    }

    # Write artifacts if out_dir specified
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        # tokens
        with open(out_dir / 'tokens.txt', 'w', encoding='utf-8') as f:
            for tok in tokens:
                f.write(f"{tok}\n")
        # ast
        with open(out_dir / 'ast.txt', 'w', encoding='utf-8') as f:
            f.write(str(program) + '\n')
        # ir
        with open(out_dir / 'ir.txt', 'w', encoding='utf-8') as f:
            for ins in ir:
                f.write(str(ins) + '\n')
        # asm
        with open(out_dir / 'asm.txt', 'w', encoding='utf-8') as f:
            for line in asm_lines:
                f.write(line + '\n')
        # machine
        with open(out_dir / 'machine.txt', 'w', encoding='utf-8') as f:
            f.write(f"CODE: {mprog.code}\n")
            f.write(f"SYMS: {mprog.sym_addrs}\n")
            f.write(f"MEM_INIT: {mprog.mem_init}\n")

    if emit:
        return results.get(emit)

    if run:
        # Prepare input provider if inputs provided
        it = iter(inputs) if inputs else None
        def provider():
            if it is None:
                return int(input('> ').strip())
            try:
                return int(next(it))
            except StopIteration:
                raise RuntimeError('Not enough input values provided to VM')
        vm = VM(mprog.code, memory_size=(max(mprog.sym_addrs.values())+1 if mprog.sym_addrs else 1), mem_init=mprog.mem_init, input_provider=provider, trace=trace_vm)
        result = vm.run()
        if trace_vm and result.trace is not None:
            for entry in result.trace:
                print(entry)
        return result

    return results


def main():
    parser = argparse.ArgumentParser(description='MiniLang Compiler')
    parser.add_argument('file', help='MiniLang source file')
    parser.add_argument('--no-opt', action='store_true', help='Disable optimizations')
    parser.add_argument('--emit', choices=['tokens','ast','ir','asm','machine'], help='Emit specific stage and exit')
    parser.add_argument('--emit-all', action='store_true', help='Write all stages to files in --out-dir')
    parser.add_argument('--out-dir', type=str, help='Directory to write artifacts (used with --emit-all)')
    parser.add_argument('--run', action='store_true', help='Run the program on the VM after compilation')
    parser.add_argument('--trace-ir', action='store_true', help='Print IR after generation')
    parser.add_argument('--trace-asm', action='store_true', help='Print assembly after generation')
    parser.add_argument('--trace-vm', action='store_true', help='Trace VM execution (print per-instruction snapshots)')
    parser.add_argument('--inputs', nargs='*', type=int, help='Provide input integers for read statements')
    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as f:
        source = f.read()

    out_dir = None
    if args.emit_all:
        if not args.out_dir:
            print("Error: --emit-all requires --out-dir", file=sys.stderr)
            sys.exit(1)
        out_dir = Path(args.out_dir)

    try:
        out = compile_pipeline(source_code=source, optimize=not args.no_opt, run=args.run, inputs=args.inputs, emit=args.emit, trace_ir=args.trace_ir, trace_asm=args.trace_asm, trace_vm=args.trace_vm, out_dir=out_dir)
    except (LexError, ParseError, SemanticError) as e:
        print(f"Compilation error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)

    if args.emit:
        if args.emit == 'tokens' and isinstance(out, list):
            for t in out:
                print(t)
        elif args.emit == 'ast':
            print(out)
        elif args.emit == 'ir' and isinstance(out, list):
            for ins in out:
                print(ins)
        elif args.emit == 'asm' and isinstance(out, list):
            for line in out:
                print(line)
        elif args.emit == 'machine':
            from .codegen_machine import MachineProgram
            if isinstance(out, MachineProgram):
                print('CODE:', out.code)
                print('SYMS:', out.sym_addrs)
                print('MEM_INIT:', out.mem_init)
    elif args.run:
        from .runtime_vm import VMResult
        if isinstance(out, VMResult):
            print('\n'.join(map(str, out.outputs)))


if __name__ == '__main__':
    main()
