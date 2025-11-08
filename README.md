# Compilador MiniLang

Este es mi proyecto de compilador para el lenguaje MiniLang. Implementa todas las fases de compilación desde análisis léxico hasta ejecución en una máquina virtual.

## ¿Qué hace?

El compilador procesa archivos `.minilang` y los ejecuta pasando por estas etapas:

- Análisis léxico: tokeniza el código (soporta comentarios `//` y `/* */`)
- Parser recursivo descendente que arma el AST
- Análisis semántico con tabla de símbolos y chequeo de inicialización
- Generación de código intermedio (TAC)
- Optimizaciones básicas (constant folding)
- Generación de ensamblador para arquitectura de acumulador
- Traducción a código máquina
- Máquina virtual que ejecuta el programa

## Requisitos

Necesitas Python 3.10 o superior.

## Organización del proyecto

```text
project_final/
├── minilang_compiler/    # Todos los módulos del compilador
├── examples/             # Programas de prueba
├── tests/                # Tests con pytest
└── docs/                 # Documentación técnica
```

## Instalación

```powershell
cd project_final

# Crear un entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# Instalar el compilador
pip install -e .

# Para correr tests
pip install pytest
```

## Cómo usarlo

### Ejecutar un programa

La forma más simple es:

```powershell
python -m minilang_compiler.compiler .\examples\program1.minilang --run --inputs 3 7
```

También funciona con el comando `minilangc` después de instalar.

### Ver las diferentes etapas

Si quieres ver lo que genera cada fase del compilador:

```powershell
# Ver tokens
python -m minilang_compiler.compiler .\examples\program1.minilang --emit tokens

# Ver el AST
python -m minilang_compiler.compiler .\examples\program1.minilang --emit ast

# Ver código intermedio (TAC)
python -m minilang_compiler.compiler .\examples\program1.minilang --emit ir

# Ver ensamblador
python -m minilang_compiler.compiler .\examples\program1.minilang --emit asm

# Ver código máquina
python -m minilang_compiler.compiler .\examples\program1.minilang --emit machine
```

Hay flags de debugging también (`--trace-ir`, `--trace-asm`, `--trace-vm`) que muestran más detalles de cada paso.

### Tests

Para correr los tests:

```powershell
pytest -q
```

## Programas de ejemplo

Hay 5 programas en la carpeta `examples/`:

1. `program1.minilang` - Un programa con todo: aritmética, if-else y while
2. `program2_nested_if.minilang` - If-else anidados
3. `program3_while_zero.minilang` - Loop que nunca se ejecuta
4. `program4_precedence.minilang` - Prueba de precedencia de operadores
5. `program5_echo.minilang` - Lee y escribe valores

## Algunas notas importantes

- El `read` solo acepta enteros. Usa `--inputs` para pasarlos por línea de comandos.
- Las constantes se guardan en memoria con nombres tipo `const_0`, `const_1`, etc.
- Si usas una variable antes de darle valor, te salta una advertencia.
- Los errores te muestran la línea exacta con un indicador de dónde está el problema.
