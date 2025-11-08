"""
Interfaz Web para el Compilador MiniLang
Corre con: python web_app.py
"""
from flask import Flask, render_template, request, jsonify
from minilang_compiler.compiler import compile_pipeline
from minilang_compiler.lexer import LexError
from minilang_compiler.parser import ParseError
from minilang_compiler.semantic import SemanticError

app = Flask(__name__)


@app.route('/')
def index():
    """Página principal con el editor"""
    return render_template('index.html')


@app.route('/compile', methods=['POST'])
def compile_code():
    """Endpoint para compilar y ejecutar código MiniLang"""
    data = request.json
    source_code = data.get('code', '')
    inputs = data.get('inputs', [])
    show_stages = data.get('show_stages', False)
    
    # Parsear inputs (viene como string separado por comas o espacios)
    if isinstance(inputs, str):
        inputs = [int(x.strip()) for x in inputs.replace(',', ' ').split() if x.strip().isdigit()]
    
    try:
        # Compilar y ejecutar
        result = compile_pipeline(
            source_code=source_code,
            optimize=True,
            run=True,
            inputs=inputs,
            trace_ir=False,
            trace_asm=False,
            trace_vm=False
        )
        
        response = {
            'success': True,
            'outputs': result.outputs if hasattr(result, 'outputs') else []
        }
        
        # Si se piden las etapas intermedias
        if show_stages:
            all_results = compile_pipeline(
                source_code=source_code,
                optimize=True,
                run=False
            )
            
            # Tokens
            tokens_str = '\n'.join(str(t) for t in all_results['tokens'][:50])  # Limitar a 50
            if len(all_results['tokens']) > 50:
                tokens_str += '\n... (más tokens)'
            
            # AST
            ast_str = str(all_results['ast'])
            
            # IR (TAC)
            ir_str = '\n'.join(str(ins) for ins in all_results['ir'])
            
            # Assembly
            asm_str = '\n'.join(all_results['asm'])
            
            # Machine code
            machine = all_results['machine']
            machine_str = f"CODE: {machine.code[:40]}{'...' if len(machine.code) > 40 else ''}\n"
            machine_str += f"SYMBOLS: {machine.sym_addrs}\n"
            machine_str += f"CONSTANTS: {machine.mem_init}"
            
            # Warnings semánticas
            warnings = all_results['sem_warnings']
            warnings_str = '\n'.join(warnings) if warnings else 'Sin advertencias'
            
            response['stages'] = {
                'tokens': tokens_str,
                'ast': ast_str,
                'ir': ir_str,
                'asm': asm_str,
                'machine': machine_str,
                'warnings': warnings_str
            }
        
        return jsonify(response)
    
    except (LexError, ParseError, SemanticError) as e:
        return jsonify({
            'success': False,
            'error': f'Error de compilación: {str(e)}'
        })
    except RuntimeError as e:
        return jsonify({
            'success': False,
            'error': f'Error de ejecución: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error inesperado: {str(e)}'
        })


@app.route('/examples')
def get_examples():
    """Devuelve programas de ejemplo"""
    examples = {
        'program1': {
            'name': 'Programa Completo',
            'code': '''read a;
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
end''',
            'inputs': '3 7',
            'description': 'Programa con aritmética, if-else y while'
        },
        'program2': {
            'name': 'If-Else Anidado',
            'code': '''read x;
read y;
sum = x + y;
if sum > 10 {
    print sum;
    if x < y {
        print 1;
    } else {
        print 0;
    }
} else {
    print 0;
}
end''',
            'inputs': '5 10',
            'description': 'Estructuras if-else anidadas'
        },
        'program3': {
            'name': 'While con Cero Iteraciones',
            'code': '''read n;
i = 0;
while i < n {
    print i;
    i = i + 1;
}
print 999;
end''',
            'inputs': '0',
            'description': 'Loop que nunca se ejecuta'
        },
        'program4': {
            'name': 'Precedencia de Operadores',
            'code': '''a = 2 + 3 * 4;
print a;
b = 10 - 2 * 3;
print b;
c = 20 / 4 + 1;
print c;
d = (2 + 3) * 4;
print d;
e = 10 == 5 + 5;
print e;
f = 3 < 2 + 2;
print f;
end''',
            'inputs': '',
            'description': 'Prueba de precedencia de operadores'
        },
        'program5': {
            'name': 'Echo Simple',
            'code': '''read a;
print a;
read b;
print b;
read c;
print c;
end''',
            'inputs': '42 7 0',
            'description': 'Lee y escribe valores'
        }
    }
    return jsonify(examples)


if __name__ == '__main__':
    print("🚀 Iniciando Compilador MiniLang Web...")
    print("📝 Abre tu navegador en: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
