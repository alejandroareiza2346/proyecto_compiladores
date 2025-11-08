# Compilador MiniLang

Este es mi proyecto de compilador para el lenguaje MiniLang. Implementa todas las fases de compilación desde análisis léxico hasta ejecución en una máquina virtual.

**✨ NUEVO: Ahora incluye una interfaz web interactiva!** 🚀

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

# Para la interfaz web, instalar Flask
pip install Flask

# Para correr tests
pip install pytest
```

## 🌐 Interfaz Web (Recomendado)

La forma más fácil de usar el compilador es con la interfaz web:

```powershell
# Iniciar el servidor
python web_app.py

# Abre tu navegador en: http://127.0.0.1:5000
```

**Características de la interfaz:**

- 📝 Editor de código integrado
- 🎨 5 programas de ejemplo listos para usar
- ▶️ Compilación y ejecución con un clic
- 🔍 Visualización de todas las etapas (Tokens, AST, IR, Assembly, Machine Code)
- 💾 Entrada de valores interactiva para `read`
- ⚡ Resultados en tiempo real con formato
- ⌨️ Atajo de teclado: `Ctrl + Enter` para compilar

## 💻 Uso por Línea de Comandos

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
