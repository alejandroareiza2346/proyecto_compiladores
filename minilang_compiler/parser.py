"""
MÓDULO DE ANÁLISIS SINTÁCTICO (PARSER)
Proyecto: Compilador MiniLang
Universidad: [Nombre de la Universidad]
Curso: Compiladores

PROPÓSITO:
Implementa la segunda fase de compilación: el análisis sintáctico.
Convierte la secuencia de tokens en un Árbol de Sintaxis Abstracta (AST).

TÉCNICA:
Parser de Descenso Recursivo (Recursive Descent Parser)
- Cada regla de la gramática se traduce en un método
- Análisis predictivo LL(1) sin retroceso
- Manejo de precedencia de operadores mediante jerarquía de métodos

GRAMÁTICA DE MINILANG:
    program    := stmt* 'end' EOF
    stmt       := read_stmt | print_stmt | assign_stmt | if_stmt | while_stmt
    read_stmt  := 'read' IDENT ';'
    print_stmt := 'print' expr ';'
    assign_stmt:= IDENT '=' expr ';'
    if_stmt    := 'if' expr '{' stmt* '}' 'else' '{' stmt* '}'
    while_stmt := 'while' expr '{' stmt* '}'
    
    expr       := equality
    equality   := comparison (('==' | '!=') comparison)*
    comparison := term (('<' | '>' | '<=' | '>=') term)*
    term       := factor (('+' | '-') factor)*
    factor     := unary (('*' | '/') unary)*
    unary      := '-' unary | primary
    primary    := NUMBER | IDENT | '(' expr ')'

PRECEDENCIA DE OPERADORES (menor a mayor):
    1. Igualdad: ==, !=
    2. Comparación: <, >, <=, >=
    3. Aditivos: +, -
    4. Multiplicativos: *, /
    5. Unario: -
    6. Primario: literales, variables, paréntesis

EJEMPLO DE USO:
    tokens = [Token(READ), Token(IDENT,'x'), Token(SEMI), Token(END), Token(EOF)]
    parser = Parser(tokens, source_code)
    ast = parser.parse()
    # Resultado: Program([Read('x')])
"""

from typing import List, Optional
from .tokens import Token, TokenType
from .ast_nodes import *
from .errors import format_error


class ParseError(Exception):
    """Excepción lanzada cuando se detecta un error sintáctico."""
    pass


class Parser:
    """
    Analizador sintáctico para el lenguaje MiniLang.
    
    Mantiene el estado del análisis:
    - Lista de tokens del lexer
    - Posición actual en la lista
    - Referencia al código fuente (para mensajes de error)
    """
    
    def __init__(self, tokens: List[Token], source: Optional[str] = None):
        """
        Inicializa el parser.
        
        Parámetros:
            tokens: Lista de tokens producida por el lexer
            source: Código fuente original (opcional, para mensajes de error)
        """
        self.tokens = tokens    # Secuencia completa de tokens
        self.pos = 0           # Índice del token actual
        self.source = source   # Código fuente para contexto de errores

    def _peek(self) -> Token:
        """
        Observa el token actual sin consumirlo.
        
        Retorna:
            Token en la posición actual
        """
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        """
        Consume y retorna el token actual, avanzando la posición.
        
        Retorna:
            Token consumido
        
        Nota: No avanza más allá del último token (EOF)
        """
        tok = self._peek()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def _match(self, *types: TokenType) -> bool:
        """
        Verifica si el token actual coincide con alguno de los tipos dados.
        Si coincide, lo consume.
        
        Parámetros:
            *types: Tipos de token a verificar
        
        Retorna:
            True si coincide (y consume), False en caso contrario
        
        Ejemplo:
            if self._match(TokenType.PLUS, TokenType.MINUS):
                # El token actual era + o -, ya fue consumido
        """
        if self._peek().type in types:
            self._advance()
            return True
        return False

    def _consume(self, t: TokenType, message: str) -> Token:
        """
        Consume un token del tipo esperado, o lanza error si no coincide.
        
        Parámetros:
            t: Tipo de token esperado
            message: Mensaje de error si no coincide
        
        Retorna:
            Token consumido
        
        Lanza:
            ParseError si el token actual no es del tipo esperado
        
        Ejemplo:
            self._consume(TokenType.SEMI, "Expected ';' after statement")
        """
        if self._peek().type == t:
            return self._advance()
        
        # Error: token no coincide con el esperado
        tok = self._peek()
        snippet = format_error(self.source, tok.line, tok.column)
        raise ParseError(f"{message} at {tok.line}:{tok.column}, found {tok.type.name} '{tok.lexeme}'\n{snippet}")

    def parse(self) -> Program:
        """
        Punto de entrada principal del parser.
        Analiza un programa completo y construye el AST.
        
        Gramática:
            program := stmt* 'end' EOF
        
        Retorna:
            Nodo Program conteniendo todas las declaraciones
        
        Lanza:
            ParseError si:
            - Encuentra EOF antes de 'end'
            - Hay tokens después de 'end'
            - Cualquier declaración es sintácticamente incorrecta
        
        Ejemplo:
            Código: "read x; print x; end"
            Resultado: Program([Read('x'), Print(Var('x'))])
        """
        body: List[Stmt] = []
        
        # Procesar todas las declaraciones hasta encontrar 'end'
        while self._peek().type != TokenType.END:
            if self._peek().type == TokenType.EOF:
                # Error: llegó al final sin encontrar 'end'
                tok = self._peek()
                raise ParseError(f"Expected 'end' before EOF at {tok.line}:{tok.column}")
            body.append(self._statement())
        
        # Consumir 'end' y verificar que no haya nada después
        self._consume(TokenType.END, "Expected 'end' to terminate program")
        self._consume(TokenType.EOF, "Expected no tokens after 'end'")
        
        return Program(body)

    # Métodos para analizar declaraciones (statements)
    def _statement(self) -> Stmt:
        """
        Analiza una declaración individual.
        
        Gramática:
            stmt := read_stmt | print_stmt | assign_stmt | if_stmt | while_stmt
        
        Estrategia: Analizar el primer token para determinar el tipo de declaración
        
        Retorna:
            Nodo Stmt correspondiente al tipo de declaración
        
        Lanza:
            ParseError si encuentra un token inesperado
        """
        tok = self._peek()
        
        # Declaración READ: read IDENT ;
        if tok.type == TokenType.READ:
            self._advance()  # Consumir 'read'
            name = self._consume(TokenType.IDENT, "Expected identifier after 'read'").lexeme
            self._consume(TokenType.SEMI, "Expected ';' after read statement")
            return Read(name)
        
        # Declaración PRINT: print expr ;
        if tok.type == TokenType.PRINT:
            self._advance()  # Consumir 'print'
            expr = self._expression()
            self._consume(TokenType.SEMI, "Expected ';' after print expression")
            return Print(expr)
        
        # Declaración IF-ELSE: if expr { stmt* } else { stmt* }
        if tok.type == TokenType.IF:
            self._advance()  # Consumir 'if'
            cond = self._expression()
            
            # Bloque THEN
            self._consume(TokenType.LBRACE, "Expected '{' to start if-block")
            then_body: List[Stmt] = []
            while self._peek().type != TokenType.RBRACE:
                then_body.append(self._statement())
            self._consume(TokenType.RBRACE, "Expected '}' to end if-block")
            
            # Bloque ELSE (obligatorio en MiniLang)
            self._consume(TokenType.ELSE, "Expected 'else' after if-block")
            self._consume(TokenType.LBRACE, "Expected '{' to start else-block")
            else_body: List[Stmt] = []
            while self._peek().type != TokenType.RBRACE:
                else_body.append(self._statement())
            self._consume(TokenType.RBRACE, "Expected '}' to end else-block")
            
            return IfElse(cond, then_body, else_body)
        
        # Declaración WHILE: while expr { stmt* }
        if tok.type == TokenType.WHILE:
            self._advance()  # Consumir 'while'
            cond = self._expression()
            
            # Cuerpo del bucle
            self._consume(TokenType.LBRACE, "Expected '{' to start while-block")
            body: List[Stmt] = []
            while self._peek().type != TokenType.RBRACE:
                body.append(self._statement())
            self._consume(TokenType.RBRACE, "Expected '}' to end while-block")
            
            return While(cond, body)
        
        # Declaración de ASIGNACIÓN: IDENT = expr ;
        if tok.type == TokenType.IDENT:
            name = self._advance().lexeme
            self._consume(TokenType.ASSIGN, "Expected '=' after identifier in assignment")
            expr = self._expression()
            self._consume(TokenType.SEMI, "Expected ';' after assignment")
            return Assign(name, expr)
        
        # Token inesperado: no es ninguna declaración válida
        raise ParseError(f"Unexpected token {tok.type.name} '{tok.lexeme}' at {tok.line}:{tok.column}")

    # Métodos para analizar expresiones con precedencia de operadores
    
    def _expression(self) -> Expr:
        """
        Punto de entrada para el análisis de expresiones.
        Comienza con el nivel de precedencia más bajo.
        
        Retorna:
            Nodo Expr representando la expresión
        """
        return self._equality()

    def _equality(self) -> Expr:
        """
        Analiza operadores de igualdad: == !=
        Precedencia más baja.
        
        Gramática:
            equality := comparison (('==' | '!=') comparison)*
        
        Ejemplo:
            a < b == c > d
            # Se agrupa como: (a < b) == (c > d)
        """
        expr = self._comparison()
        while self._match(TokenType.EQ, TokenType.NEQ):
            op_tok = self.tokens[self.pos - 1]  # Token del operador recién consumido
            right = self._comparison()
            expr = BinaryOp(expr, op_tok.lexeme, right)
        return expr

    def _comparison(self) -> Expr:
        """
        Analiza operadores de comparación: < > <= >=
        
        Gramática:
            comparison := term (('<' | '>' | '<=' | '>=') term)*
        
        Ejemplo:
            a + b < c - d
            # Se agrupa como: (a + b) < (c - d)
        """
        expr = self._term()
        while self._match(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op_tok = self.tokens[self.pos - 1]
            right = self._term()
            expr = BinaryOp(expr, op_tok.lexeme, right)
        return expr

    def _term(self) -> Expr:
        """
        Analiza operadores aditivos: + -
        
        Gramática:
            term := factor (('+' | '-') factor)*
        
        Ejemplo:
            a * b + c / d
            # Se agrupa como: (a * b) + (c / d)
        """
        expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op_tok = self.tokens[self.pos - 1]
            right = self._factor()
            expr = BinaryOp(expr, op_tok.lexeme, right)
        return expr

    def _factor(self) -> Expr:
        """
        Analiza operadores multiplicativos: * /
        
        Gramática:
            factor := unary (('*' | '/') unary)*
        
        Ejemplo:
            -a * b
            # Se agrupa como: (-a) * b
        """
        expr = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH):
            op_tok = self.tokens[self.pos - 1]
            right = self._unary()
            expr = BinaryOp(expr, op_tok.lexeme, right)
        return expr

    def _unary(self) -> Expr:
        """
        Analiza operadores unarios: -
        Precedencia más alta (excepto paréntesis).
        
        Gramática:
            unary := '-' unary | primary
        
        Recursivo para permitir múltiples negaciones: --x
        
        Ejemplo:
            -5    -> UnaryOp('-', Number(5))
            --x   -> UnaryOp('-', UnaryOp('-', Var('x')))
        """
        if self._match(TokenType.MINUS):
            op_tok = self.tokens[self.pos - 1]
            right = self._unary()  # Recursión para permitir múltiples unarios
            return UnaryOp(op_tok.lexeme, right)
        return self._primary()

    def _primary(self) -> Expr:
        """
        Analiza expresiones primarias (átomos).
        Precedencia máxima.
        
        Gramática:
            primary := NUMBER | IDENT | '(' expr ')'
        
        Tipos de expresiones primarias:
        - Literales numéricos: 42, 0, 999
        - Variables: x, contador, resultado
        - Expresiones entre paréntesis: (a + b)
        
        Los paréntesis permiten alterar la precedencia natural.
        
        Ejemplo:
            2 * (3 + 4)
            # Los paréntesis fuerzan que la suma se evalúe primero
        """
        tok = self._peek()
        
        # Caso 1: Literal numérico
        if self._match(TokenType.NUMBER):
            return Number(int(tok.lexeme))
        
        # Caso 2: Variable
        if self._match(TokenType.IDENT):
            return Var(tok.lexeme)
        
        # Caso 3: Expresión entre paréntesis
        if self._match(TokenType.LPAREN):
            expr = self._expression()  # Recursión para analizar la expresión interna
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        # Error: no es una expresión primaria válida
        raise ParseError(f"Expected expression at {tok.line}:{tok.column}, found {tok.type.name} '{tok.lexeme}'")
