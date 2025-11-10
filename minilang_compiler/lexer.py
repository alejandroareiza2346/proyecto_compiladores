"""
MÓDULO DE ANÁLISIS LÉXICO (LEXER)


PROPÓSITO:
Implementa la primera fase de compilación: el análisis léxico.
Convierte el código fuente (cadena de caracteres) en una secuencia de tokens.

FUNCIONALIDAD PRINCIPAL:
- Reconocimiento de tokens mediante escaneo carácter por carácter
- Manejo de espacios en blanco y saltos de línea
- Soporte para comentarios de línea (//) y bloque (/* */)
- Seguimiento de posición (línea y columna) para mensajes de error
- Detección de errores léxicos (caracteres inválidos, comentarios sin terminar)

ALGORITMO:
Implementa un autómata finito determinista (DFA) que:
1. Lee caracteres secuencialmente
2. Identifica patrones de tokens
3. Genera objetos Token con metadata de posición
4. Maneja casos especiales (palabras clave, operadores de dos caracteres)

EJEMPLO DE USO:
    source = "x = 10; print x;"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    # Resultado: [Token(IDENT,'x'), Token(ASSIGN,'='), Token(NUMBER,'10'), ...]
"""

from typing import List
from .tokens import Token, TokenType, KEYWORDS
from .errors import format_error


class LexError(Exception):
    """Excepción lanzada cuando se detecta un error léxico."""
    pass


class Lexer:
    """
    Analizador léxico para el lenguaje MiniLang.
    
    El lexer mantiene el estado del análisis:
    - Posición actual en el código fuente
    - Número de línea y columna para mensajes de error
    - Buffer de caracteres para construir tokens
    """
    
    def __init__(self, source: str) -> None:
        """
        Inicializa el analizador léxico.
        
        Parámetros:
            source: Código fuente completo como cadena de texto
        
        Estado inicial:
            - pos: 0 (inicio del archivo)
            - line: 1 (primera línea)
            - col: 1 (primera columna)
        """
        self.source = source          # Código fuente completo
        self.length = len(source)     # Longitud total para verificar límites
        self.pos = 0                  # Índice actual en el código
        self.line = 1                 # Línea actual (indexado desde 1)
        self.col = 1                  # Columna actual (indexado desde 1)

    def _peek(self) -> str:
        """
        Observa el carácter actual sin consumirlo.
        
        Retorna:
            Carácter en la posición actual, o '\0' si llegó al final
        
        Nota: '\0' (null character) se usa convencionalmente para indicar EOF
        """
        return self.source[self.pos] if self.pos < self.length else '\0'

    def _advance(self) -> str:
        """
        Consume y retorna el carácter actual, avanzando la posición.
        
        Actualiza automáticamente:
        - pos: incrementa en 1
        - line: incrementa si encuentra '\n'
        - col: reinicia a 1 en nueva línea, o incrementa
        
        Retorna:
            Carácter consumido
        """
        ch = self._peek()
        self.pos += 1
        if ch == '\n':
            # Nueva línea: incrementar contador de líneas y reiniciar columna
            self.line += 1
            self.col = 1
        else:
            # Mismo línea: solo incrementar columna
            self.col += 1
        return ch

    def _match(self, expected: str) -> bool:
        """
        Verifica si el siguiente carácter coincide y lo consume si es así.
        
        Útil para tokens de dos caracteres como '==', '<=', '!=', etc.
        
        Parámetros:
            expected: Carácter esperado
        
        Retorna:
            True si coincide (y consume), False en caso contrario
        
        Ejemplo:
            # Si el siguiente carácter es '='
            if self._match('='):  # Consume el '=' y retorna True
                # Procesar operador de dos caracteres
        """
        if self._peek() == expected:
            self._advance()
            return True
        return False

    def _skip_whitespace_and_comments(self) -> None:
        """
        Salta espacios en blanco y comentarios.
        
        Maneja tres tipos de elementos ignorables:
        1. Espacios en blanco: ' ', '\r', '\t', '\n'
        2. Comentarios de línea: // hasta fin de línea
        3. Comentarios de bloque: /* hasta */
        
        Algoritmo:
        - Bucle continuo que verifica cada tipo
        - Solo termina cuando encuentra un carácter significativo
        - Lanza LexError si encuentra comentario de bloque sin terminar
        
        Ejemplos de comentarios:
            // Esto es un comentario de línea
            /* Esto es un
               comentario de
               múltiples líneas */
        """
        while True:
            ch = self._peek()
            
            # Caso 1: Espacios en blanco estándar
            if ch in {' ', '\r', '\t', '\n'}:
                self._advance()
                continue
            
            # Caso 2: Comentario de línea // ...
            # Verifica dos caracteres: actual y siguiente
            if ch == '/' and self.pos + 1 < self.length and self.source[self.pos + 1] == '/':
                # Consumir hasta fin de línea o EOF
                while self._peek() not in {'\n', '\0'}:
                    self._advance()
                continue
            
            # Caso 3: Comentario de bloque /* ... */
            if ch == '/' and self.pos + 1 < self.length and self.source[self.pos + 1] == '*':
                # Consumir el /* inicial
                self._advance()
                self._advance()
                
                # Buscar el */ de cierre
                while True:
                    if self._peek() == '\0':
                        # EOF sin cerrar comentario: error léxico
                        msg = format_error(self.source, self.line, self.col)
                        raise LexError(f"Unterminated block comment\n{msg}")
                    
                    # Verificar si encontramos */
                    if self._peek() == '*' and (self.pos + 1 < self.length and self.source[self.pos + 1] == '/'):
                        # Consumir el */ de cierre
                        self._advance()
                        self._advance()
                        break
                    
                    # Avanzar dentro del comentario
                    self._advance()
                continue
            
            # No es espacio ni comentario: terminar el bucle
            break

    def _identifier(self, start_line: int, start_col: int) -> Token:
        """
        Procesa un identificador o palabra clave.
        
        Gramática:
            identifier = letter (letter | digit | '_')*
            letter = 'a'..'z' | 'A'..'Z' | '_'
            digit = '0'..'9'
        
        Parámetros:
            start_line: Línea donde comienza el identificador
            start_col: Columna donde comienza el identificador
        
        Retorna:
            Token con tipo IDENT o palabra clave (READ, PRINT, IF, etc.)
        
        Algoritmo:
            1. Guardar posición inicial
            2. Consumir todos los caracteres alfanuméricos y guiones bajos
            3. Extraer el texto completo
            4. Consultar diccionario KEYWORDS para distinguir palabra clave de identificador
        
        Ejemplos:
            "contador" -> Token(IDENT, "contador")
            "read"     -> Token(READ, "read")
            "x123"     -> Token(IDENT, "x123")
        """
        start = self.pos - 1  # Ya consumimos el primer carácter
        
        # Consumir caracteres alphanumericos y guiones bajos
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()
        
        # Extraer el texto del identificador
        text = self.source[start:self.pos]
        
        # Determinar si es palabra clave o identificador
        # KEYWORDS.get(text, default) retorna el tipo de keyword si existe,
        # o TokenType.IDENT si no es palabra reservada
        tok_type = KEYWORDS.get(text, TokenType.IDENT)
        
        return Token(tok_type, text, start_line, start_col)

    def _number(self, start_line: int, start_col: int) -> Token:
        """
        Procesa un literal numérico entero.
        
        Gramática:
            number = digit+
            digit = '0'..'9'
        
        Parámetros:
            start_line: Línea donde comienza el número
            start_col: Columna donde comienza el número
        
        Retorna:
            Token de tipo NUMBER con el texto del número
        
        Nota: La conversión a int se hace más tarde en el parser
        
        Ejemplos:
            "123"  -> Token(NUMBER, "123")
            "0"    -> Token(NUMBER, "0")
            "9999" -> Token(NUMBER, "9999")
        """
        start = self.pos - 1  # Ya consumimos el primer dígito
        
        # Consumir todos los dígitos consecutivos
        while self._peek().isdigit():
            self._advance()
        
        # Extraer el texto del número
        text = self.source[start:self.pos]
        
        return Token(TokenType.NUMBER, text, start_line, start_col)

    def tokenize(self) -> List[Token]:
        """
        Método principal: convierte código fuente en lista de tokens.
        
        Retorna:
            Lista de objetos Token, terminada con Token(EOF)
        
        Algoritmo:
            1. Saltar espacios y comentarios
            2. Verificar fin de archivo -> generar EOF y terminar
            3. Guardar posición actual para el token
            4. Consumir próximo carácter
            5. Clasificar el carácter:
               - Letra o _: identificador o palabra clave
               - Dígito: número
               - Operador: crear token correspondiente
               - Desconocido: lanzar LexError
            6. Repetir hasta EOF
        
        Manejo especial de operadores de dos caracteres:
            - '==' (igualdad) vs '=' (asignación)
            - '!=' (desigualdad) vs '!' (inválido)
            - '<=' (menor o igual) vs '<' (menor)
            - '>=' (mayor o igual) vs '>' (mayor)
        
        Lanza:
            LexError si encuentra:
            - Carácter no reconocido
            - '!' sin '=' siguiente
            - Comentario de bloque sin cerrar
        """
        tokens: List[Token] = []
        
        while True:
            # Paso 1: Ignorar espacios y comentarios
            self._skip_whitespace_and_comments()
            
            # Paso 2: Verificar fin de archivo
            ch = self._peek()
            if ch == '\0':
                # Agregar token EOF y terminar
                tokens.append(Token(TokenType.EOF, '', self.line, self.col))
                break
            
            # Paso 3: Guardar posición del inicio del token
            start_line, start_col = self.line, self.col
            
            # Paso 4: Consumir el carácter
            c = self._advance()

            # Paso 5: Clasificar y procesar según tipo de carácter
            
            # Caso A: Identificador o palabra clave (letra o _)
            if c.isalpha() or c == '_':
                tokens.append(self._identifier(start_line, start_col))
                continue
            
            # Caso B: Número (dígito)
            if c.isdigit():
                tokens.append(self._number(start_line, start_col))
                continue

            # Caso C: Operadores y delimitadores de un solo carácter
            if c == '+':
                tokens.append(Token(TokenType.PLUS, c, start_line, start_col))
            elif c == '-':
                tokens.append(Token(TokenType.MINUS, c, start_line, start_col))
            elif c == '*':
                tokens.append(Token(TokenType.STAR, c, start_line, start_col))
            elif c == '/':
                tokens.append(Token(TokenType.SLASH, c, start_line, start_col))
            elif c == '(':
                tokens.append(Token(TokenType.LPAREN, c, start_line, start_col))
            elif c == ')':
                tokens.append(Token(TokenType.RPAREN, c, start_line, start_col))
            elif c == '{':
                tokens.append(Token(TokenType.LBRACE, c, start_line, start_col))
            elif c == '}':
                tokens.append(Token(TokenType.RBRACE, c, start_line, start_col))
            elif c == ';':
                tokens.append(Token(TokenType.SEMI, c, start_line, start_col))
            
            # Caso D: Operadores de uno o dos caracteres
            
            elif c == '!':
                # '!' solo es válido seguido de '=' para formar '!='
                if self._match('='):
                    tokens.append(Token(TokenType.NEQ, '!=', start_line, start_col))
                else:
                    # '!' solo no es válido en MiniLang
                    msg = format_error(self.source, start_line, start_col)
                    raise LexError(f"Unexpected '!' (expected '!=')\n{msg}")
            
            elif c == '=':
                # Puede ser '==' (igualdad) o '=' (asignación)
                if self._match('='):
                    tokens.append(Token(TokenType.EQ, '==', start_line, start_col))
                else:
                    tokens.append(Token(TokenType.ASSIGN, '=', start_line, start_col))
            
            elif c == '<':
                # Puede ser '<=' (menor o igual) o '<' (menor)
                if self._match('='):
                    tokens.append(Token(TokenType.LE, '<=', start_line, start_col))
                else:
                    tokens.append(Token(TokenType.LT, '<', start_line, start_col))
            
            elif c == '>':
                # Puede ser '>=' (mayor o igual) o '>' (mayor)
                if self._match('='):
                    tokens.append(Token(TokenType.GE, '>=', start_line, start_col))
                else:
                    tokens.append(Token(TokenType.GT, '>', start_line, start_col))
            
            # Caso E: Carácter no reconocido
            else:
                msg = format_error(self.source, start_line, start_col)
                raise LexError(f"Unexpected character '{c}'\n{msg}")
        
        return tokens
