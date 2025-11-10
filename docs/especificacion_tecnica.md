# COMPILADOR MINILANG - ESPECIFICACIÓN TÉCNICA

## CLASIFICACIÓN DEL DOCUMENTO: TÉCNICO

### HISTORIAL DE REVISIONES

- Rev 1.0 - Noviembre 2025 - Especificación inicial

---

## 1. VISIÓN GENERAL DEL SISTEMA

El compilador MiniLang es una implementación completa de un pipeline de compilación de seis etapas dirigido a una arquitectura de máquina virtual basada en acumulador. El sistema procesa archivos fuente a través de análisis léxico, análisis sintáctico, validación semántica, generación de representación intermedia, optimización de código y fases de emisión de código máquina.

### 1.1 COMPONENTES DEL SISTEMA

```text
Código Fuente (.minilang)
    |
    v
[Analizador Léxico] --> Flujo de Tokens
    |
    v
[Analizador Sintáctico] --> Árbol de Sintaxis Abstracta (AST)
    |
    v
[Analizador Semántico] --> AST Validado + Tabla de Símbolos
    |
    v
[Optimizador] --> AST Optimizado
    |
    v
[Generador IR] --> Código de Tres Direcciones (TAC)
    |
    v
[Generador de Ensamblador] --> Instrucciones de Ensamblador
    |
    v
[Generador de Código Máquina] --> Bytecode
    |
    v
[Máquina Virtual] --> Ejecución del Programa
```

### 1.2 ESPECIFICACIÓN DEL LENGUAJE

MiniLang es un lenguaje imperativo fuertemente tipado con las siguientes restricciones:

- Tipo de dato único: entero con signo
- Solo alcance global
- Sin declaraciones de funciones
- Sin soporte de recursión
- Modelo de ejecución secuencial

---

## 2. MÓDULO DE ANÁLISIS LÉXICO

**Archivo**: `minilang_compiler/lexer.py`

### 2.1 ALGORITMO DE TOKENIZACIÓN

El lexer implementa un escáner carácter por carácter de un solo paso usando un enfoque de autómata finito determinista (DFA).

**Máquina de Estados**:

```text
INICIO -> ESPACIO_BLANCO -> INICIO
INICIO -> LETRA -> IDENTIFICADOR/PALABRA_CLAVE
INICIO -> DÍGITO -> NÚMERO
INICIO -> OPERADOR -> TOKEN_OPERADOR
INICIO -> INICIO_COMENTARIO -> CUERPO_COMENTARIO -> INICIO
```

### 2.2 TIPOS DE TOKENS

Definidos en `tokens.py`:

**Tokens de Un Solo Carácter**:

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

**Tokens de Múltiples Caracteres**:

- LT: `<`
- GT: `>`
- LE: `<=`
- GE: `>=`
- EQ: `==`
- NEQ: `!=`

**Literales**:

- IDENT: `[a-zA-Z_][a-zA-Z0-9_]*`
- NUMBER: `[0-9]+`

**Palabras Clave**:

- READ
- PRINT
- IF
- ELSE
- WHILE
- END

### 2.3 MANEJO DE COMENTARIOS

Dos estilos de comentarios soportados:

- Una sola línea: `// texto del comentario`
- Múltiples líneas: `/* texto del comentario */`

Los comentarios se eliminan durante la tokenización y no aparecen en el flujo de tokens.

### 2.4 DETECCIÓN DE ERRORES

Errores léxicos detectados:

- Caracteres inválidos
- Comentarios de bloque sin terminar
- Operadores mal formados (ej., `!` sin `=`)

Cada error incluye:

- Número de línea (indexado desde 1)
- Número de columna (indexado desde 1)
- Contexto del código fuente con indicador de cursor

### 2.5 DETALLES DE IMPLEMENTACIÓN

**Clase**: `Lexer`

**Atributos**:

- `source`: Cadena de entrada
- `pos`: Posición actual en el código fuente
- `line`: Número de línea actual
- `col`: Número de columna actual

**Métodos**:

- `tokenize()`: Punto de entrada principal, devuelve lista de objetos Token
- `_advance()`: Consume un carácter, actualiza contadores de posición
- `_peek()`: Mira el carácter actual sin consumir
- `_match(expected)`: Avance condicional si el carácter coincide
- `_skip_whitespace_and_comments()`: Salta caracteres quedentifier(start_line, start_col)`: Tokeniza identificador o palabra clave
- `_number(start_line, start_col)`: Tokeniza literal numérico

**Complejidad**: O(n) donde n es la longitud del código fuente

---

## 3. MÓDULO DE ANÁLISIS SINTÁCTICO

**Archivo**: `minilang_compiler/parser.py`

### 3.1 ESTRATEGIA DE ANÁLISIS

Parser de descenso recursivo que implementa una gramática LL(1) con análisis predictivo. No se requiere retroceso.

### 3.2 ESPECIFICACIÓN DE LA GRAMÁTICA

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

### 3.3 PRECEDENCIA DE OPERADORES

De mayor a menor:

1. Menos unario: `-`
2. Multiplicativos: `*`, `/`
3. Aditivos: `+`, `-`
4. Relacionales: `<`, `>`, `<=`, `>=`
5. Igualdad: `==`, `!=`

Asociatividad: Izquierda a derecha para todos los operadores binarios

### 3.4 TIPOS DE NODOS AST

Definidos en `ast_nodes.py`:

**Nodos de Expresión**:

- `Number(value: int)`: Literal entero
- `Var(name: str)`: Referencia a variable
- `UnaryOp(op: str, expr: Expr)`: Operación unaria
- `BinaryOp(left: Expr, op: str, right: Expr)`: Operación binaria

**Nodos de Declaración**:

- `Read(name: str)`: Declaración de entrada
- `Print(expr: Expr)`: Declaración de salida
- `Assign(name: str, expr: Expr)`: Declaración de asignación
- `IfElse(cond: Expr, then_body: List[Stmt], else_body: List[Stmt])`: Condicional
- `While(cond: Expr, body: List[Stmt])`: Bucle

**Nodo de Programa**:

- `Program(body: List[Stmt])`: Nodo raíz

### 3.5 RECUPERACIÓN DE ERRORES

Los errores del parser incluyen:

- Tipo de token inesperado
- Tokens requeridos faltantes (punto y coma, llaves, palabras clave)
- Final de archivo prematuro
- Expresiones mal formadas

Los mensajes de error incluyen contexto del código fuente con información de línea/columna.

### 3.6 DETALLES DE IMPLEMENTACIÓN

**Clase**: `Parser`

**Atributos**:

- `tokens`: Lista de tokens del lexer
- `pos`: Índice de token actual
- `source`: Fuente original (para reportar errores)

**Métodos**:

- `parse()`: Punto de entrada, devuelve AST de Program
- `_statement()`: Analiza declaración
- `_expression()`: Entrada al análisis de expresiones
- `_equality()`, `_comparison()`, `_term()`, `_factor()`, `_unary()`, `_primary()`: Cascada de precedencia de expresiones
- `_peek()`: Token actual sin consumir
- `_advance()`: Mover al siguiente token
- `_match(*types)`: Avance condicional si el token coincide
- `_consume(type, message)`: Consumo de token requerido con error

**Complejidad**: O(n) donde n es el conteo de tokens

---

## 4. MÓDULO DE ANÁLISIS SEMÁNTICO

**Archivo**: `minilang_compiler/semantic.py`

### 4.1 OBJETIVOS DEL ANÁLISIS

1. Seguimiento de declaración de variables
2. Verificación de inicialización de variables
3. Análisis de flujo de control para garantías de inicialización

### 4.2 ESTRUCTURA DE LA TABLA DE SÍMBOLOS

**Clase**: `SymbolTable`

**Atributos**:

- `symbols`: Diccionario que mapea nombres de variables a objetos SymbolInfo

**Clase**: `SymbolInfo`

**Atributos**:

- `name`: Identificador de variable
- `initialized`: Bandera booleana

### 4.3 ALGORITMO DE ANÁLISIS DE INICIALIZACIÓN

Análisis sensible al flujo que rastrea qué variables están garantizadas para ser inicializadas en cada punto del programa.

**Algoritmo**:

función analyze_block(statements, in_init_set):
    current_init = copia(in_init_set)
    para cada stmt en statements:
        current_init = analyze_statement(stmt, current_init)
    retornar current_init

función analyze_statement(stmt, init_set):
    si stmt es Read:
        init_set.add(stmt.name)
    si no si stmt es Assign:
        check_expression(stmt.expr, init_set)
        init_set.add(stmt.name)
    si no si stmt es Print:
        check_expression(stmt.expr, init_set)
    si no si stmt es IfElse:
        check_expression(stmt.cond, init_set)
        then_init = analyze_block(stmt.then_body, init_set)
        else_init = analyze_block(stmt.else_body, init_set)
        init_set = then_init ∩ else_init  // Solo garantizado si ambas ramas
    si no si stmt es While:
        check_expression(stmt.cond, init_set)
        analyze_block(stmt.body, init_set)  // No propagar (bucle puede no ejecutarse)
    retornar init_set

### 4.4 GENERACIÓN DE ADVERTENCIAS

Se emiten advertencias cuando:

- Variable usada antes de la inicialización
- Variable potencialmente no inicializada (ej., establecida solo en una rama de if-else)

Enfoque conservador: Si existe alguna ruta de ejecución donde la variable no está inicializada, se emite advertencia.

### 4.5 DETALLES DE IMPLEMENTACIÓN

**Clase**: `SemanticAnalyzer`

**Métodos**:

- `analyze(program)`: Entrada principal, devuelve SemanticResult
- `_analyze_block(body, in_init, allow_init_out)`: Análisis de bloque
- `_analyze_stmt(stmt, init)`: Análisis de declaración única
- `_check_expr(expr, init)`: Validación de expresión

**Salida**: `SemanticResult` que contiene:

- `table`: Tabla de símbolos final
- `warnings`: Lista de mensajes de advertencia

---

## 5. MÓDULO DE OPTIMIZACIÓN

**Archivo**: `minilang_compiler/optimizer.py`

### 5.1 TÉCNICAS DE OPTIMIZACIÓN

Implementación actual: Plegado de constantes a nivel de AST

### 5.2 ALGORITMO DE PLEGADO DE CONSTANTES

Recorrido ascendente del AST, evaluando expresiones constantes en tiempo de compilación.

**Reglas**:
fold(Number(n)) = Number(n)
fold(Var(x)) = Var(x)
fold(BinaryOp(Number(a), op, Number(b))) = Number(eval(a op b))
fold(BinaryOp(e1, op, e2)) = BinaryOp(fold(e1), op, fold(e2))
fold(UnaryOp('-', Number(n))) = Number(-n)
fold(UnaryOp(op, e)) = UnaryOp(op, fold(e))

**Operaciones Evaluadas**:

- Aritméticas: `+`, `-`, `*`, `/` (división entera)
- Relacionales: `<`, `>`, `<=`, `>=`
- Igualdad: `==`, `!=`

**Resultados**: Las operaciones booleanas producen 0 (falso) o 1 (verdadero)

### 5.3 OPTIMIZACIÓN DE FLUJO DE CONTROL

Si la condición es constante:

- `if 0 { A } else { B }` → `B`
- `if N { A } else { B }` → `A` (donde N ≠ 0)

### 5.4 DETALLES DE IMPLEMENTACIÓN

**Funciones**:

- `fold_constants_prog(program)`: Punto de entrada para optimización de programa
- `fold_constants_expr(expr)`: Plegador de expresiones recursivo

**Complejidad**: O(n) donde n es el conteo de nodos AST

---

## 6. MÓDULO DE REPRESENTACIÓN INTERMEDIA

**Archivo**: `minilang_compiler/ir.py`

### 6.1 FORMATO IR

Representación de Código de Tres Direcciones (TAC). Cada instrucción tiene como máximo tres operandos.

**Formato de Instrucción**:
IRInstr(op, a1, a2, res)

Donde:

- `op`: Código de operación
- `a1`, `a2`: Operandos (pueden ser None)
- `res`: Destino del resultado (puede ser None)

### 6.2 CONJUNTO DE INSTRUCCIONES

**Asignaciones**:

- `assign src None dest`: dest = src

**Aritméticas**:

- `+ left right dest`: dest = left + right
- `- left right dest`: dest = left - right
- `* left right dest`: dest = left * right
- `/ left right dest`: dest = left / right
- `uminus val None dest`: dest = -val

**Relacionales**:

- `< left right dest`: dest = (left < right)
- `> left right dest`: dest = (left > right)
- `<= left right dest`: dest = (left <= right)
- `>= left right dest`: dest = (left >= right)
- `== left right dest`: dest = (left == right)
- `!= left right dest`: dest = (left != right)

**Flujo de Control**:

- `label name None None`: Definir etiqueta
- `goto label None None`: Salto incondicional
- `ifnz cond label None`: Saltar si cond != 0

**E/S**:

- `read var None None`: Entrada a variable
- `print val None None`: Salida de valor

### 6.3 VARIABLES TEMPORALES

Temporales generados con nombres secuenciales: `t1`, `t2`, `t3`, ...

Cada resultado de subexpresión almacenado en un temporal.

Ejemplo:
c = a + b * 2

Genera:
  t1 = 2
  t2 = b * t1
  t3 = a + t2
  c = t3

### 6.4 GENERACIÓN DE ETIQUETAS

Etiquetas generadas con nombres secuenciales: `L1`, `L2`, `L3`, ...

Etiqueta especial: `END` marca la terminación del programa.

### 6.5 TRADUCCIÓN DE FLUJO DE CONTROL

**If-Else**:
if COND { THEN } else { ELSE }

Se traduce a:
  t1 = COND
  ifnz t1 L_true
  ELSE_code
  goto L_end
  label L_true
  THEN_code
  label L_end
**While**:
while COND { BODY }

Se traduce a:
  label L_start
  t1 = COND
  ifnz t1 L_body
  goto L_end
  label L_body
  BODY_code
  goto L_start
  label L_end

### 6.6 DETALLES DE IMPLEMENTACIÓN

**Clase**: `IRGenerator`

**Atributos**:

- `temp_counter`: Contador de variables temporales
- `label_counter`: Contador de etiquetas
- `ir`: Lista de objetos IRInstr

**Métodos**:

- `generate(program)`: Convertir AST a IR
- `new_temp()`: Asignar nuevo temporal
- `new_label(base)`: Asignar nueva etiqueta
- `_emit_stmt(stmt)`: Generar IR para declaración
- `_emit_expr(expr)`: Generar IR para expresión, devolver operando de resultado

---

## 7. MÓDULO DE GENERACIÓN DE ENSAMBLADOR

**Archivo**: `minilang_compiler/codegen_asm.py`

### 7.1 ARQUITECTURA OBJETIVO

Arquitectura basada en acumulador con las siguientes características:

- Registro acumulador único
- Operandos basados en memoria
- Sin registros de propósito general

### 7.2 ARQUITECTURA DEL CONJUNTO DE INSTRUCCIONES

**Movimiento de Datos**:

- `LOAD addr`: ACC = MEM[addr]
- `STORE addr`: MEM[addr] = ACC

**Aritméticas**:

- `ADD addr`: ACC = ACC + MEM[addr]
- `SUB addr`: ACC = ACC - MEM[addr]
- `MUL addr`: ACC = ACC * MEM[addr]
- `DIV addr`: ACC = ACC / MEM[addr] (división entera)

**Flujo de Control**:

- `JMP label`: Salto incondicional
- `JLT label`: Saltar si ACC < 0
- `JGT label`: Saltar si ACC > 0
- `JLE label`: Saltar si ACC <= 0
- `JGE label`: Saltar si ACC >= 0
- `JEQ label`: Saltar si ACC == 0
- `JNE label`: Saltar si ACC != 0

**E/S**:

- `IN addr`: MEM[addr] = read_input()
- `OUT addr`: write_output(MEM[addr])

**Especiales**:

- `LABEL name`: Definir etiqueta (pseudo-instrucción)
- `HALT`: Detener ejecución

### 7.3 TRADUCCIÓN DE IR A ENSAMBLADOR

**Operaciones Binarias**:
IR: t3 = t1 + t2

Ensamblador:
  LOAD t1
  ADD t2
  STORE t3

**Menos Unario**:
IR: t2 = -t1

Ensamblador:
  LOAD const_0
  SUB t1
  STORE t2

**Operaciones Relacionales**:
IR: t3 = t1 < t2

Ensamblador:
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

### 7.4 MANEJO DE CONSTANTES

Las constantes se asignan como ubicaciones de memoria con nombres `const_0`, `const_1`, etc.

Las constantes se descubren durante la generación de ensamblador y se recopilan en un conjunto.

### 7.5 RECOPILACIÓN DE SÍMBOLOS

Todos los nombres de variables y temporales se recopilan durante la generación para la fase de asignación de memoria.

### 7.6 DETALLES DE IMPLEMENTACIÓN

**Clase**: `ASMGenerator`

**Atributos**:

- `lines`: Lista de instrucciones de ensamblador
- `syms`: Conjunto de nombres de símbolos
- `consts`: Conjunto de valores constantes

**Métodos**:

- `generate(ir)`: Convertir IR a ensamblador
- `_sym_for_const(value)`: Obtener/crear símbolo constante
- `_use_sym(name)`: Registrar uso de símbolo
- `_emit(line)`: Agregar instrucción a la salida

**Salida**: Tupla de (assembly_lines, symbols, constants)

---

## 8. MÓDULO DE GENERACIÓN DE CÓDIGO MÁQUINA

**Archivo**: `minilang_compiler/codegen_machine.py`

### 8.1 FORMATO DE BYTECODE

Array aplanado de enteros: `[opcode, operando, opcode, operando, ...]`

Cada instrucción ocupa dos ranuras de array.

### 8.2 MAPEO DE OPCODES

LOAD:  1    STORE: 2    ADD:   3    SUB:   4
MUL:   5    DIV:   6    JMP:   7    JLT:   8
JGT:   9    JLE:   10   JGE:   11   JEQ:   12
JNE:   13   IN:    14   OUT:   15   HALT:  16

### 8.3 PROCESO DE ENSAMBLADO

**Fase 1: Recopilación de Instrucciones**
Analizar líneas de ensamblador para construir lista de instrucciones con opcodes y nombres de operandos.

Rastrear posiciones de etiquetas (índice de instrucción).
**Fase 2: Enlace**

Resolver todos los nombres de operandos:

- Etiquetas → direcciones de instrucción
- Variables → direcciones de memoria
- Temporales → direcciones de memoria
- Constantes → direcciones de memoria

### 8.4 ASIGNACIÓN DE MEMORIA

Direcciones de memoria asignadas secuencialmente comenzando desde 0.

Orden de asignación:

1. Constantes (con valores de inicialización)
2. Variables (ordenadas alfabéticamente)
3. Temporales (ordenados numéricamente)

### 8.5 RESOLUCIÓN DE ETIQUETAS

Las etiquetas se mapean a índices de instrucción (no desplazamientos de bytes).

Los operandos de salto contienen el índice de instrucción objetivo.

### 8.6 ESTRUCTURA DEL PROGRAMA MÁQUINA

**Clase**: `MachineProgram`

**Atributos**:

- `code`: Array de bytecode
- `sym_addrs`: Diccionario que mapea nombres de símbolos a direcciones de memoria
- `mem_init`: Diccionario que mapea direcciones a valores iniciales
- `labels`: Diccionario que mapea nombres de etiquetas a direcciones de instrucción

### 8.7 DETALLES DE IMPLEMENTACIÓN

**Clase**: `Assembler`

**Métodos**:

- `assemble(asm_lines)`: Analizar ensamblador a instrucciones y etiquetas
- `link(instrs, labels, syms, const_values)`: Resolver direcciones y generar bytecode

---

## 9. MÓDULO DE MÁQUINA VIRTUAL

**Archivo**: `minilang_compiler/runtime_vm.py`

### 9.1 ARQUITECTURA DE LA VM

**Componentes**:

- Contador de Programa (PC): Dirección de instrucción actual
- Acumulador (ACC): Registro único para cálculos
- Memoria (MEM): Array de enteros
- Proveedor de Entrada: Función que suministra valores de entrada
- Buffer de Salida: Lista que recopila valores de salida

### 9.2 CICLO DE EJECUCIÓN

```python
mientras PC < longitud_código:
    opcode = código[PC]
    operando = código[PC + 1]
    PC += 2
    
    ejecutar(opcode, operando)
    
    si opcode == HALT:
        romper
```

### 9.3 EJECUCIÓN DE INSTRUCCIONES

**Operaciones de Datos**:

- LOAD: `ACC = MEM[operando]`
- STORE: `MEM[operando] = ACC`
- ADD: `ACC = ACC + MEM[operando]`
- SUB: `ACC = ACC - MEM[operando]`
- MUL: `ACC = ACC * MEM[operando]`
- DIV: `ACC = ACC / MEM[operando]` (lanza excepción si MEM[operando] == 0)

**Operaciones de Control**:

- JMP: `PC = operando * 2` (convertir índice de instrucción a desplazamiento de bytes)
- JLT: `si ACC < 0: PC = operando * 2`
- JGT: `si ACC > 0: PC = operando * 2`
- JLE: `si ACC <= 0: PC = operando * 2`
- JGE: `si ACC >= 0: PC = operando * 2`
- JEQ: `si ACC == 0: PC = operando * 2`
- JNE: `si ACC != 0: PC = operando * 2`

**Operaciones de E/S**:

- IN: `MEM[operando] = proveedor_entrada()`
- OUT: `buffer_salida.append(MEM[operando])`

**Especiales**:

- HALT: Terminar ejecución

### 9.4 INICIALIZACIÓN DE MEMORIA

Memoria pre-poblada con valores constantes antes de la ejecución.

Tamaño determinado por la dirección asignada más alta + 1.

### 9.5 MECANISMO DE ENTRADA

Entrada proporcionada mediante función invocable. Dos modos:

1. Interactivo: Leer desde stdin
2. Por lotes: Leer desde lista pre-suministrada

### 9.6 MODO DE RASTREO

El rastreo de ejecución opcional registra después de cada instrucción:

- Valor de PC
- Opcode y operando
- Valor del acumulador
- Instantánea de memoria (primeras 32 celdas)

### 9.7 MANEJO DE ERRORES

Errores en tiempo de ejecución:

- División por cero
- Opcode desconocido
- Agotamiento de entrada (en modo por lotes)

### 9.8 DETALLES DE IMPLEMENTACIÓN

**Clase**: `VM`

**Atributos**:

- `code`: Array de bytecode
- `pc`: Contador de programa
- `acc`: Acumulador
- `mem`: Array de memoria
- `outputs`: Buffer de salida
- `trace`: Registro de rastreo opcional
- `input_provider`: Función de entrada

**Métodos**:

- `run()`: Ejecutar programa, devolver VMResult

**Clase**: `VMResult`

**Atributos**:

- `outputs`: Lista de valores de salida
- `trace`: Rastreo de ejecución opcional

---

## 10. MÓDULO DE ORQUESTACIÓN DEL COMPILADOR

**Archivo**: `minilang_compiler/compiler.py`

### 10.1 PIPELINE DE COMPILACIÓN

```python
def compile_pipeline(source_code, optimize, run, inputs, emit, trace_ir, trace_asm, trace_vm, out_dir):
    # Etapa 1: Análisis Léxico
    tokens = Lexer(source_code).tokenize()
    
    # Etapa 2: Análisis Sintáctico
    program = Parser(tokens, source_code).parse()
    
    # Etapa 3: Optimización (opcional)
    if optimize:
        program = fold_constants_prog(program)
    
    # Etapa 4: Análisis Semántico
    sem_result = SemanticAnalyzer().analyze(program)
    
    # Etapa 5: Generación de IR
    ir = IRGenerator().generate(program)
    
    # Etapa 6: Generación de Ensamblador
    asm_lines, syms, consts = ASMGenerator().generate(ir)
    
    # Etapa 7: Generación de Código Máquina
    assembler = Assembler()
    instrs, labels, collected_syms = assembler.assemble(asm_lines)
    const_values = {f"const_{v}": v for v in consts}
    machine_prog = assembler.link(instrs, labels, collected_syms, const_values)
    
    # Etapa 8: Ejecución (opcional)
    if run:
        vm = VM(machine_prog.code, memory_size, machine_prog.mem_init, input_provider, trace_vm)
        result = vm.run()
        return result
    
    return artifacts
```

### 10.2 INTERFAZ DE LÍNEA DE COMANDOS

**Argumentos**:

- `file`: Ruta del archivo fuente (requerido)
- `--no-opt`: Deshabilitar optimizaciones
- `--emit STAGE`: Emitir salida de etapa específica
- `--emit-all`: Escribir todas las etapas en archivos
- `--out-dir DIR`: Directorio de salida para `--emit-all`
- `--run`: Ejecutar programa en VM
- `--trace-ir`: Imprimir IR después de la generación
- `--trace-asm`: Imprimir ensamblador después de la generación
- `--trace-vm`: Imprimir rastreo de ejecución de VM
- `--inputs N1 N2 ...`: Proporcionar valores de entrada

**Etapas para --emit**:

- `tokens`: Flujo de tokens
- `ast`: Árbol de sintaxis abstracta
- `ir`: Representación intermedia
- `asm`: Código de ensamblador
- `machine`: Código máquina (bytecode + tabla de símbolos)

### 10.3 MANEJO DE ERRORES

Errores de compilación capturados y reportados:

- `LexError`: Fallo de análisis léxico
- `ParseError`: Fallo de análisis sintáctico
- `SemanticError`: Fallo de validación semántica

Códigos de salida:

- 0: Éxito
- 1: Error de compilación
- 2: Error inesperado (error interno)

### 10.4 MODOS DE SALIDA

**Modo Interactivo** (sin --emit):

- Si `--run`: Imprimir salidas del programa línea por línea
- De lo contrario: Sin salida (solo verificación de compilación)

**Modo Emit** (--emit STAGE):

- Imprimir etapa solicitada a stdout

**Modo Emit-All** (--emit-all):

- Escribir todas las etapas en archivos separados en `--out-dir`
- Archivos: tokens.txt, ast.txt, ir.txt, asm.txt, machine.txt

---

## 11. MÓDULO DE INTERFAZ WEB

**Archivo**: `web_app.py`

### 11.1 ARQUITECTURA

Aplicación web basada en Flask que proporciona interfaz de compilador accesible desde el navegador.

**Rutas**:

- `GET /`: Página principal (sirve index.html)
- `POST /compile`: Endpoint de compilación
- `GET /examples`: Cargar programas de ejemplo

### 11.2 ENDPOINT DE COMPILACIÓN

**Formato de Solicitud** (JSON):

```json
{
    "code": "cadena de código fuente",
    "inputs": "3 7" o [3, 7],
    "show_stages": true/false
}
```

**Formato de Respuesta** (JSON):

```json
{
    "success": true,
    "outputs": [17, 0, 1, 2, ...],
    "stages": {
        "tokens": "listado de tokens",
        "ast": "representación AST",
        "ir": "listado TAC",
        "asm": "listado de ensamblador",
        "machine": "info de código máquina",
        "warnings": "advertencias semánticas"
    }
}
```

**Respuesta de Error**:

```json
{
    "success": false,
    "error": "mensaje de error"
}
```

### 11.3 ENDPOINT DE EJEMPLOS

Devuelve objeto JSON con 5 programas de ejemplo preconfigurados:

- program1: Demostración completa de características
- program2: If-else anidado
- program3: While con cero iteraciones
- program4: Precedencia de operadores
- program5: Echo de E/S

Cada ejemplo incluye:

- `name`: Nombre de visualización
- `code`: Código fuente
- `inputs`: Valores de entrada
- `description`: Explicación breve

### 11.4 IMPLEMENTACIÓN DEL FRONTEND

**Archivo**: `templates/index.html`

Aplicación de una sola página con:

- Editor de código (textarea)
- Campo de entrada para valores de lectura
- Casilla de verificación para visualización de etapas
- Botones de selección de ejemplo
- Botón de Compilar/Ejecutar
- Botón de Limpiar
- Área de visualización de salida
- Paneles de etapas colapsables

**Funciones JavaScript**:

- `loadExamples()`: Obtener y poblar botones de ejemplo
- `loadExample(example)`: Cargar ejemplo en el editor
- `compileCode()`: Enviar solicitud de compilación al backend
- `createStageDiv(title, content)`: Crear panel de etapa colapsable
- `clearAll()`: Reiniciar interfaz

**Atajos de Teclado**:

- Ctrl+Enter: Compilar y ejecutar

---

## 12. MARCO DE PRUEBAS

**Directorio**: `tests/`

### 12.1 MÓDULOS DE PRUEBA

**test_lexer.py**:

- Reconocimiento básico de tokens
- Manejo de comentarios
- Seguimiento de posición
- Detección de errores (caracteres inválidos)

**test_parser.py**:

- Análisis de programa mínimo
- Estructuras de declaración y bloque
- Detección de errores (punto y coma faltante)

**test_semantic.py**:

- Generación de advertencia de inicialización
- Variables adecuadamente inicializadas (sin advertencias)

**test_ir_vm.py**:

- Prueba de pipeline de extremo a extremo
- Verificación de ejecución del programa
- Validación de salida

### 12.2 EJECUCIÓN DE PRUEBAS

```bash
pytest -v
```

Todas las pruebas deben pasar antes del despliegue.

---

## 13. CONSTRUCCIÓN Y DESPLIEGUE

### 13.1 ESTRUCTURA DEL PAQUETE

**pyproject.toml**:

- Metadatos del proyecto
- Requisito de versión de Python: >=3.10
- Punto de entrada: comando `minilangc`
- Sistema de construcción: setuptools

**requirements.txt**:

- Flask >=3.1.0
- pytest >=8.4.0

### 13.2 INSTALACIÓN

```bash
pip install -r requirements.txt
pip install -e .
```

El modo editable (`-e`) permite el desarrollo sin reinstalación.

### 13.3 INTEGRACIÓN CONTINUA

**Archivo**: `.github/workflows/ci.yml`

Flujo de trabajo de GitHub Actions:

- Disparador: Push o pull request a la rama main
- Plataforma: Windows
- Versiones de Python: 3.10, 3.11, 3.12, 3.13
- Pasos:
  1. Checkout del código
  2. Configuración de Python
  3. Instalación de dependencias
  4. Ejecución de pytest

---

## 14. LIMITACIONES Y RESTRICCIONES

### 14.1 LIMITACIONES DEL LENGUAJE

- Tipo de dato único (solo entero)
- Sin soporte de punto flotante
- Sin soporte de cadenas
- Sin arrays o tipos compuestos
- Sin funciones o procedimientos
- Sin recursión
- Solo alcance global
- Sin alcances anidados

### 14.2 LIMITACIONES DE IMPLEMENTACIÓN

- Sin verificación de tipos (tipo único hace esto innecesario)
- Sin asignación de registros (arquitectura de acumulador)
- Optimizaciones limitadas (solo plegado de constantes)
- Sin eliminación de código muerto
- Sin eliminación de subexpresiones comunes
- Sin optimizaciones de bucles
- Sin optimizaciones de mirilla

### 14.3 LIMITACIONES EN TIEMPO DE EJECUCIÓN

- Semántica de división entera (truncamiento hacia cero)
- Sin detección de desbordamiento
- División por cero lanza excepción
- Tamaño de memoria fijo en tiempo de compilación
- Sin asignación dinámica de memoria
- Sin recolección de basura

### 14.4 DECISIONES ARQUITECTÓNICAS

**Acumulador vs Máquina de Registros**:

- Acumulador elegido por simplicidad
- Reduce complejidad de instrucciones
- Elimina fase de asignación de registros
- Compensación: Más operaciones de memoria

**TAC como IR**:

- Formato simple de tres direcciones
- Fácil de generar desde AST
- Traducción directa a ensamblador
- Representación independiente de plataforma

**Máquina Virtual vs Código Nativo**:

- VM proporciona portabilidad
- Implementación más simple
- Depuración más fácil
- Compensación: Ejecución más lenta

---

## 15. PUNTOS DE EXTENSIÓN

### 15.1 MEJORAS POTENCIALES

**Características del Lenguaje**:

- Tipos de datos adicionales (float, string, boolean)
- Arrays e indexación
- Funciones con parámetros y valores de retorno
- Alcance local y alcance léxico
- Estructuras o registros
- Bucles for
- Declaraciones break/continue

**Optimización**:

- Propagación de constantes
- Eliminación de código muerto
- Eliminación de subexpresiones comunes
- Reducción de fuerza
- Movimiento de código invariante de bucles
- Optimización de mirilla

**Generación de Código**:

- Asignación de registros
- Programación de instrucciones
- Generación de código nativo (x86, ARM)
- Backend LLVM

**Análisis**:

- Inferencia de tipos
- Análisis de flujo de datos
- Construcción de grafo de flujo de control
- Análisis de variables vivas
- Definiciones alcanzables

**Herramientas**:

- Depurador con puntos de interrupción
- Perfilador para análisis de rendimiento
- Visualización de AST/CFG
- REPL interactivo

---

## FIN DEL DOCUMENTO

**Control del Documento**:

- Clasificación: Especificación Técnica
- Distribución: Equipo del Proyecto
- Última Actualización: Noviembre 2025
- Versión: 1.0
