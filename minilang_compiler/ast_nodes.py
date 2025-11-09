"""
MÓDULO DE NODOS DEL ÁRBOL DE SINTAXIS ABSTRACTA (AST)
Proyecto: Compilador MiniLang
Universidad: [Nombre de la Universidad]
Curso: Compiladores

PROPÓSITO:
Define las estructuras de datos que representan el Árbol de Sintaxis Abstracta (AST).
El AST es una representación en árbol de la estructura sintáctica del programa fuente,
donde cada nodo representa una construcción del lenguaje.

JERARQUÍA:
1. Expresiones (Expr): Construcciones que evalúan a un valor
   - Number: Literales numéricos
   - Var: Referencias a variables
   - UnaryOp: Operaciones unarias (negación)
   - BinaryOp: Operaciones binarias (aritméticas y relacionales)

2. Declaraciones (Stmt): Construcciones que ejecutan acciones
   - Read: Entrada de datos
   - Print: Salida de datos
   - Assign: Asignación de variables
   - IfElse: Estructura condicional
   - While: Estructura iterativa

3. Programa (Program): Nodo raíz que contiene todas las declaraciones

EJEMPLO DE USO:
    # Representa: x = 5 + 3
    assign = Assign(
        name='x',
        expr=BinaryOp(
            left=Number(5),
            op='+',
            right=Number(3)
        )
    )
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union


# Clase base para todas las expresiones
@dataclass
class Expr:
    """
    Clase base abstracta para todas las expresiones.
    
    Una expresión es cualquier construcción del lenguaje que evalúa a un valor.
    Todas las expresiones concretas heredan de esta clase.
    """
    pass

@dataclass
class Number(Expr):
    """
    Nodo que representa un literal numérico entero.
    
    Atributos:
        value: Valor entero del literal
    
    Ejemplo:
        Number(42)  representa el literal 42
        Number(-5)  representa el literal -5
    """
    value: int

@dataclass
class Var(Expr):
    """
    Nodo que representa una referencia a una variable.
    
    Atributos:
        name: Nombre del identificador de la variable
    
    Ejemplo:
        Var('x')        representa el uso de la variable x
        Var('contador') representa el uso de la variable contador
    """
    name: str

@dataclass
class UnaryOp(Expr):
    """
    Nodo que representa una operación unaria.
    
    Atributos:
        op: Operador unario (actualmente solo '-' para negación)
        expr: Expresión a la que se aplica el operador
    
    Ejemplo:
        UnaryOp('-', Number(5))
        # Representa: -5
        
        UnaryOp('-', Var('x'))
        # Representa: -x
    """
    op: str       # Operador: '-' (negación aritmética)
    expr: Expr    # Operando de la operación

@dataclass
class BinaryOp(Expr):
    """
    Nodo que representa una operación binaria.
    
    Atributos:
        left: Expresión del operando izquierdo
        op: Operador binario
        right: Expresión del operando derecho
    
    Operadores soportados:
        Aritméticos: '+', '-', '*', '/'
        Relacionales: '<', '>', '<=', '>='
        Igualdad: '==', '!='
    
    Ejemplo:
        BinaryOp(Number(3), '+', Number(5))
        # Representa: 3 + 5
        
        BinaryOp(Var('x'), '<', Number(10))
        # Representa: x < 10
        
        BinaryOp(
            left=BinaryOp(Number(2), '*', Number(3)),
            op='+',
            right=Number(1)
        )
        # Representa: (2 * 3) + 1
    """
    left: Expr    # Operando izquierdo
    op: str       # Operador binario
    right: Expr   # Operando derecho


# Clase base para todas las declaraciones
@dataclass
class Stmt:
    """
    Clase base abstracta para todas las declaraciones.
    
    Una declaración es una construcción del lenguaje que ejecuta una acción
    pero no retorna un valor. Todas las declaraciones concretas heredan de esta clase.
    """
    pass

@dataclass
class Read(Stmt):
    """
    Nodo que representa una instrucción de entrada.
    
    Atributos:
        name: Nombre de la variable que recibirá el valor leído
    
    Ejemplo:
        Read('x')
        # Representa: read x;
        # Lee un valor entero y lo almacena en la variable x
    """
    name: str

@dataclass
class Print(Stmt):
    """
    Nodo que representa una instrucción de salida.
    
    Atributos:
        expr: Expresión cuyo valor será impreso
    
    Ejemplo:
        Print(Number(42))
        # Representa: print 42;
        
        Print(Var('resultado'))
        # Representa: print resultado;
        
        Print(BinaryOp(Var('x'), '+', Number(1)))
        # Representa: print x + 1;
    """
    expr: Expr

@dataclass
class Assign(Stmt):
    """
    Nodo que representa una instrucción de asignación.
    
    Atributos:
        name: Nombre de la variable destino
        expr: Expresión cuyo valor será asignado a la variable
    
    Ejemplo:
        Assign('x', Number(10))
        # Representa: x = 10;
        
        Assign('suma', BinaryOp(Var('a'), '+', Var('b')))
        # Representa: suma = a + b;
    """
    name: str   # Variable destino
    expr: Expr  # Valor a asignar

@dataclass
class IfElse(Stmt):
    """
    Nodo que representa una estructura condicional if-else.
    
    Atributos:
        cond: Expresión booleana de la condición
        then_body: Lista de declaraciones a ejecutar si la condición es verdadera
        else_body: Lista de declaraciones a ejecutar si la condición es falsa
    
    Nota: En MiniLang, toda estructura if debe tener su correspondiente else.
    
    Ejemplo:
        IfElse(
            cond=BinaryOp(Var('x'), '>', Number(0)),
            then_body=[Print(Number(1))],
            else_body=[Print(Number(0))]
        )
        # Representa:
        # if x > 0 {
        #     print 1;
        # } else {
        #     print 0;
        # }
    """
    cond: Expr          # Condición a evaluar
    then_body: List[Stmt]  # Bloque verdadero
    else_body: List[Stmt]  # Bloque falso

@dataclass
class While(Stmt):
    """
    Nodo que representa una estructura iterativa while.
    
    Atributos:
        cond: Expresión booleana de la condición de continuación
        body: Lista de declaraciones a ejecutar mientras la condición sea verdadera
    
    Ejemplo:
        While(
            cond=BinaryOp(Var('i'), '<', Number(10)),
            body=[
                Print(Var('i')),
                Assign('i', BinaryOp(Var('i'), '+', Number(1)))
            ]
        )
        # Representa:
        # while i < 10 {
        #     print i;
        #     i = i + 1;
        # }
    """
    cond: Expr       # Condición del bucle
    body: List[Stmt]  # Cuerpo del bucle


# Nodo raíz del programa
@dataclass
class Program:
    """
    Nodo raíz del Árbol de Sintaxis Abstracta.
    
    Atributos:
        body: Lista de todas las declaraciones del programa
    
    Este nodo representa el programa completo. En MiniLang, un programa
    es simplemente una secuencia de declaraciones seguida de la palabra 'end'.
    
    Ejemplo:
        Program([
            Read('x'),
            Assign('y', BinaryOp(Var('x'), '*', Number(2))),
            Print(Var('y'))
        ])
        # Representa:
        # read x;
        # y = x * 2;
        # print y;
        # end
    """
    body: List[Stmt]  # Secuencia de declaraciones del programa
