"""
MÓDULO DE DEFINICIÓN DE TOKENS


PROPÓSITO:
Este módulo define los tipos de tokens (lexemas) reconocidos por el analizador léxico.
Un token es la unidad mínima con significado en el lenguaje de programación.

CONTENIDO:
1. TokenType: Enumeración de todos los tipos de tokens válidos
2. KEYWORDS: Mapeo de palabras clave del lenguaje
3. Token: Clase de datos que representa un token individual con su metadata

EJEMPLO DE USO:
    token = Token(TokenType.NUMBER, "42", line=1, column=5)
    # Representa el número 42 encontrado en la línea 1, columna 5
"""

from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    """
    Enumeración de tipos de tokens del lenguaje MiniLang.
    
    Los tokens se clasifican en cuatro categorías:
    1. Operadores de un solo carácter
    2. Operadores de uno o dos caracteres
    3. Literales (identificadores y números)
    4. Palabras clave (reservadas del lenguaje)
    """
    
    # Tokens de un solo carácter
    # Estos representan operadores y delimitadores básicos
    PLUS = auto()        # Operador suma: +
    MINUS = auto()       # Operador resta: -
    STAR = auto()        # Operador multiplicación: *
    SLASH = auto()       # Operador división: /
    LPAREN = auto()      # Paréntesis izquierdo: (
    RPAREN = auto()      # Paréntesis derecho: )
    LBRACE = auto()      # Llave izquierda: {
    RBRACE = auto()      # Llave derecha: }
    SEMI = auto()        # Punto y coma: ;
    ASSIGN = auto()      # Operador asignación: =

    # Tokens de uno o dos caracteres
    # Estos operadores relacionales pueden tener versiones compuestas
    LT = auto()          # Menor que: <
    GT = auto()          # Mayor que: >
    LE = auto()          # Menor o igual: <=
    GE = auto()          # Mayor o igual: >=
    EQ = auto()          # Igualdad: ==
    NEQ = auto()         # Desigualdad: !=

    # Literales
    # Representan valores e identificadores definidos por el usuario
    IDENT = auto()       # Identificador de variable (ej: x, contador, suma)
    NUMBER = auto()      # Literal numérico entero (ej: 42, 0, 123)

    # Palabras clave
    # Palabras reservadas del lenguaje con significado especial
    READ = auto()        # Instrucción de entrada: read
    PRINT = auto()       # Instrucción de salida: print
    IF = auto()          # Inicio de condicional: if
    ELSE = auto()        # Alternativa de condicional: else
    WHILE = auto()       # Inicio de bucle: while
    END = auto()         # Fin de programa: end

    # Token especial
    EOF = auto()         # End Of File: marca el final del archivo fuente


"""
Diccionario de palabras clave del lenguaje.

Este mapeo permite al analizador léxico distinguir rápidamente entre
identificadores definidos por el usuario y palabras reservadas del lenguaje.

Ejemplo:
    Si el lexer encuentra "read", consulta este diccionario y obtiene TokenType.READ.
    Si encuentra "variable", no está en el diccionario, por lo que es TokenType.IDENT.
"""
KEYWORDS = {
    'read': TokenType.READ,      # Entrada de datos
    'print': TokenType.PRINT,    # Salida de datos
    'if': TokenType.IF,          # Inicio de estructura condicional
    'else': TokenType.ELSE,      # Cláusula alternativa
    'while': TokenType.WHILE,    # Inicio de estructura iterativa
    'end': TokenType.END,        # Terminador de programa
}


@dataclass(frozen=True)
class Token:
    """
    Clase inmutable que representa un token individual.
    
    Atributos:
        type: Tipo de token (de la enumeración TokenType)
        lexeme: Texto literal tal como aparece en el código fuente
        line: Número de línea donde se encontró (indexado desde 1)
        column: Número de columna donde comienza (indexado desde 1)
    
    La inmutabilidad (frozen=True) garantiza que los tokens no puedan
    ser modificados después de su creación, lo cual es fundamental para
    mantener la integridad del análisis léxico.
    
    Ejemplo:
        Token(TokenType.NUMBER, "123", 5, 10)
        # Representa el número 123 en la línea 5, columna 10
        
        Token(TokenType.PLUS, "+", 7, 15)
        # Representa el operador + en la línea 7, columna 15
    """
    type: TokenType      # Clasificación del token
    lexeme: str          # Texto original del código fuente
    line: int            # Posición vertical en el archivo
    column: int          # Posición horizontal en la línea

    def __repr__(self) -> str:
        """
        Representación legible del token para depuración.
        
        Formato: Token(TIPO, 'lexema', línea:columna)
        """
        return f"Token({self.type.name}, '{self.lexeme}', {self.line}:{self.column})"
