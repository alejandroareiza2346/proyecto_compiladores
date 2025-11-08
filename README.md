# MINILANG COMPILER

## INSTALLATION

Clone repository:
```
git clone https://github.com/alejandroareiza2346/proyecto_compiladores.git
cd proyecto_compiladores
```

Setup virtual environment:
```
python -m venv .venv
```

Activate (Windows):
```
.venv\Scripts\Activate.ps1
```

Activate (Linux/Mac):
```
source .venv/bin/activate
```

Install:
```
pip install -r requirements.txt
pip install -e .
```

## USAGE

### Web Interface
```
python web_app.py
```
Access: 127.0.0.1:5000

### CLI
Execute program:
```
python -m minilang_compiler.compiler examples/program1.minilang --run --inputs 3 7
```

Emit tokens:
```
python -m minilang_compiler.compiler file.minilang --emit tokens
```

Emit AST:
```
python -m minilang_compiler.compiler file.minilang --emit ast
```

Emit IR:
```
python -m minilang_compiler.compiler file.minilang --emit ir
```

Emit assembly:
```
python -m minilang_compiler.compiler file.minilang --emit asm
```

Emit machine code:
```
python -m minilang_compiler.compiler file.minilang --emit machine
```

Trace execution:
```
python -m minilang_compiler.compiler file.minilang --run --trace-vm --inputs 5 10
```

### Test Suite
```
pytest -v
```

## END OF DOCUMENT
