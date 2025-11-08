from typing import List, Optional
from .tokens import Token, TokenType
from .ast_nodes import *
from .errors import format_error


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token], source: Optional[str] = None):
        self.tokens = tokens
        self.pos = 0
        self.source = source

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        tok = self._peek()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def _match(self, *types: TokenType) -> bool:
        if self._peek().type in types:
            self._advance()
            return True
        return False

    def _consume(self, t: TokenType, message: str) -> Token:
        if self._peek().type == t:
            return self._advance()
        tok = self._peek()
        # Muestra el error con contexto del código
        snippet = format_error(self.source, tok.line, tok.column)
        raise ParseError(f"{message} at {tok.line}:{tok.column}, found {tok.type.name} '{tok.lexeme}'\n{snippet}")

    def parse(self) -> Program:
        body: List[Stmt] = []
        while self._peek().type != TokenType.END:
            if self._peek().type == TokenType.EOF:
                tok = self._peek()
                raise ParseError(f"Expected 'end' before EOF at {tok.line}:{tok.column}")
            body.append(self._statement())
        self._consume(TokenType.END, "Expected 'end' to terminate program")
        self._consume(TokenType.EOF, "Expected no tokens after 'end'")
        return Program(body)

    # Statements
    def _statement(self) -> Stmt:
        tok = self._peek()
        if tok.type == TokenType.READ:
            self._advance()
            name = self._consume(TokenType.IDENT, "Expected identifier after 'read'").lexeme
            self._consume(TokenType.SEMI, "Expected ';' after read statement")
            return Read(name)
        if tok.type == TokenType.PRINT:
            self._advance()
            expr = self._expression()
            self._consume(TokenType.SEMI, "Expected ';' after print expression")
            return Print(expr)
        if tok.type == TokenType.IF:
            self._advance()
            cond = self._expression()
            self._consume(TokenType.LBRACE, "Expected '{' to start if-block")
            then_body: List[Stmt] = []
            while self._peek().type != TokenType.RBRACE:
                then_body.append(self._statement())
            self._consume(TokenType.RBRACE, "Expected '}' to end if-block")
            self._consume(TokenType.ELSE, "Expected 'else' after if-block")
            self._consume(TokenType.LBRACE, "Expected '{' to start else-block")
            else_body: List[Stmt] = []
            while self._peek().type != TokenType.RBRACE:
                else_body.append(self._statement())
            self._consume(TokenType.RBRACE, "Expected '}' to end else-block")
            return IfElse(cond, then_body, else_body)
        if tok.type == TokenType.WHILE:
            self._advance()
            cond = self._expression()
            self._consume(TokenType.LBRACE, "Expected '{' to start while-block")
            body: List[Stmt] = []
            while self._peek().type != TokenType.RBRACE:
                body.append(self._statement())
            self._consume(TokenType.RBRACE, "Expected '}' to end while-block")
            return While(cond, body)
        if tok.type == TokenType.IDENT:
            name = self._advance().lexeme
            self._consume(TokenType.ASSIGN, "Expected '=' after identifier in assignment")
            expr = self._expression()
            self._consume(TokenType.SEMI, "Expected ';' after assignment")
            return Assign(name, expr)
        raise ParseError(f"Unexpected token {tok.type.name} '{tok.lexeme}' at {tok.line}:{tok.column}")

    # Expressions with precedence
    def _expression(self) -> Expr:
        return self._equality()

    def _equality(self) -> Expr:
        expr = self._comparison()
        while self._match(TokenType.EQ, TokenType.NEQ):
            op_tok = self.tokens[self.pos - 1]
            right = self._comparison()
            expr = BinaryOp(expr, op_tok.lexeme, right)
        return expr

    def _comparison(self) -> Expr:
        expr = self._term()
        while self._match(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op_tok = self.tokens[self.pos - 1]
            right = self._term()
            expr = BinaryOp(expr, op_tok.lexeme, right)
        return expr

    def _term(self) -> Expr:
        expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op_tok = self.tokens[self.pos - 1]
            right = self._factor()
            expr = BinaryOp(expr, op_tok.lexeme, right)
        return expr

    def _factor(self) -> Expr:
        expr = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH):
            op_tok = self.tokens[self.pos - 1]
            right = self._unary()
            expr = BinaryOp(expr, op_tok.lexeme, right)
        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.MINUS):
            op_tok = self.tokens[self.pos - 1]
            right = self._unary()
            return UnaryOp(op_tok.lexeme, right)
        return self._primary()

    def _primary(self) -> Expr:
        tok = self._peek()
        if self._match(TokenType.NUMBER):
            return Number(int(tok.lexeme))
        if self._match(TokenType.IDENT):
            return Var(tok.lexeme)
        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        raise ParseError(f"Expected expression at {tok.line}:{tok.column}, found {tok.type.name} '{tok.lexeme}'")
