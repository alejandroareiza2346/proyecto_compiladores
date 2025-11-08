# MINILANG COMPILER# MINILANG COMPILER

## INSTALLATION## INSTALLATION

Clone repository:Clone repository:

```bashgit clone https://github.com/alejandroareiza2346/proyecto_compiladores.git

git clone https://github.com/alejandroareiza2346/proyecto_compiladores.gitcd proyecto_compiladores

cd proyecto_compiladores```

```

Setup virtual environment:

Setup virtual environment:```

python -m venv .venv

```bash```

python -m venv .venv

```Activate (Windows):

```

Activate (Windows):.venv\Scripts\Activate.ps1

```powershell

.venv\Scripts\Activate.ps1Activate (Linux/Mac):

``````

source .venv/bin/activate

Activate (Linux/Mac):```

```bashInstall:

source .venv/bin/activate```

```pip install -r requirements.txt

pip install -e .

Install:```



```bash## USAGE

pip install -r requirements.txt

pip install -e .### Web Interface

``````

python web_app.py

## USAGE```

Access: 127.0.0.1:5000

### Web Interface

### CLI

```bashExecute program:

python web_app.py```

```python -m minilang_compiler.compiler examples/program1.minilang --run --inputs 3 7

```

Access: 127.0.0.1:5000

Emit tokens:

### CLI```

python -m minilang_compiler.compiler file.minilang --emit tokens

Execute program:```

```bashEmit AST:

python -m minilang_compiler.compiler examples/program1.minilang --run --inputs 3 7```

```python -m minilang_compiler.compiler file.minilang --emit ast

```

Emit tokens:

Emit IR:

```bash```

python -m minilang_compiler.compiler file.minilang --emit tokens
python -m minilang_compiler.compiler file.minilang --emit ir

Emit AST:Emit assembly:

```bashpython -m minilang_compiler.compiler file.minilang --emit asm

python -m minilang_compiler.compiler file.minilang --emit ast```

```

Emit machine code:

Emit IR:```

python -m minilang_compiler.compiler file.minilang --emit machine

```bash```

python -m minilang_compiler.compiler file.minilang --emit ir

```Trace execution:

```

Emit assembly:python -m minilang_compiler.compiler file.minilang --run --trace-vm --inputs 5 10

```bash

python -m minilang_compiler.compiler file.minilang --emit asm### Test Suite

``````

pytest -v

Emit machine code:```

```bash## END OF DOCUMENT

python -m minilang_compiler.compiler file.minilang --emit machine
```

Trace execution:

```bash
python -m minilang_compiler.compiler file.minilang --run --trace-vm --inputs 5 10
```

### Test Suite

```bash
pytest -v
```

## END OF DOCUMENT
