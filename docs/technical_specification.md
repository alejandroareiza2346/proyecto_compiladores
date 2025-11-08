# MINILANG COMPILER - TECHNICAL SPECIFICATION

## DOCUMENT CLASSIFICATION: TECHNICAL

### REVISION HISTORY
- Rev 1.0 - November 2025 - Initial specification

---

## 1. SYSTEM OVERVIEW

The MiniLang compiler is a complete implementation of a six-stage compilation pipeline targeting an accumulator-based virtual machine architecture. The system processes source files through lexical analysis, syntactic analysis, semantic validation, intermediate representation generation, code optimization, and machine code emission phases.

### 1.1 SYSTEM COMPONENTS

```
Source Code (.minilang)
    |
    v
[Lexical Analyzer] --> Token Stream
    |
    v
[Syntax Analyzer] --> Abstract Syntax Tree (AST)
    |
    v
[Semantic Analyzer] --> Validated AST + Symbol Table
    |
    v
[Optimizer] --> Optimized AST
    |
    v
[IR Generator] --> Three-Address Code (TAC)
    |
    v
[Assembly Generator] --> Assembly Instructions
    |
    v
[Machine Code Generator] --> Bytecode
    |
    v
[Virtual Machine] --> Program Execution
```

### 1.2 LANGUAGE SPECIFICATION

MiniLang is a strongly-typed imperative language with the following constraints:
- Single data type: signed integer
- Global scope only
- No function declarations
- No recursion support
- Sequential execution model

---

## 2. LEXICAL ANALYSIS MODULE

**File**: `minilang_compiler/lexer.py`

### 2.1 TOKENIZATION ALGORITHM

The lexer implements a single-pass character-by-character scanner using a deterministic finite automaton (DFA) approach.

**State Machine**:
```
START -> WHITESPACE -> START
START -> LETTER -> IDENTIFIER/KEYWORD
START -> DIGIT -> NUMBER
START -> OPERATOR -> OPERATOR_TOKEN
START -> COMMENT_START -> COMMENT_BODY -> START
```

### 2.2 TOKEN TYPES

Defined in `tokens.py`:

**Single-Character Tokens**:
- PLUS: `+`
- MINUS: `-`
- STAR: `*`
- SLASH: `/`
- LPAREN: `(`
- RPAREN: `)`
- LBRACE: `{`
- RBRACE: `}`
- SEMI: `;`
- ASSIGN: `=`

**Multi-Character Tokens**:
- LT: `<`
- GT: `>`
- LE: `<=`
- GE: `>=`
- EQ: `==`
- NEQ: `!=`

**Literals**:
- IDENT: `[a-zA-Z_][a-zA-Z0-9_]*`
- NUMBER: `[0-9]+`

**Keywords**:
- READ
- PRINT
- IF
- ELSE
- WHILE
- END

### 2.3 COMMENT HANDLING

Two comment styles supported:
- Single-line: `// comment text`
- Multi-line: `/* comment text */`

Comments are stripped during tokenization and do not appear in token stream.

### 2.4 ERROR DETECTION

Lexical errors detected:
- Invalid characters
- Unterminated block comments
- Malformed operators (e.g., `!` without `=`)

Each error includes:
- Line number (1-indexed)
- Column number (1-indexed)
- Source code context with caret indicator

### 2.5 IMPLEMENTATION DETAILS

**Class**: `Lexer`

**Attributes**:
- `source`: Input string
- `pos`: Current position in source
- `line`: Current line number
- `col`: Current column number

**Methods**:
- `tokenize()`: Main entry point, returns list of Token objects
- `_advance()`: Consume one character, update position counters
- `_peek()`: Look at current character without consuming
- `_match(expected)`: Conditional advance if character matches
- `_skip_whitespace_and_comments()`: Skip non-token characters
- `_identifier(start_line, start_col)`: Tokenize identifier or keyword
- `_number(start_line, start_col)`: Tokenize numeric literal

**Complexity**: O(n) where n is source length

---

## 3. SYNTAX ANALYSIS MODULE

**File**: `minilang_compiler/parser.py`

### 3.1 PARSING STRATEGY

Recursive descent parser implementing an LL(1) grammar with predictive parsing. No backtracking required.

### 3.2 GRAMMAR SPECIFICATION

```ebnf
program    := stmt* 'end' EOF
stmt       := read_stmt | print_stmt | assign_stmt | if_stmt | while_stmt
read_stmt  := 'read' IDENT ';'
print_stmt := 'print' expr ';'
assign_stmt := IDENT '=' expr ';'
if_stmt    := 'if' expr '{' stmt* '}' 'else' '{' stmt* '}'
while_stmt := 'while' expr '{' stmt* '}'

expr       := equality
equality   := comparison (('==' | '!=') comparison)*
comparison := term (('<' | '>' | '<=' | '>=') term)*
term       := factor (('+' | '-') factor)*
factor     := unary (('*' | '/') unary)*
unary      := '-' unary | primary
primary    := NUMBER | IDENT | '(' expr ')'
```

### 3.3 OPERATOR PRECEDENCE

From highest to lowest:
1. Unary minus: `-`
2. Multiplicative: `*`, `/`
3. Additive: `+`, `-`
4. Relational: `<`, `>`, `<=`, `>=`
5. Equality: `==`, `!=`

Associativity: Left-to-right for all binary operators

### 3.4 AST NODE TYPES

Defined in `ast_nodes.py`:

**Expression Nodes**:
- `Number(value: int)`: Integer literal
- `Var(name: str)`: Variable reference
- `UnaryOp(op: str, expr: Expr)`: Unary operation
- `BinaryOp(left: Expr, op: str, right: Expr)`: Binary operation

**Statement Nodes**:
- `Read(name: str)`: Input statement
- `Print(expr: Expr)`: Output statement
- `Assign(name: str, expr: Expr)`: Assignment statement
- `IfElse(cond: Expr, then_body: List[Stmt], else_body: List[Stmt])`: Conditional
- `While(cond: Expr, body: List[Stmt])`: Loop

**Program Node**:
- `Program(body: List[Stmt])`: Root node

### 3.5 ERROR RECOVERY

Parser errors include:
- Unexpected token type
- Missing required tokens (semicolons, braces, keywords)
- Premature end of file
- Malformed expressions

Error messages include source code context with line/column information.

### 3.6 IMPLEMENTATION DETAILS

**Class**: `Parser`

**Attributes**:
- `tokens`: Token list from lexer
- `pos`: Current token index
- `source`: Original source (for error reporting)

**Methods**:
- `parse()`: Entry point, returns Program AST
- `_statement()`: Parse statement
- `_expression()`: Entry to expression parsing
- `_equality()`, `_comparison()`, `_term()`, `_factor()`, `_unary()`, `_primary()`: Expression precedence cascade
- `_peek()`: Current token without consuming
- `_advance()`: Move to next token
- `_match(*types)`: Conditional advance if token matches
- `_consume(type, message)`: Required token consumption with error

**Complexity**: O(n) where n is token count

---

## 4. SEMANTIC ANALYSIS MODULE

**File**: `minilang_compiler/semantic.py`

### 4.1 ANALYSIS OBJECTIVES

1. Variable declaration tracking
2. Variable initialization verification
3. Control flow analysis for initialization guarantees

### 4.2 SYMBOL TABLE STRUCTURE

**Class**: `SymbolTable`

**Attributes**:
- `symbols`: Dictionary mapping variable names to SymbolInfo objects

**Class**: `SymbolInfo`

**Attributes**:
- `name`: Variable identifier
- `initialized`: Boolean flag

### 4.3 INITIALIZATION ANALYSIS ALGORITHM

Flow-sensitive analysis tracking which variables are guaranteed to be initialized at each program point.

**Algorithm**:
```
function analyze_block(statements, in_init_set):
    current_init = copy(in_init_set)
    for stmt in statements:
        current_init = analyze_statement(stmt, current_init)
    return current_init

function analyze_statement(stmt, init_set):
    if stmt is Read:
        init_set.add(stmt.name)
    elif stmt is Assign:
        check_expression(stmt.expr, init_set)
        init_set.add(stmt.name)
    elif stmt is Print:
        check_expression(stmt.expr, init_set)
    elif stmt is IfElse:
        check_expression(stmt.cond, init_set)
        then_init = analyze_block(stmt.then_body, init_set)
        else_init = analyze_block(stmt.else_body, init_set)
        init_set = then_init ∩ else_init  // Only guaranteed if both branches
    elif stmt is While:
        check_expression(stmt.cond, init_set)
        analyze_block(stmt.body, init_set)  // Don't propagate (loop may not execute)
    return init_set
```

### 4.4 WARNING GENERATION

Warnings issued when:
- Variable used before initialization
- Variable potentially uninitialized (e.g., set in only one branch of if-else)

Conservative approach: If any execution path exists where variable is uninitialized, warning is issued.

### 4.5 IMPLEMENTATION DETAILS

**Class**: `SemanticAnalyzer`

**Methods**:
- `analyze(program)`: Main entry, returns SemanticResult
- `_analyze_block(body, in_init, allow_init_out)`: Block analysis
- `_analyze_stmt(stmt, init)`: Single statement analysis
- `_check_expr(expr, init)`: Expression validation

**Output**: `SemanticResult` containing:
- `table`: Final symbol table
- `warnings`: List of warning messages

---

## 5. OPTIMIZATION MODULE

**File**: `minilang_compiler/optimizer.py`

### 5.1 OPTIMIZATION TECHNIQUES

Current implementation: AST-level constant folding

### 5.2 CONSTANT FOLDING ALGORITHM

Bottom-up traversal of AST, evaluating compile-time constant expressions.

**Rules**:
```
fold(Number(n)) = Number(n)
fold(Var(x)) = Var(x)
fold(BinaryOp(Number(a), op, Number(b))) = Number(eval(a op b))
fold(BinaryOp(e1, op, e2)) = BinaryOp(fold(e1), op, fold(e2))
fold(UnaryOp('-', Number(n))) = Number(-n)
fold(UnaryOp(op, e)) = UnaryOp(op, fold(e))
```

**Operations Evaluated**:
- Arithmetic: `+`, `-`, `*`, `/` (integer division)
- Relational: `<`, `>`, `<=`, `>=`
- Equality: `==`, `!=`

**Results**: Boolean operations yield 0 (false) or 1 (true)

### 5.3 CONTROL FLOW OPTIMIZATION

If condition is constant:
- `if 0 { A } else { B }` → `B`
- `if N { A } else { B }` → `A` (where N ≠ 0)

### 5.4 IMPLEMENTATION DETAILS

**Functions**:
- `fold_constants_prog(program)`: Entry point for program optimization
- `fold_constants_expr(expr)`: Recursive expression folder

**Complexity**: O(n) where n is AST node count

---

## 6. INTERMEDIATE REPRESENTATION MODULE

**File**: `minilang_compiler/ir.py`

### 6.1 IR FORMAT

Three-Address Code (TAC) representation. Each instruction has at most three operands.

**Instruction Format**:
```
IRInstr(op, a1, a2, res)
```

Where:
- `op`: Operation code
- `a1`, `a2`: Operands (may be None)
- `res`: Result destination (may be None)

### 6.2 INSTRUCTION SET

**Assignments**:
- `assign src None dest`: dest = src

**Arithmetic**:
- `+ left right dest`: dest = left + right
- `- left right dest`: dest = left - right
- `* left right dest`: dest = left * right
- `/ left right dest`: dest = left / right
- `uminus val None dest`: dest = -val

**Relational**:
- `< left right dest`: dest = (left < right)
- `> left right dest`: dest = (left > right)
- `<= left right dest`: dest = (left <= right)
- `>= left right dest`: dest = (left >= right)
- `== left right dest`: dest = (left == right)
- `!= left right dest`: dest = (left != right)

**Control Flow**:
- `label name None None`: Define label
- `goto label None None`: Unconditional jump
- `ifnz cond label None`: Jump if cond != 0

**I/O**:
- `read var None None`: Input to variable
- `print val None None`: Output value

### 6.3 TEMPORARY VARIABLES

Temporaries generated with sequential naming: `t1`, `t2`, `t3`, ...

Each subexpression result stored in a temporary.

Example:
```
c = a + b * 2

Generates:
  t1 = 2
  t2 = b * t1
  t3 = a + t2
  c = t3
```

### 6.4 LABEL GENERATION

Labels generated with sequential naming: `L1`, `L2`, `L3`, ...

Special label: `END` marks program termination.

### 6.5 CONTROL FLOW TRANSLATION

**If-Else**:
```
if COND { THEN } else { ELSE }

Translates to:
  t1 = COND
  ifnz t1 L_true
  ELSE_code
  goto L_end
  label L_true
  THEN_code
  label L_end
```

**While**:
```
while COND { BODY }

Translates to:
  label L_start
  t1 = COND
  ifnz t1 L_body
  goto L_end
  label L_body
  BODY_code
  goto L_start
  label L_end
```

### 6.6 IMPLEMENTATION DETAILS

**Class**: `IRGenerator`

**Attributes**:
- `temp_counter`: Temporary variable counter
- `label_counter`: Label counter
- `ir`: List of IRInstr objects

**Methods**:
- `generate(program)`: Convert AST to IR
- `new_temp()`: Allocate new temporary
- `new_label(base)`: Allocate new label
- `_emit_stmt(stmt)`: Generate IR for statement
- `_emit_expr(expr)`: Generate IR for expression, return result operand

---

## 7. ASSEMBLY GENERATION MODULE

**File**: `minilang_compiler/codegen_asm.py`

### 7.1 TARGET ARCHITECTURE

Accumulator-based architecture with the following characteristics:
- Single accumulator register
- Memory-based operands
- No general-purpose registers

### 7.2 INSTRUCTION SET ARCHITECTURE

**Data Movement**:
- `LOAD addr`: ACC = MEM[addr]
- `STORE addr`: MEM[addr] = ACC

**Arithmetic**:
- `ADD addr`: ACC = ACC + MEM[addr]
- `SUB addr`: ACC = ACC - MEM[addr]
- `MUL addr`: ACC = ACC * MEM[addr]
- `DIV addr`: ACC = ACC / MEM[addr] (integer division)

**Control Flow**:
- `JMP label`: Unconditional jump
- `JLT label`: Jump if ACC < 0
- `JGT label`: Jump if ACC > 0
- `JLE label`: Jump if ACC <= 0
- `JGE label`: Jump if ACC >= 0
- `JEQ label`: Jump if ACC == 0
- `JNE label`: Jump if ACC != 0

**I/O**:
- `IN addr`: MEM[addr] = read_input()
- `OUT addr`: write_output(MEM[addr])

**Special**:
- `LABEL name`: Define label (pseudo-instruction)
- `HALT`: Stop execution

### 7.3 IR TO ASSEMBLY TRANSLATION

**Binary Operations**:
```
IR: t3 = t1 + t2

Assembly:
  LOAD t1
  ADD t2
  STORE t3
```

**Unary Minus**:
```
IR: t2 = -t1

Assembly:
  LOAD const_0
  SUB t1
  STORE t2
```

**Relational Operations**:
```
IR: t3 = t1 < t2

Assembly:
  LOAD t1
  SUB t2
  JLT L_true
  LOAD const_0
  STORE t3
  JMP L_end
  LABEL L_true
  LOAD const_1
  STORE t3
  LABEL L_end
```

### 7.4 CONSTANT HANDLING

Constants allocated as memory locations with names `const_0`, `const_1`, etc.

Constants discovered during assembly generation and collected in a set.

### 7.5 SYMBOL COLLECTION

All variable names and temporaries collected during generation for memory allocation phase.

### 7.6 IMPLEMENTATION DETAILS

**Class**: `ASMGenerator`

**Attributes**:
- `lines`: List of assembly instructions
- `syms`: Set of symbol names
- `consts`: Set of constant values

**Methods**:
- `generate(ir)`: Convert IR to assembly
- `_sym_for_const(value)`: Get/create constant symbol
- `_use_sym(name)`: Record symbol usage
- `_emit(line)`: Add instruction to output

**Output**: Tuple of (assembly_lines, symbols, constants)

---

## 8. MACHINE CODE GENERATION MODULE

**File**: `minilang_compiler/codegen_machine.py`

### 8.1 BYTECODE FORMAT

Flattened array of integers: `[opcode, operand, opcode, operand, ...]`

Each instruction occupies two array slots.

### 8.2 OPCODE MAPPING

```
LOAD:  1    STORE: 2    ADD:   3    SUB:   4
MUL:   5    DIV:   6    JMP:   7    JLT:   8
JGT:   9    JLE:   10   JGE:   11   JEQ:   12
JNE:   13   IN:    14   OUT:   15   HALT:  16
```

### 8.3 ASSEMBLY PROCESS

**Phase 1: Instruction Collection**

Parse assembly text, build instruction list with opcodes and operand names.

Track label positions (instruction index).

**Phase 2: Linking**

Resolve all operand names:
- Labels → instruction addresses
- Variables → memory addresses
- Temporaries → memory addresses
- Constants → memory addresses

### 8.4 MEMORY ALLOCATION

Memory addresses assigned sequentially starting from 0.

Allocation order:
1. Constants (with initialization values)
2. Variables (alphabetically sorted)
3. Temporaries (numerically sorted)

### 8.5 LABEL RESOLUTION

Labels map to instruction indices (not byte offsets).

Jump operands contain target instruction index.

### 8.6 MACHINE PROGRAM STRUCTURE

**Class**: `MachineProgram`

**Attributes**:
- `code`: Bytecode array
- `sym_addrs`: Dictionary mapping symbol names to memory addresses
- `mem_init`: Dictionary mapping addresses to initial values
- `labels`: Dictionary mapping label names to instruction addresses

### 8.7 IMPLEMENTATION DETAILS

**Class**: `Assembler`

**Methods**:
- `assemble(asm_lines)`: Parse assembly to instructions and labels
- `link(instrs, labels, syms, const_values)`: Resolve addresses and generate bytecode

---

## 9. VIRTUAL MACHINE MODULE

**File**: `minilang_compiler/runtime_vm.py`

### 9.1 VM ARCHITECTURE

**Components**:
- Program Counter (PC): Current instruction address
- Accumulator (ACC): Single register for computations
- Memory (MEM): Array of integers
- Input Provider: Function supplying input values
- Output Buffer: List collecting output values

### 9.2 EXECUTION CYCLE

```
while PC < code_length:
    opcode = code[PC]
    operand = code[PC + 1]
    PC += 2
    
    execute(opcode, operand)
    
    if opcode == HALT:
        break
```

### 9.3 INSTRUCTION EXECUTION

**Data Operations**:
- LOAD: `ACC = MEM[operand]`
- STORE: `MEM[operand] = ACC`
- ADD: `ACC = ACC + MEM[operand]`
- SUB: `ACC = ACC - MEM[operand]`
- MUL: `ACC = ACC * MEM[operand]`
- DIV: `ACC = ACC / MEM[operand]` (raises exception if MEM[operand] == 0)

**Control Operations**:
- JMP: `PC = operand * 2` (convert instruction index to byte offset)
- JLT: `if ACC < 0: PC = operand * 2`
- JGT: `if ACC > 0: PC = operand * 2`
- JLE: `if ACC <= 0: PC = operand * 2`
- JGE: `if ACC >= 0: PC = operand * 2`
- JEQ: `if ACC == 0: PC = operand * 2`
- JNE: `if ACC != 0: PC = operand * 2`

**I/O Operations**:
- IN: `MEM[operand] = input_provider()`
- OUT: `output_buffer.append(MEM[operand])`

**Special**:
- HALT: Terminate execution

### 9.4 MEMORY INITIALIZATION

Memory pre-populated with constant values before execution.

Size determined by highest allocated address + 1.

### 9.5 INPUT MECHANISM

Input provided via callable function. Two modes:
1. Interactive: Read from stdin
2. Batch: Read from pre-supplied list

### 9.6 TRACE MODE

Optional execution tracing records after each instruction:
- PC value
- Opcode and operand
- Accumulator value
- Memory snapshot (first 32 cells)

### 9.7 ERROR HANDLING

Runtime errors:
- Division by zero
- Unknown opcode
- Input exhaustion (in batch mode)

### 9.8 IMPLEMENTATION DETAILS

**Class**: `VM`

**Attributes**:
- `code`: Bytecode array
- `pc`: Program counter
- `acc`: Accumulator
- `mem`: Memory array
- `outputs`: Output buffer
- `trace`: Optional trace log
- `input_provider`: Input function

**Methods**:
- `run()`: Execute program, return VMResult

**Class**: `VMResult`

**Attributes**:
- `outputs`: List of output values
- `trace`: Optional execution trace

---

## 10. COMPILER ORCHESTRATION MODULE

**File**: `minilang_compiler/compiler.py`

### 10.1 COMPILATION PIPELINE

```python
def compile_pipeline(source_code, optimize, run, inputs, emit, trace_ir, trace_asm, trace_vm, out_dir):
    # Stage 1: Lexical Analysis
    tokens = Lexer(source_code).tokenize()
    
    # Stage 2: Syntax Analysis
    program = Parser(tokens, source_code).parse()
    
    # Stage 3: Optimization (optional)
    if optimize:
        program = fold_constants_prog(program)
    
    # Stage 4: Semantic Analysis
    sem_result = SemanticAnalyzer().analyze(program)
    
    # Stage 5: IR Generation
    ir = IRGenerator().generate(program)
    
    # Stage 6: Assembly Generation
    asm_lines, syms, consts = ASMGenerator().generate(ir)
    
    # Stage 7: Machine Code Generation
    assembler = Assembler()
    instrs, labels, collected_syms = assembler.assemble(asm_lines)
    const_values = {f"const_{v}": v for v in consts}
    machine_prog = assembler.link(instrs, labels, collected_syms, const_values)
    
    # Stage 8: Execution (optional)
    if run:
        vm = VM(machine_prog.code, memory_size, machine_prog.mem_init, input_provider, trace_vm)
        result = vm.run()
        return result
    
    return artifacts
```

### 10.2 COMMAND-LINE INTERFACE

**Arguments**:
- `file`: Source file path (required)
- `--no-opt`: Disable optimizations
- `--emit STAGE`: Emit specific stage output
- `--emit-all`: Write all stages to files
- `--out-dir DIR`: Output directory for `--emit-all`
- `--run`: Execute program on VM
- `--trace-ir`: Print IR after generation
- `--trace-asm`: Print assembly after generation
- `--trace-vm`: Print VM execution trace
- `--inputs N1 N2 ...`: Provide input values

**Stages for --emit**:
- `tokens`: Token stream
- `ast`: Abstract syntax tree
- `ir`: Intermediate representation
- `asm`: Assembly code
- `machine`: Machine code (bytecode + symbol table)

### 10.3 ERROR HANDLING

Compilation errors caught and reported:
- `LexError`: Lexical analysis failure
- `ParseError`: Syntax analysis failure
- `SemanticError`: Semantic validation failure

Exit codes:
- 0: Success
- 1: Compilation error
- 2: Unexpected error (internal error)

### 10.4 OUTPUT MODES

**Interactive Mode** (no --emit):
- If `--run`: Print program outputs line by line
- Otherwise: No output (compilation check only)

**Emit Mode** (--emit STAGE):
- Print requested stage to stdout

**Emit-All Mode** (--emit-all):
- Write all stages to separate files in `--out-dir`
- Files: tokens.txt, ast.txt, ir.txt, asm.txt, machine.txt

---

## 11. WEB INTERFACE MODULE

**File**: `web_app.py`

### 11.1 ARCHITECTURE

Flask-based web application providing browser-accessible compiler interface.

**Routes**:
- `GET /`: Main page (serves index.html)
- `POST /compile`: Compilation endpoint
- `GET /examples`: Load example programs

### 11.2 COMPILATION ENDPOINT

**Request Format** (JSON):
```json
{
    "code": "source code string",
    "inputs": "3 7" or [3, 7],
    "show_stages": true/false
}
```

**Response Format** (JSON):
```json
{
    "success": true,
    "outputs": [17, 0, 1, 2, ...],
    "stages": {
        "tokens": "token listing",
        "ast": "AST representation",
        "ir": "TAC listing",
        "asm": "assembly listing",
        "machine": "machine code info",
        "warnings": "semantic warnings"
    }
}
```

**Error Response**:
```json
{
    "success": false,
    "error": "error message"
}
```

### 11.3 EXAMPLES ENDPOINT

Returns JSON object with 5 preconfigured example programs:
- program1: Complete feature demonstration
- program2: Nested if-else
- program3: While with zero iterations
- program4: Operator precedence
- program5: I/O echo

Each example includes:
- `name`: Display name
- `code`: Source code
- `inputs`: Input values
- `description`: Brief explanation

### 11.4 FRONTEND IMPLEMENTATION

**File**: `templates/index.html`

Single-page application with:
- Code editor (textarea)
- Input field for read values
- Checkbox for stage visualization
- Example selection buttons
- Compile/Execute button
- Clear button
- Output display area
- Collapsible stage panels

**JavaScript Functions**:
- `loadExamples()`: Fetch and populate example buttons
- `loadExample(example)`: Load example into editor
- `compileCode()`: Send compilation request to backend
- `createStageDiv(title, content)`: Create collapsible stage panel
- `clearAll()`: Reset interface

**Keyboard Shortcuts**:
- Ctrl+Enter: Compile and execute

---

## 12. TESTING FRAMEWORK

**Directory**: `tests/`

### 12.1 TEST MODULES

**test_lexer.py**:
- Basic token recognition
- Comment handling
- Position tracking
- Error detection (invalid characters)

**test_parser.py**:
- Minimal program parsing
- Statement and block structures
- Error detection (missing semicolons)

**test_semantic.py**:
- Initialization warning generation
- Properly initialized variables (no warnings)

**test_ir_vm.py**:
- End-to-end pipeline test
- Program execution verification
- Output validation

### 12.2 TEST EXECUTION

```bash
pytest -v
```

All tests must pass before deployment.

---

## 13. BUILD AND DEPLOYMENT

### 13.1 PACKAGE STRUCTURE

**pyproject.toml**:
- Project metadata
- Python version requirement: >=3.10
- Entry point: `minilangc` command
- Build system: setuptools

**requirements.txt**:
- Flask >=3.1.0
- pytest >=8.4.0

### 13.2 INSTALLATION

```bash
pip install -r requirements.txt
pip install -e .
```

Editable mode (`-e`) allows development without reinstallation.

### 13.3 CONTINUOUS INTEGRATION

**File**: `.github/workflows/ci.yml`

GitHub Actions workflow:
- Trigger: Push or pull request to main branch
- Platform: Windows
- Python versions: 3.10, 3.11, 3.12, 3.13
- Steps:
  1. Checkout code
  2. Setup Python
  3. Install dependencies
  4. Run pytest

---

## 14. LIMITATIONS AND CONSTRAINTS

### 14.1 LANGUAGE LIMITATIONS

- Single data type (integer only)
- No floating-point support
- No string support
- No arrays or composite types
- No functions or procedures
- No recursion
- Global scope only
- No nested scopes

### 14.2 IMPLEMENTATION LIMITATIONS

- No type checking (single type makes this unnecessary)
- No register allocation (accumulator architecture)
- Limited optimizations (constant folding only)
- No dead code elimination
- No common subexpression elimination
- No loop optimizations
- No peephole optimizations

### 14.3 RUNTIME LIMITATIONS

- Integer division semantics (truncation toward zero)
- No overflow detection
- Division by zero raises exception
- Memory size fixed at compile time
- No dynamic memory allocation
- No garbage collection

### 14.4 ARCHITECTURAL DECISIONS

**Accumulator vs Register Machine**:
- Accumulator chosen for simplicity
- Reduces instruction complexity
- Eliminates register allocation phase
- Trade-off: More memory operations

**TAC as IR**:
- Simple three-address format
- Easy to generate from AST
- Straightforward translation to assembly
- Platform-independent representation

**Virtual Machine vs Native Code**:
- VM provides portability
- Simpler implementation
- Easier debugging
- Trade-off: Slower execution

---

## 15. EXTENSION POINTS

### 15.1 POTENTIAL ENHANCEMENTS

**Language Features**:
- Additional data types (float, string, boolean)
- Arrays and indexing
- Functions with parameters and return values
- Local scope and lexical scoping
- Structures or records
- For loops
- Break/continue statements

**Optimization**:
- Constant propagation
- Dead code elimination
- Common subexpression elimination
- Strength reduction
- Loop invariant code motion
- Peephole optimization

**Code Generation**:
- Register allocation
- Instruction scheduling
- Native code generation (x86, ARM)
- LLVM backend

**Analysis**:
- Type inference
- Data flow analysis
- Control flow graph construction
- Live variable analysis
- Reaching definitions

**Tools**:
- Debugger with breakpoints
- Profiler for performance analysis
- Visual AST/CFG display
- Interactive REPL

---

## END OF DOCUMENT

**Document Control**:
- Classification: Technical Specification
- Distribution: Project Team
- Last Updated: November 2025
- Version: 1.0
