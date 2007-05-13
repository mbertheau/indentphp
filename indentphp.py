#!/usr/bin/env python

# indentphp (c) 2007 by Markus Bertheau

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# configuration

class Config:
    def __init__(self):
        self.strIndent = '    '
        self.indentlevel = 0

    def indent(self):
        return self.strIndent * self.indentlevel

    def incIndent(self):
        self.indentlevel += 1

    def decIndent(self):
        self.indentlevel -= 1

# tokenizer

from ply import lex, yacc
from ply.lex import TOKEN
import re

states = (
    ('php','exclusive'),
)

tokens = (
    'SCRIPTSTART',
    'SCRIPTSHORTSTART',
    'SCRIPTEND',
    'NEWLINE',
    'SPACE',
    'TAB',
    'HTMLCHAR',
    'FUNCTION',
    'IDENTIFIER',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'AMPERSAND',
    'SEMICOLON',
    'COMMA',
    'ASSIGN',
    'ARRAY',
    'VARIABLE',
    'NUMBER',
    'CONSTANT_DQ_STRING',
    'CONSTANT_SQ_STRING',
    'CURRENT_LINE',
    'CURRENT_FILE',
    'CURRENT_CLASS',
    'CURRENT_METHOD',
    'CURRENT_FUNCTION',
    'PLUS',
    'MINUS',
    'COLON',
    'DOUBLE_ARROW',
    'CLASS',
    'ABSTRACT',
    'FINAL',
    'EXTENDS',
    'IMPLEMENTS',
    'VAR',
    'PUBLIC',
    'PRIVATE',
    'PROTECTED',
    'STATIC',
    'CONST',
    'INTERFACE',
    'IF',
    'EMPTY',
    'RETURN',
    'ELSE',
    'ISSET',
    'QUESTION',
    'LSQBRACKET',
    'RSQBRACKET',
    'DOUBLECOLON'
)

@TOKEN(r'<\?php')
def t_SCRIPTSTART(t):
    t.lexer.begin('php')
    return t

@TOKEN(r'<\?')
def t_SCRIPTSHORTSTART(t):
    t.lexer.begin('php')
    return t

@TOKEN(r'\?>')
def t_php_SCRIPTEND(t):
    t.lexer.begin('INITIAL')
    return t

@TOKEN(r'((0x[0-9a-fA-F]+)|((([0-9]*\.[0-9]+)|([0-9]+\.[0-9]*)|([0-9]+))([eE][-+]?[0-9]+)?))')
def t_php_NUMBER(t):
    return t

reserved = {
    'function'      : 'FUNCTION',
    'array'         : 'ARRAY',
    '__LINE__'      : 'CURRENT_LINE',
    '__FILE__'      : 'CURRENT_FILE',
    '__CLASS__'     : 'CURRENT_CLASS',
    '__METHOD__'    : 'CURRENT_METHOD',
    '__FUNCTION__'  : 'CURRENT_FUNCTION',
    'class'         : 'CLASS',
    'abstract'      : 'ABSTRACT',
    'final'         : 'FINAL',
    'extends'       : 'EXTENDS',
    'implements'    : 'IMPLEMENTS',
    'var'           : 'VAR',
    'public'        : 'PUBLIC',
    'private'       : 'PRIVATE',
    'protected'     : 'PROTECTED',
    'static'        : 'STATIC',
    'const'         : 'CONST',
    'interface'     : 'INTERFACE',
    'if'            : 'IF',
    'empty'         : 'EMPTY',
    'return'        : 'RETURN',
    'else'          : 'ELSE',
    'isset'         : 'ISSET'
}

@TOKEN(r'[a-zA-Z_][a-zA-Z_0-9]*')
def t_php_IDENTIFIER(t):
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

@TOKEN(r'(\n|\r|\r\n)')
def t_php_NEWLINE(t):
    t.lexer.lineno += 1
    return t

t_php_RBRACE = r'}'
t_php_LBRACE = r'{'
t_php_LPAREN = r'\('
t_php_RPAREN = r'\)'
t_php_AMPERSAND = r'&'
t_php_SEMICOLON = r';'
t_php_COMMA = r','
t_php_ASSIGN = r'='
t_php_DOUBLE_ARROW = r'=>'
t_php_PLUS = r'\+'
t_php_MINUS = r'-'
t_php_COLON = r':'
t_php_DOUBLECOLON = r'::'
t_php_SPACE = r'\ '
t_php_TAB = r'\t'
t_php_QUESTION = r'\?'
t_php_LSQBRACKET = r'\['
t_php_RSQBRACKET = r'\]'
t_php_VARIABLE = r'\$[a-zA-Z_][a-zA-Z_0-9]*'
t_php_CONSTANT_DQ_STRING = r'"([^$"\\]|(\\.))*"'
t_php_CONSTANT_SQ_STRING = r'\'([^$\'\\]|(\\.))*\''
t_HTMLCHAR = r'.'

def t_error(t):
    print 'lexing error on line %d' % t.lexer.lineno

def t_php_error(t):
    print 'lexing error in php on line %d' % t.lexer.lineno

lexer = lex.lex(debug=0, reflags=re.S)

# parser

import types

start = 'file'

def p_file_1(p):
    """file : start1 scriptwithoutend
    """
    p[0] = File(p[1], p[2])

def p_file_2(p):
    """file : start1
    """
    p[0] = File(p[1])

def p_start1_1(p):
    """start1 : script
    """
    p[0] = [p[1]]

def p_start1_2(p):
    """start1 : html
    """
    p[0] = [HTML(p[1])]

def p_start1_3(p):
    """start1 : start1 script
    """
    p[0] = p[1]
    p[0].append(p[2])

def p_start1_4(p):
    """start1 : start1 html
    """
    p[0] = p[1]
    p[0].append(HTML(p[2]))

def p_scriptwithoutend_1(p):
    """scriptwithoutend : SCRIPTSTART whitespace php
    """
    p[0] = p[3]

def p_scriptwithoutend_2(p):
    """scriptwithoutend : SCRIPTSHORTSTART opt_whitespace php
    """
    p[0] = p[3]

def p_script_1(p):
    """script : SCRIPTSTART whitespace php SCRIPTEND
    """
    p[0] = p[3]

def p_script_2(p):
    """script : SCRIPTSHORTSTART opt_whitespace php SCRIPTEND
    """
    p[0] = p[3]

def p_php(p):
    """php : statement_list
    """
    p[0] = Script(p[1])

def p_statement_list(p):
    """statement_list :   statement_list top_statement
                        |
    """
    if len(p) > 1:
        p[0] = p[1]
        p[0].append(p[2])
    else:
        p[0] = StatementList([])

def p_top_statement(p):
    """top_statement :   statement
                       | function_declaration_statement
                       | class_declaration_statement
    """
    p[0] = p[1]

def p_statement_1(p):
    """statement : LBRACE opt_whitespace statement_list RBRACE opt_whitespace
    """
    p[0] = BlockStatement(p[3])

def p_statement_2(p):
    """statement : IF opt_whitespace LPAREN opt_whitespace expr RPAREN opt_whitespace statement elseif_list else_single
    """
    p[0] = IfStatement(p[5], p[8], p[9], p[10])

#def p_statement_3(p):
#    """statement : IF opt_whitespace LPAREN opt_whitespace expr RPAREN opt_whitespace COLON opt_whitespace statement_list new_elseif_list new_else_single ENDIF opt_whitespace SEMICOLON opt_whitespace
#    """
#    p[0] = IfColonStatement(p[5], p[10], p[11], p[12])
#
#def p_statement_4(p):
#    """statement : WHILE opt_whitespace LPAREN opt_whitespace expr RPAREN opt_whitespace while_statement
#    """
#    p[0] = WhileStatement(p[5], p[8])
#
#def p_statement_5(p):
#    """statement : DO opt_whitespace statement WHILE opt_whitespace LPAREN opt_whitespace expr RPAREN opt_whitespace SEMICOLON opt_whitespace
#    """
#    p[0] = DoStatement(p[3], p[8])
#
#def p_statement_6(p):
#    """statement : FOR opt_whitespace LPAREN opt_whitespace for_expr SEMICOLON opt_whitespace for_expr SEMICOLON opt_whitespace for_expr RPAREN opt_whitespace for_statement
#    """
#    p[0] = ForStatement(p[5], p[8], p[11], p[14])
#
#def p_statement_7(p):
#    """statement : SWITCH opt_whitespace LPAREN opt_whitespace expr RPAREN opt_whitespace switch_case_list
#    """
#    p[0] = SwitchStatement(p[5], p[8])
#
#def p_statement_8(p):
#    """statement : BREAK opt_whitespace SEMICOLON opt_whitespace
#    """
#    p[0] = BreakStatement()
#
#def p_statement_9(p):
#    """statement : BREAK opt_whitespace expr SEMICOLON opt_whitespace
#    """
#    p[0] = BreakStatement(p[3])
#
#def p_statement_10(p):
#    """statement : CONTINUE opt_whitespace SEMICOLON opt_whitespace
#    """
#    p[0] = ContinueStatement()
#
#def p_statement_11(p):
#    """statement : CONTINUE opt_whitespace expr SEMICOLON opt_whitespace
#    """
#    p[0] = ContinueStatement(p[3])
#
def p_statement_12(p):
    """statement : RETURN opt_whitespace SEMICOLON opt_whitespace
    """
    p[0] = ReturnStatement()

#def p_statement_13(p):
#    """statement : RETURN opt_whitespace expr_without_variable SEMICOLON opt_whitespace
#    """
#    p[0] = ReturnStatement(p[3])
#
#def p_statement_14(p):
#    """statement : RETURN opt_whitespace variable SEMICOLON opt_whitespace
#    """
#    p[0] = ReturnStatement(p[3])
#
#def p_statement_15(p):
#    """statement : GLOBAL opt_whitespace global_var_list SEMICOLON opt_whitespace
#    """
#    p[0] = GlobalStatement(p[3])
#
#def p_statement_16(p):
#    """statement : STATIC opt_whitespace static_var_list SEMICOLON opt_whitespace
#    """
#    p[0] = StaticStatement(p[3])
#
#def p_statement_17(p):
#    """statement : ECHO opt_whitespace echo_expr_list SEMICOLON opt_whitespace
#    """
#    p[0] = EchoStatement(p[3])
#
#def p_statement_18(p):
#    """statement : INLINE_HTML
#    """
#    p[0] = InlineHTMLStatement(p[1])
#
#def p_statement_19(p):
#    """statement : expr SEMICOLON opt_whitespace
#    """
#    p[0] = ExpressionStatement(p[1])
#
#def p_statement_20(p):
#    """statement : USE opt_whitespace use_filename SEMICOLON opt_whitespace
#    """
#    p[0] = UseStatement(p[3])
#
#def p_statement_21(p):
#    """statement : UNSET opt_whitespace LPAREN opt_whitespace unset_variables RPAREN opt_whitespace SEMICOLON opt_whitespace
#    """
#    p[0] = UnsetStatement(p[5])
#
#def p_statement_22(p):
#    """statement : FOREACH opt_whitespace LPAREN opt_whitespace variable AS opt_whitespace foreach_variable foreach_optional_arg LPAREN opt_whitespace foreach_statement
#    """
#    p[0] = ForeachStatement(p[5], p[8], p[9], p[12])
#
#def p_statement_23(p):
#    """statement : FOREACH opt_whitespace LPAREN opt_whitespace expr_without_variable AS opt_whitespace variable foreach_optional_arg LPAREN opt_whitespace foreach_statement
#    """
#    p[0] = ForeachStatement(p[5], p[8], p[9], p[12])
#
#def p_statement_24(p):
#    """statement : DECLARE opt_whitespace LPAREN opt_whitespace declare_list RPAREN opt_whitespace declare_statement
#    """
#    p[0] = DeclareStatement(p[5], p[8])

def p_statement_25(p):
    """statement : SEMICOLON opt_whitespace
    """
    p[0] = EmptyStatement()

#def p_statement_26(p):
#    """statement : TRY opt_whitespace LBRACE opt_whitespace statement_list RBRACE opt_whitespace CATCH opt_whitespace LPAREN opt_whitespace fully_qualified_class_name VARIABLE opt_whitespace RPAREN opt_whitespace LBRACE opt_whitespace statement_list RBRACE opt_whitespace additional_catches
#    """
#    p[0] = TryStatement(p[5], p[12], p[13], ...)
#
#def p_statement_27(p):
#    """statement : THROW opt_whitespace expr SEMICOLON opt_whitespace
#    """
#    p[0] = ThrowStatement(p[3])

def p_elseif_list(p):
    """elseif_list : """
    pass

#def p_elseif_list_2(p):
#    """elseif_list : elseif_list ELSEIF opt_whitespace LPAREN opt_whitespace expr RPAREN opt_whitespace statement
#    """
#    pass

def p_else_single_1(p):
    """else_single : """
    pass

def p_else_single_2(p):
    """else_single : ELSE opt_whitespace statement"""
    p[0] = p[3]

def p_expr_1(p):
    """expr : variable
    """
    p[0] = VariableExpr(p[1])

def p_expr_2(p):
    """expr : expr_without_variable
    """
    p[0] = p[1]

#def p_expr_without_variable_1(p):
#    """expr_without_variable : LIST opt_whitespace LPAREN opt_whitespace assignment_list RPAREN opt_whitespace ASSIGN opt_whitespace expr
#    """
#    p[0] = ListExpr(p[5], p[10])
#
def p_expr_without_variable_2(p):
    """expr_without_variable : variable ASSIGN opt_whitespace expr
    """
    p[0] = AssignExpr(p[1], False, p[4])

#def p_expr_without_variable_3(p):
#    """expr_without_variable : variable ASSIGN opt_whitespace AMPERSAND opt_whitespace variable
#    """
#    p[0] = AssignExpr(p[1], True, p[6])
#
#def p_expr_without_variable_4(p):
#    """expr_without_variable : variable ASSIGN opt_whitespace AMPERSAND opt_whitespace NEW opt_whitespace class_name_reference ctor_arguments
#    """
#    p[0] = AssignNewExpr(p[1], p[8], p[9])
#
#def p_expr_without_variable_5(p):
#    """expr_without_variable : NEW opt_whitespace class_name_reference ctor_arguments
#    """
#    p[0] = NewExpr(p[3], p[4])
#
#def p_expr_without_variable_6(p):
#    """expr_without_variable : CLONE opt_whitespace expr
#    """
#    p[0] = CloneExpr(p[3])
#
#def p_expr_without_variable_7(p):
#    """expr_without_variable :   variable PLUS_EQUAL opt_whitespace expr
#                               | variable MINUS_EQUAL opt_whitespace expr
#                               | variable MUL_EQUAL opt_whitespace expr
#                               | variable DIV_EQUAL opt_whitespace expr
#                               | variable CONCAT_EQUAL opt_whitespace expr
#                               | variable MOD_EQUAL opt_whitespace expr
#                               | variable AND_EQUAL opt_whitespace expr
#                               | variable OR_EQUAL opt_whitespace expr
#                               | variable XOR_EQUAL opt_whitespace expr
#                               | variable SL_EQUAL opt_whitespace expr
#                               | variable SR_EQUAL opt_whitespace expr
#                               | expr BOOLEAN_OR opt_whitespace expr
#                               | expr BOOLEAN_AND opt_whitespace expr
#                               | expr LOGICAL_OR opt_whitespace expr
#                               | expr LOGICAL_AND opt_whitespace expr
#                               | expr LOGICAL_XOR opt_whitespace expr
#                               | expr PIPE opt_whitespace expr
#                               | expr AMPERSAND opt_whitespace expr
#                               | expr CARET opt_whitespace expr
#                               | expr DOT opt_whitespace expr
#                               | expr PLUS opt_whitespace expr
#                               | expr MINUS opt_whitespace expr
#                               | expr STAR opt_whitespace expr
#                               | expr SLASH opt_whitespace expr
#                               | expr PERCENT opt_whitespace expr
#                               | expr SL opt_whitespace expr
#                               | expr SR opt_whitespace expr
#                               | expr IS_IDENTICAL opt_whitespace expr
#                               | expr IS_NOT_IDENTICAL opt_whitespace expr
#                               | expr IS_EQUAL opt_whitespace expr
#                               | expr IS_NOT_EQUAL opt_whitespace expr
#                               | expr SMALLER opt_whitespace expr
#                               | expr IS_SMALLER_OR_EQUAL opt_whitespace expr
#                               | expr GREATER opt_whitespace expr
#                               | expr IS_GREATER_OR_EQUAL opt_whitespace expr
#    """
#    p[0] = OperationExpression(p[1], p[2], p[4])
#
#def p_expr_without_variable_8(p):
#    """expr_without_variable : variable INC opt_whitespace
#    """
#    p[0] = PostIncExpr(p[1])
#
#def p_expr_without_variable_9(p):
#    """expr_without_variable : INC opt_whitespace variable
#    """
#    p[0] = PreIncExpr(p[3])
#
#def p_expr_without_variable_10(p):
#    """expr_without_variable : variable DEC opt_whitespace
#    """
#    p[0] = PostDecExpr(p[1])
#
#def p_expr_without_variable_11(p):
#    """expr_without_variable : DEC opt_whitespace variable
#    """
#    p[0] = PreDecExpr(p[3])
#
#def p_expr_without_variable_12(p):
#    """expr_without_variable :   PLUS opt_whitespace expr
#                               | MINUS opt_whitespace expr
#                               | EXCL opt_whitespace expr
#                               | TILDE opt_whitespace expr
#    """
#    p[0] = UnaryExpr(p[1], p[3])
#
#def p_expr_without_variable_13(p):
#    """expr_without_variable : expr INSTANCEOF opt_whitespace class_name_reference
#    """
#    p[0] = InstanceOfExpr(p[1], p[4])
#
#def p_expr_without_variable_14(p):
#    """expr_without_variable : LPAREN opt_whitespace expr RPAREN opt_whitespace
#    """
#    p[0] = ParenExpr(p[3])
#
def p_expr_without_variable_15(p):
    """expr_without_variable : expr QUESTION opt_whitespace expr COLON opt_whitespace expr
    """
    p[0] = TernaryIfExpr(p[1], p[4], p[7])

def p_expr_without_variable_16(p):
    """expr_without_variable : ISSET opt_whitespace LPAREN opt_whitespace isset_variables RPAREN opt_whitespace
    """
    p[0] = IssetExpr(p[5])

def p_expr_without_variable_17(p):
    """expr_without_variable : EMPTY opt_whitespace LPAREN opt_whitespace variable RPAREN opt_whitespace
    """
    p[0] = EmptyExpr(p[5])

#def p_expr_without_variable_18(p):
#    """expr_without_variable : INCLUDE opt_whitespace expr
#    """
#    p[0] = IncludeExpr(p[3])
#
#def p_expr_without_variable_19(p):
#    """expr_without_variable : INCLUDE_ONCE opt_whitespace expr
#    """
#    p[0] = IncludeOnceExpr(p[3])
#
#def p_expr_without_variable_20(p):
#    """expr_without_variable : EVAL opt_whitespace LPAREN opt_whitespace expr RPAREN opt_whitespace
#    """
#    p[0] = EvalExpr(p[5])
#
#def p_expr_without_variable_21(p):
#    """expr_without_variable : REQUIRE opt_whitespace expr
#    """
#    p[0] = RequireExpr(p[3])
#
#def p_expr_without_variable_22(p):
#    """expr_without_variable : REQUIRE_ONCE opt_whitespace expr
#    """
#    p[0] = RequireOnceExpr(p[3])
#
#def p_expr_without_variable_23(p):
#    """expr_without_variable :   LPAREN opt_whitespace INT opt_whitespace RPAREN opt_whitespace expr
#                               | LPAREN opt_whitespace INTEGER opt_whitespace RPAREN opt_whitespace expr
#                               | LPAREN opt_whitespace REAL opt_whitespace RPAREN opt_whitespace expr
#                               | LPAREN opt_whitespace DOUBLE opt_whitespace RPAREN opt_whitespace expr
#                               | LPAREN opt_whitespace FLOAT opt_whitespace RPAREN opt_whitespace expr
#                               | LPAREN opt_whitespace STRING opt_whitespace RPAREN opt_whitespace expr
#                               | LPAREN opt_whitespace BINARY opt_whitespace RPAREN opt_whitespace expr
#                               | LPAREN opt_whitespace ARRAY opt_whitespace RPAREN opt_whitespace expr
#                               | LPAREN opt_whitespace OBJECT opt_whitespace RPAREN opt_whitespace expr
#                               | LPAREN opt_whitespace BOOL opt_whitespace RPAREN opt_whitespace expr
#                               | LPAREN opt_whitespace BOOLEAN opt_whitespace RPAREN opt_whitespace expr
#                               | LPAREN opt_whitespace UNSET opt_whitespace RPAREN opt_whitespace expr
#    """
#    p[0] = CastExpr(p[3], p[7])
#
#def p_expr_without_variable_24(p):
#    """expr_without_variable : AT opt_whitespace expr
#    """
#    p[0] = AtExpr(p[3])
#
#def p_expr_without_variable_25(p):
#    """expr_without_variable : scalar
#    """
#    p[0] = ScalarExpr(p[1])
#
#def p_expr_without_variable_26(p):
#    """expr_without_variable : ARRAY opt_whitespace LPAREN opt_whitespace array_pair_list RPAREN opt_whitespace
#    """
#    p[0] = ArrayExpr(p[5])
#
#def p_expr_without_variable_27(p):
#    """expr_without_variable : LBACKTICK opt_whitespace encaps_list RBACKTICK opt_whitespace
#    """
#    p[0] = BacktickExpr(p[3])
#
#def p_expr_without_variable_28(p):
#    """expr_without_variable : PRINT opt_whitespace expr
#    """
#    p[0] = PrintExpr(p[3])

def p_variable_1(p):
    """variable : base_variable_with_function_calls
    """
    p[0] = p[1]

#def p_variable_2(p):
#    """variable : base_variable_with_function_calls OBJECT_OPERATOR opt_whitespace object_property method_or_not variable_properties
#    """
#
def p_base_variable_with_function_calls_1(p):
    """base_variable_with_function_calls : base_variable
    """
    p[0] = p[1]

# def p_base_variable_with_function_calls_2(p):
#     """p_base_variable_with_function_calls : function_call
#     """
#
def p_base_variable(p):
    """base_variable :   reference_variable
    """
#                       | simple_indirect_reference reference_variable
#                       | static_member
    p[0] = p[1]

def p_reference_variable(p):
    """reference_variable :   compound_variable
                            | reference_variable LSQBRACKET opt_whitespace dim_offset RSQBRACKET opt_whitespace
    """
#                            | reference_variable LBRACE opt_whitespace expr RBRACE
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ArraySubscript(p[1], p[4])

def p_dim_offset(p):
    """dim_offset :   expr
                    |
    """
    if len(p) == 2:
        p[0] = p[1]

def p_compound_variable(p):
    """compound_variable :   VARIABLE opt_whitespace
    """
#                           | DOLLAR opt_whitespace LBRACE opt_whitespace expr RBRACE opt_whitespace
    p[0] = Variable(p[1])

def p_isset_variables(p):
    """isset_variables :   variable
                         | isset_variables COMMA opt_whitespace variable
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[4])

def p_function_declaration_statement(p):
    """function_declaration_statement : FUNCTION whitespace is_reference opt_whitespace IDENTIFIER opt_whitespace LPAREN opt_whitespace parameter_list RPAREN opt_whitespace LBRACE opt_whitespace statement_list RBRACE opt_whitespace
    """
    p[0] = FunctionDeclaration(p[5], p[3], p[9], p[14])

def p_is_reference(p):
    """is_reference :   AMPERSAND
                      |
    """
    p[0] = len(p) > 1

def p_parameter_list(p):
    """parameter_list :   non_empty_parameter_list
                        |
    """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]

def p_non_empty_parameter_list(p):
    """non_empty_parameter_list :   parameter
                                  | non_empty_parameter_list COMMA opt_whitespace parameter
    """
    if len(p) > 2:
        p[0] = p[1]
        p[0].append(Parameter(p[4]))
    else:
        p[0] = [p[1]]

def p_parameter(p):
    """parameter :   opt_class_type is_reference VARIABLE opt_whitespace
                   | opt_class_type is_reference VARIABLE opt_whitespace ASSIGN opt_whitespace static_scalar
    """
    if len(p) > 5:
        p[0] = Parameter(p[3], p[2], p[1], p[7])
    else:
        p[0] = Parameter(p[3], p[2], p[1])

def p_opt_class_type(p):
    """opt_class_type :   IDENTIFIER opt_whitespace
                        | ARRAY opt_whitespace
                        |
    """
    if len(p) > 1:
        p[0] = p[1]

def p_class_declaration_statement_1(p):
    """class_declaration_statement :   class_entry_type IDENTIFIER opt_whitespace extends_from implements_list LBRACE opt_whitespace class_statement_list RBRACE opt_whitespace
    """
    p[0] = ClassDeclaration("class", p[2], p[1], p[4], p[5], p[8])

def p_class_declaration_statement_2(p):
    """class_declaration_statement : INTERFACE opt_whitespace IDENTIFIER opt_whitespace interface_extends_list LBRACE opt_whitespace class_statement_list RBRACE opt_whitespace
    """
    p[0] = ClassDeclaration("interface", p[3], None, p[5], [], p[8])

def p_class_entry_type(p):
    """class_entry_type :   CLASS opt_whitespace
                          | ABSTRACT opt_whitespace CLASS opt_whitespace
                          | FINAL opt_whitespace CLASS opt_whitespace
    """
    if len(p) > 3:
        p[0] = p[1]

def p_extends_from(p):
    """extends_from :   EXTENDS opt_whitespace IDENTIFIER opt_whitespace
                      |
    """
    if len(p) > 1:
        p[0] = [p[3]]
    else:
        p[0] = []

def p_implements_list(p):
    """implements_list :   IMPLEMENTS opt_whitespace interface_list
                         |
    """
    if len(p) > 1:
        p[0] = p[3]
    else:
        p[0] = []

def p_interface_list(p):
    """interface_list : IDENTIFIER opt_whitespace
                        | interface_list COMMA opt_whitespace IDENTIFIER opt_whitespace
    """
    if len(p) == 3:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[4])

def p_interface_extends_list(p):
    """interface_extends_list :   EXTENDS opt_whitespace interface_list
                                |
    """
    if len(p) > 1:
        p[0] = p[3]
    else:
        p[0] = []

def p_class_statement_list(p):
    """class_statement_list :   class_statement_list class_statement
                              |
    """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]
        p[0].append(p[2])

def p_class_statement(p):
    """class_statement :   variable_modifiers class_variable_declaration SEMICOLON opt_whitespace
                         | class_constant_declaration SEMICOLON opt_whitespace
                         | method_modifiers FUNCTION opt_whitespace is_reference IDENTIFIER opt_whitespace LPAREN opt_whitespace parameter_list RPAREN opt_whitespace method_body
    """
    if len(p) == 5:
        p[0] = ClassVariableList(p[1], p[2])
    if len(p) == 4:
        p[0] = ClassConstantsList(p[1])
    if len(p) == 13:
        p[0] = MethodDeclaration(p[5], p[1], p[4], p[9], p[12])

def p_variable_modifiers_1(p):
    """variable_modifiers : non_empty_member_modifiers
    """
    p[0] = p[1]

def p_variable_modifiers_2(p):
    """variable_modifiers : VAR opt_whitespace
    """
    p[0] = [p[1]]

def p_method_modifiers(p):
    """method_modifiers :   non_empty_member_modifiers
                          |
    """
    p[0] = []
    if len(p) > 1:
        p[0] = p[1]

def p_non_empty_member_modifiers(p):
    """non_empty_member_modifiers :   member_modifier
                                    | non_empty_member_modifiers member_modifier
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])

def p_member_modifier(p):
    """member_modifier :   PUBLIC opt_whitespace
                         | PROTECTED opt_whitespace
                         | PRIVATE opt_whitespace
                         | STATIC opt_whitespace
                         | ABSTRACT opt_whitespace
                         | FINAL opt_whitespace
    """
    p[0] = p[1]

def p_class_variable_declaration_1(p):
    """class_variable_declaration :   class_variable_declaration COMMA opt_whitespace VARIABLE opt_whitespace
                                    | class_variable_declaration COMMA opt_whitespace VARIABLE opt_whitespace ASSIGN opt_whitespace static_scalar
    """
    p[0] = p[1]
    if len(p) == 6:
        p[0].append(ClassVariable(p[4]))
    else:
        p[0].append(ClassVariable(p[4], p[8]))

def p_class_variable_declaration_2(p):
    """class_variable_declaration :   VARIABLE opt_whitespace
                                    | VARIABLE opt_whitespace ASSIGN opt_whitespace static_scalar
    """
    if len(p) == 3:
        p[0] = [ClassVariable(p[1])]
    else:
        p[0] = [ClassVariable(p[1], p[5])]
   
def p_class_constant_declaration(p):
    """class_constant_declaration :   class_constant_declaration COMMA opt_whitespace IDENTIFIER opt_whitespace ASSIGN opt_whitespace static_scalar
                                    | CONST opt_whitespace IDENTIFIER opt_whitespace ASSIGN opt_whitespace static_scalar
    """
    if len(p) == 9:
        p[0] = p[1]
        p[0].append(ClassConstant(p[4], p[8]))
    if len(p) == 8:
        p[0] = [ClassConstant(p[3], p[7])]

def p_method_body(p):
    """method_body :   SEMICOLON opt_whitespace
                     | LBRACE opt_whitespace statement_list RBRACE opt_whitespace
    """
    if len(p) > 3:
        p[0] = p[3]

def p_static_scalar(p):
    """static_scalar :   common_scalar
                       | IDENTIFIER opt_whitespace
                       | PLUS opt_whitespace static_scalar
                       | MINUS opt_whitespace static_scalar
                       | ARRAY opt_whitespace LPAREN opt_whitespace static_array_pair_list RPAREN opt_whitespace
                       | static_class_constant
    """
    if len(p) == 2:
        p[0] = p[1]
    if len(p) == 3:
        p[0] = Scalar(p[1])
    if len(p) == 4:
        p[0] = p[3]
        if p[1] == '-':
            p[0].neg()
    if len(p) == 8:
        p[0] = StaticArray(p[5])

def p_common_scalar(p):
    """common_scalar :   NUMBER opt_whitespace
                       | CONSTANT_DQ_STRING opt_whitespace
                       | CONSTANT_SQ_STRING opt_whitespace
                       | CURRENT_LINE opt_whitespace
                       | CURRENT_FILE opt_whitespace
                       | CURRENT_CLASS opt_whitespace
                       | CURRENT_METHOD opt_whitespace
                       | CURRENT_FUNCTION opt_whitespace
    """
    p[0] = Scalar(p[1])

def p_static_array_pair_list(p):
    """static_array_pair_list :   non_empty_static_array_pair_list opt_comma
                                | 
    """
    if len(p) > 1:
        p[0] = p[1]
    else:
        p[0] = []

def p_opt_comma(p):
    """opt_comma :   COMMA opt_whitespace
                   |
    """
    pass

def p_non_empty_static_array_pair_list_1(p):
    """non_empty_static_array_pair_list :   static_scalar
                                          | static_scalar DOUBLE_ARROW opt_whitespace static_scalar
    """
    if len(p) == 2:
        p[0] = [p[1]]
    if len(p) == 5:
        p[0] = [Pair(p[1], p[4])]

def p_non_empty_static_array_pair_list_2(p):
    """non_empty_static_array_pair_list :   non_empty_static_array_pair_list COMMA opt_whitespace static_scalar
                                          | non_empty_static_array_pair_list COMMA opt_whitespace static_scalar DOUBLE_ARROW opt_whitespace static_scalar
    """
    if len(p) == 5:
        p[0] = p[1]
        p[0].append(p[4])
    if len(p) == 8:
        p[0] = p[1]
        p[0].append(Pair(p[4], p[7]))

def p_static_class_constant(p):
    """static_class_constant : IDENTIFIER opt_whitespace DOUBLECOLON opt_whitespace IDENTIFIER opt_whitespace
    """
    p[0] = Scalar(p[1] + "::" + p[5])

def p_whitespace(p):
    """whitespace :   whitespace TAB
                    | whitespace SPACE
                    | whitespace NEWLINE
                    | TAB
                    | SPACE
                    | NEWLINE
    """
    pass

def p_opt_whitespace(p):
    """opt_whitespace : 
                        | whitespace
    """
    pass

def p_html_1(p):
    """html : html HTMLCHAR
    """
    if p[1] is None:
        p[0] = p[2]
    else:
        p[0] = p[1] + p[2]

def p_html_2(p):
    """html : HTMLCHAR
    """
    p[0] = p[1]

def p_error(p):
    print 'Syntax error on line %d' % p.lexer.lineno

yacc.yacc(debug=1)

# ast classes

class File:
    def __init__(self, parts, part = None):
        self.parts = parts
        if part is not None:
            self.parts.append(part)

    def out(self, config):
        res = []
        for part in self.parts:
            res.append(part.out(config))
        res = ''.join(res)
        if res[-1] != '\n':
            res = res + '\n'
        return res

class Script:
    def __init__(self, statement_list):
        self.statement_list = statement_list

    def out(self, config):
        res = ['<?php\n']
        res.append(self.statement_list.out(config))
        res.append('?>')
        return ''.join(res)

class HTML:
    def __init__(self, s):
        self.s = s

    def out(self, config):
        return self.s

# statements

class StatementList:
    def __init__(self, statement_list):
        self.statement_list = statement_list

    def append(self, statement):
        self.statement_list.append(statement)

    def out(self, config):
        if len(self.statement_list) == 0:
            return ''
        res = []
        for statement in self.statement_list[:-1]:
            res.append(statement.out(config))
            # add empty line after certain statements if it isn't the last
            if statement.__class__ in (IfStatement, FunctionDeclaration):
                res.append('\n')
        res.append(self.statement_list[-1].out(config))
        return ''.join(res)

class EmptyStatement:
    def out(self, config):
        return config.indent() + ';\n'

class IfStatement:
    def __init__(self, cond, body, elseif_list, else_single):
        self.cond = cond
        self.body = body
        self.elseif_list = elseif_list
        self.else_single = else_single

    def out(self, config):
        res = [config.indent(), 'if (']
        res.append(self.cond.out(config))
        res.append(')\n')
        if isinstance(self.body, BlockStatement):
            res.append(self.body.out(config))
        else:
            config.incIndent()
            res.append(self.body.out(config))
            config.decIndent()
        if self.else_single is not None:
            res.append('else\n')
            if isinstance(self.else_single, BlockStatement):
                res.append(self.else_single.out(config))
            else:
                config.incIndent()
                res.append(self.else_single.out(config))
                config.decIndent()
        return ''.join(res)

class BlockStatement:
    def __init__(self, statement_list):
        self.statement_list = statement_list
    
    def out(self, config):
        res = [config.indent(), '{\n']
        config.incIndent()
        res.append(self.statement_list.out(config))
        config.decIndent()
        res.append(config.indent())
        res.append('}\n')
        return ''.join(res)

class FunctionDeclaration:
    def __init__(self, name, is_reference = False, parameter_list = [], statement_list = []):
        self.name = name
        self.is_reference = is_reference
        self.parameter_list = parameter_list
        self.statement_list = statement_list

    def out(self, config):
        res = []
        res.append(config.indent())
        res.append('function ')
        if self.is_reference:
            res.append('&')
        res.append(self.name)
        res.append('(')
        parameters = []
        for parameter in self.parameter_list:
            parameters.append(parameter.out(config))
        res.append(', '.join(parameters))
        res.append(')\n')
        res.append(config.indent())
        res.append('{\n')
        config.incIndent()
        res.append(self.statement_list.out(config))
        config.decIndent()
        res.append(config.indent())
        res.append('}\n')
        return ''.join(res)

class ClassDeclaration:
    def __init__(self, class_or_interface, name, entry_type, extends_list, implements_list, statement_list):
        self.class_or_interface = class_or_interface
        self.name = name
        self.entry_type = entry_type
        self.extends_list = extends_list
        self.implements_list = implements_list
        self.statement_list = statement_list

    def out(self, config):
        res = ['\n']
        entries = []
        if self.entry_type is not None:
            entries.append(self.entry_type)
        entries.append(self.class_or_interface)
        res.append(' '.join(entries))
        res.append(' %s' % self.name)
        if len(self.extends_list) > 0:
            res.append(' extends ')
            res.append(', '.join(self.extends_list))
        if len(self.implements_list) > 0:
            res.append(' implements ')
            interfaces = []
            for interface in self.implements_list:
                interfaces.append(interface)
            res.append(', '.join(interfaces))
        res.append('\n')
        res.append(config.indent())
        res.append('{\n')
        config.incIndent()
        for statement in self.statement_list:
            res.append(statement.out(config))
            res.append('\n')
        config.decIndent()
        res.append(config.indent())
        res.append('}\n')
        return ''.join(res)

class ClassVariable:
    def __init__(self, name, value = None):
        self.name = name
        self.value = value

    def out(self, config):
        res = [self.name]
        if self.value is not None:
            res.append(" = ")
            res.append(self.value.out(config))
        return ''.join(res)

class ClassVariableList:
    def __init__(self, modifier_list, variable_list):
        self.modifier_list = modifier_list
        self.variable_list = variable_list

    def out(self, config):
        res = [config.indent()]
        for modifier in self.modifier_list:
            res.append(modifier)
            res.append(' ')
        variables = []
        for variable in self.variable_list:
            variables.append(variable.out(config))
        res.append(', '.join(variables))
        res.append(';')
        return ''.join(res);

class ClassConstant:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def out(self, config):
        return "%s = %s" % (self.name, self.value.out(config))

class ClassConstantsList:
    def __init__(self, constant_list):
        self.constant_list = constant_list

    def out(self, config):
        res = [config.indent(), 'const ']
        constants = []
        for constant in self.constant_list:
            constants.append(constant.out(config))
        res.append(', '.join(constants))
        res.append(';')
        return ''.join(res)

class MethodDeclaration:
    def __init__(self, name, modifier_list, is_reference, parameter_list, statement_list):
        self.name = name
        self.modifier_list = modifier_list
        self.is_reference = is_reference
        self.parameter_list = parameter_list
        self.statement_list = statement_list

    def out(self, config):
        res = ['\n', config.indent()]
        for modifier in self.modifier_list:
            res.append('%s ' % modifier)
        res.append('function ')
        if self.is_reference:
            res.append('&')
        res.append('%s(' % self.name)
        parameters = []
        for parameter in self.parameter_list:
            parameters.append(parameter.out(config))
        res.append(', '.join(parameters))
        res.append(')')
        if self.statement_list is None:
            # abstract method
            res.append(';')
        else:
            res.append('\n')
            res.append(config.indent())
            res.append('{\n')
            config.incIndent()
            res.append(self.statement_list.out(config))
            config.decIndent()
            res.append(config.indent())
            res.append('}')
        return ''.join(res)

class Parameter:
    def __init__(self, name, is_reference, class_type, value = None):
        self.name = name
        self.is_reference = is_reference
        self.class_type = class_type
        self.value = value

    def out(self, config):
        res = []
        if self.class_type is not None:
            res.append(self.class_type + " ")
        if self.is_reference:
            res.append('&')
        res.append(self.name)
        if self.value is not None:
            res.append(" = ")
            res.append(self.value.out(config))
        return ''.join(res)

class Scalar:
    def __init__(self, value):
        self.value = value
        self.negated = False

    def neg(self):
        self.negated = not self.negated

    def out(self, config):
        res = self.value
        if not isinstance(self.value, types.StringTypes):
            res = self.value.out(config)
        if self.negated:
            return '-' + res
        return res

class StaticArray:
    def __init__(self, element_list):
        self.element_list = element_list

    def out(self, config):
        res = ['array(']
        elements = []
        for element in self.element_list:
            elements.append(element.out(config))
        res.append(', '.join(elements))
        res.append(')')
        return ''.join(res)

class Pair:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def out(self, config):
        return '%s => %s' % (self.key.out(config), self.value.out(config))

class Variable:
    def __init__(self, var):
        self.var = var

    def out(self, config):
        return self.var

class ArraySubscript:
    def __init__(self, var, index):
        self.var = var
        self.index = index

    def out(self, config):
        res = [self.var.out(config), '[']
        if self.index is not None:
            res.append(self.index.out(config))
        res.append(']')
        return ''.join(res)

class EmptyExpr:
    def __init__(self, what):
        self.what = what

    def out(self, config):
        return 'empty(%s)' % self.what.out(config)

class AssignExpr:
    def __init__(self, lhs, as_reference, expr):
        self.lhs = lhs
        self.as_reference = as_reference
        self.expr = expr

    def out(self, config):
        res = [self.lhs.out(config), ' = ', self.expr.out(config)]
        return ''.join(res)

class IssetExpr:
    def __init__(self, isset_variables):
        self.isset_variables = isset_variables

    def out(self, config):
        res = ['isset(']
        vars = []
        for var in self.isset_variables:
            vars.append(var.out(config))
        res.append(', '.join(vars))
        res.append(')')
        return ''.join(res)

class TernaryIfExpr:
    def __init__(self, cond, body_true, body_false):
        self.cond = cond
        self.body_true = body_true
        self.body_false = body_false
    
    def out(self, config):
        res = [self.cond.out(config), ' ? ', self.body_true.out(config), ' : ', self.body_false.out(config)]
        return ''.join(res)

class ReturnStatement:
    def out(self, config):
        return config.indent() + 'return;\n'

# main

import sys

def indentstring(s):
    # sometimes we parse several files in one run
    # so we use a throw-away clone of the initial lexer with a clean state
    mylexer = lexer.clone()
    myyacc = yacc.yacc()
    res = myyacc.parse(s, lexer=mylexer, debug=1)
    config = Config()
    if res is not None:
        return res.out(config)
    return ''

def indentfile(infilename, outfilename):
    outf = file(outfilename, 'w')
    instring = open(infilename).read()
    if len(instring) != 0:
        outf.write(indentstring(instring))
    outf.close()

def main():
    onlytokens = False
    fname = sys.argv[1]
    if sys.argv[1] == '--tokens':
        onlytokens = True
        fname = sys.argv[2]

    s = open(fname).read()
    if len(s) == 0:
        sys.exit(1)

    if onlytokens:
        lex.input(s)
        while 1:
            tok = lex.token()
            if not tok:
                break
            print tok
    else:
        sys.stdout.write(indentstring(s))

if __name__ == '__main__':
    main()
