"""
MÓDULO DE FORMATEO DE ERRORES
Proyecto: Compilador MiniLang
Universidad: [Nombre de la Universidad]
Curso: Compiladores

PROPÓSITO:
Proporciona funciones utilitarias para formatear mensajes de error de manera legible,
mostrando el contexto del código fuente donde ocurrió el error.

FUNCIONALIDAD:
- Extrae la línea relevante del código fuente
- Señala la posición exacta del error con un indicador visual (^)
- Maneja casos especiales como fuente no disponible o posiciones fuera de rango

EJEMPLO DE SALIDA:
    Line 3, Col 5:
    x = 5 +;
        ^
"""

from typing import Optional


def format_error(source: Optional[str], line: int, column: int) -> str:
    """
    Formatea un mensaje de error con contexto del código fuente.
    
    Parámetros:
        source: Código fuente completo (puede ser None)
        line: Número de línea donde ocurrió el error (indexado desde 1)
        column: Número de columna donde ocurrió el error (indexado desde 1)
    
    Retorna:
        Cadena formateada con el mensaje de error, mostrando:
        - Número de línea y columna
        - La línea de código donde ocurrió el error
        - Un indicador (^) señalando la posición exacta
    
    Casos especiales:
        - Si source es None: retorna solo la posición
        - Si line está fuera de rango: retorna solo la posición
    
    Ejemplo:
        source = "x = 5 +\ny = 10"
        format_error(source, 1, 7)
        # Retorna:
        # Line 1, Col 7:
        # x = 5 +
        #       ^
    """
    # Caso 1: No hay código fuente disponible
    if source is None:
        return f"Error at {line}:{column}"
    
    # Dividir el código fuente en líneas
    lines = source.splitlines()
    
    # Caso 2: Número de línea inválido
    # Convertimos de indexado-1 a indexado-0 para acceder al array
    if line - 1 < 0 or line - 1 >= len(lines):
        return f"Error at {line}:{column}"
    
    # Extraer la línea específica donde ocurrió el error
    text = lines[line - 1]
    
    # Asegurar que la columna sea al menos 1
    # (protección contra valores inválidos)
    col = max(1, column)
    
    # Construir la línea del indicador (^)
    # Se colocan espacios hasta la columna del error, luego el símbolo ^
    # Nota: col - 1 porque la columna está indexada desde 1
    caret_line = " " * (col - 1) + "^"
    
    # Retornar el mensaje formateado con tres líneas:
    # 1. Posición del error
    # 2. Línea de código original
    # 3. Indicador visual
    return f"Line {line}, Col {column}:\n{text}\n{caret_line}"
