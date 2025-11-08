# Informe Técnico - Compilador MiniLang

**Autor:** Alejo  
**Curso:** Compiladores 2025-2  
**Fecha:** Noviembre 2025

## 1. Introducción

Este documento describe el diseño e implementación de un compilador completo para el lenguaje MiniLang. El lenguaje es bastante simple pero tiene todo lo básico: variables enteras, operaciones aritméticas y relacionales, control de flujo (if-else y while), entrada/salida.

Características del lenguaje:

- Solo hay un tipo: enteros
- Operadores aritméticos: `+`, `-`, `*`, `/` (división entera)
- Comparaciones: `<`, `>`, `<=`, `>=`, `==`, `!=` (devuelven 0 o 1)
- I/O: `read variable;` y `print expresion;`
- Control de flujo: `if condicion { ... } else { ... }` y `while condicion { ... }`
- Todo programa termina con `end`

Las variables se "declaran" automáticamente cuando las lees con `read` o cuando les asignas un valor. Si intentas usar una antes de darle valor, el compilador te avisa.

## 2. Gramática

La gramática que usé es esta (EBNF):

```ebnf
program    := stmt* 'end' EOF
stmt       := 'read' IDENT ';'
           | 'print' expr ';'
           | IDENT '=' expr ';'
           | 'if' expr '{' stmt* '}' 'else' '{' stmt* '}'
           | 'while' expr '{' stmt* '}'
expr       := equality
equality   := comparison ( ( '==' | '!=' ) comparison )*
comparison := term ( ( '<' | '>' | '<=' | '>=' ) term )*
term       := factor ( ( '+' | '-' ) factor )*
factor     := unary ( ( '*' | '/' ) unary )*
unary      := '-' unary | primary
primary    := NUMBER | IDENT | '(' expr ')'
```

La precedencia de operadores es la estándar: `*` y `/` antes que `+` y `-`, luego comparaciones, y finalmente igualdad. Los paréntesis se pueden usar para cambiar el orden.

## 3. Arquitectura del compilador

El proyecto está dividido en módulos, cada uno hace una parte del trabajo:

**Análisis Léxico (`lexer.py`, `tokens.py`)**  
El lexer lee el código y lo convierte en tokens. Maneja comentarios de una línea (`//`) y de múltiples (`/* */`). Si encuentra algo raro, te dice exactamente en qué línea y columna.

**Análisis Sintáctico (`parser.py`, `ast_nodes.py`)**  
Parser recursivo descendente que arma el árbol sintáctico abstracto (AST). Cada nodo representa una construcción del lenguaje (asignación, if, while, etc.).

**Análisis Semántico (`semantic.py`)**  
Revisa que no estés usando variables sin inicializar. Lleva una tabla de símbolos y te avisa si algo parece sospechoso.

**Optimización (`optimizer.py`)**  
Por ahora solo hace constant folding: si escribes `2 + 3` lo reemplaza por `5` directamente. Se podría agregar más optimizaciones acá en el futuro.

**Código Intermedio (`ir.py`)**  
Genera TAC (Three-Address Code) con temporales (`t1`, `t2`, ...) y etiquetas (`L1`, `L2`, ...). Es más fácil trabajar con esto que con el AST para las siguientes etapas.

**Generación de Ensamblador (`codegen_asm.py`)**  
Convierte el TAC a ensamblador de una máquina con acumulador. Usa instrucciones tipo LOAD, STORE, ADD, etc.

**Código Máquina (`codegen_machine.py`)**  
El "ensamblador" que convierte las instrucciones textuales a números (opcodes). También resuelve las etiquetas a direcciones reales.

**Máquina Virtual (`runtime_vm.py`)**  
Una VM simple que ejecuta el código máquina. Tiene un acumulador, memoria, y puede hacer I/O básico.

**Orquestador (`compiler.py`)**  
El main que junta todo y maneja la línea de comandos.

## 4. La máquina virtual

La VM es una máquina con acumulador. Las instrucciones que soporta son:

**Operaciones con datos:**

- `LOAD addr` - Carga de memoria al acumulador
- `STORE addr` - Guarda el acumulador en memoria
- `ADD addr`, `SUB addr`, `MUL addr`, `DIV addr` - Operaciones aritméticas

**Saltos condicionales:**

- `JMP L` - Salto incondicional
- `JLT`, `JGT`, `JLE`, `JGE`, `JEQ`, `JNE` - Saltan si el acumulador cumple la condición vs. 0

**Entrada/Salida:**

- `IN addr` - Lee un entero y lo guarda en memoria
- `OUT addr` - Imprime el valor de memoria

**Control:**

- `LABEL X` - Marca una posición (no genera código)
- `HALT` - Para la ejecución

Cada instrucción se codifica como un par `[opcode, operando]`. Por ejemplo LOAD es 1, STORE es 2 y así. Los saltos guardan la dirección destino en el operando.

## 5. Ejemplo paso a paso

Tomemos este programa (`program1.minilang`):

```minilang
read a;
read b;
c = a + b * 2;
if c >= 10 {
    print c;
} else {
    print 0;
}
i = 0;
while i < c {
    print i;
    i = i + 1;
}
end
```

**Lo que pasa en cada etapa:**

1. **Tokens**: El lexer identifica cada palabra clave, operador, número e identificador
2. **AST**: Se construye el árbol con nodos para cada asignación, if-else, while, etc.
3. **Semántica**: Verifica que `a`, `b`, `c`, `i` existan cuando se usan. Todo ok.
4. **TAC**: Genera código de tres direcciones, algo así:

   ```text
   read a
   read b
   t1 = b * const_2
   t2 = a + t1
   c = t2
   ...
   ```

5. **Ensamblador**: Convierte a instrucciones LOAD/ADD/STORE con etiquetas para los saltos
6. **Código máquina**: Números puros. Las variables y temporales tienen direcciones de memoria fijas.

Al final la VM ejecuta esos números y produce la salida del programa.

## 6. Limitaciones y decisiones de diseño

Algunas cosas a tener en cuenta:

- La división es entera (como en C). Si divides por cero, la VM lanza una excepción.
- El análisis de inicialización es conservador: dentro de un if o while asume que tal vez no se ejecuta.
- Las optimizaciones son básicas por ahora (solo constant folding).
- La VM usa enteros de Python, así que no hay límite de tamaño ni overflow.

## 7. Instrucciones de uso

Ejemplos de cómo correr el compilador:

```powershell
# Ver solo los tokens
python -m minilang_compiler.compiler examples/program1.minilang --emit tokens

# Ejecutar el programa con entradas 3 y 7
python -m minilang_compiler.compiler examples/program1.minilang --run --inputs 3 7

# Guardar todas las etapas en archivos
python -m minilang_compiler.compiler examples/program1.minilang --emit-all --out-dir output

# Ver la traza completa de ejecución
python -m minilang_compiler.compiler examples/program1.minilang --run --trace-vm --inputs 3 7
```

Para el ejemplo anterior con entradas `a=3, b=7`: calcula `c = 3 + 7*2 = 17`, imprime `17` (porque 17 >= 10) y luego imprime los números del 0 al 16 en el while.

## 8. Testing

Armé una suite de tests con pytest que cubre las partes principales:

- `test_lexer.py` - Prueba el tokenizer con casos normales y de error
- `test_parser.py` - Verifica que el parser construya el AST bien y detecte errores de sintaxis
- `test_semantic.py` - Chequea las advertencias de variables no inicializadas
- `test_ir_vm.py` - Tests end-to-end: compila y ejecuta programas completos, verifica la salida

En total son 9 tests. Se corren con `pytest -q` y todos pasan.

También configuré GitHub Actions para que corra los tests automáticamente en cada push con varias versiones de Python (3.10-3.13) en Windows.

## 9. Conclusiones

El proyecto cumple con todo lo pedido: tiene las 6 etapas clásicas de compilación funcionando, una VM que ejecuta el código, tests automatizados, y documentación completa.

Lo que más me costó fue hacer que el análisis semántico fuera lo suficientemente inteligente para detectar variables sin inicializar pero sin dar falsos positivos. También fue interesante diseñar el set de instrucciones de la máquina virtual para que fuera simple pero capaz de soportar todo el lenguaje.

**Posibles mejoras futuras:**

Si tuviera más tiempo agregaría:

- Más optimizaciones en el código intermedio (propagación de constantes, dead code elimination)
- Soporte para funciones y tipos de datos adicionales
- Un debugger interactivo para la VM
- Generación de código para una arquitectura real en vez de una VM custom

Pero para los objetivos de este curso, el compilador hace todo lo que debe hacer y funciona bien.
