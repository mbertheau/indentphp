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
    'CONST'
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
    'const'         : 'CONST'
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
t_php_COLON = r'::'
t_php_SPACE = r'\ '
t_php_TAB = r'\t'
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
    p[0] = p[1][:]
    p[0].append(p[2])

def p_start1_4(p):
    """start1 : start1 html
    """
    p[0] = p[1][:]
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
        p[0] = p[1][:]
        p[0].append(p[2])
    else:
        p[0] = []

def p_top_statement(p):
    """top_statement :   statement
                       | function_declaration_statement
                       | class_declaration_statement
    """
    p[0] = p[1]

def p_statement(p):
    """statement : SEMICOLON opt_whitespace
    """
    p[0] = EmptyStatement()

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
        p[0] = p[1][:]
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

def p_class_declaration_statement(p):
    """class_declaration_statement :   class_entry_type IDENTIFIER opt_whitespace extends_from implements_list LBRACE opt_whitespace class_statement_list RBRACE opt_whitespace
    """
#                                     | interface_entry IDENTIFIER opt_whitespace interface_extends_list LBRACE opt_whitespace class_statement_list RBRACE opt_whitespace
    p[0] = ClassDeclaration(p[2], p[1], p[4], p[5], p[8])

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
        p[0] = p[3]

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
        p[0] = p[1][:]
        p[0].append(p[4])

def p_class_statement_list(p):
    """class_statement_list :   class_statement_list class_statement
                              |
    """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1][:]
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
        p[0] = p[1][:]
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
    p[0] = p[1][:]
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
        p[0] = p[1][:]
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
    """static_class_constant : IDENTIFIER opt_whitespace COLON opt_whitespace IDENTIFIER opt_whitespace
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
        for statement in self.statement_list:
            res.append(statement.out(config))
            res.append('\n')
        res.append('?>')
        return ''.join(res)

class HTML:
    def __init__(self, s):
        self.s = s

    def out(self, config):
        return self.s

# statements

class EmptyStatement:
    def out(self, config):
        return config.indent() + ';'

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
        statements = []
        for statement in self.statement_list:
            statements.append(statement.out(config))
            statements.append('\n')
        res.append(''.join(statements))
        config.decIndent()
        res.append(config.indent())
        res.append('}\n')
        return ''.join(res)

class ClassDeclaration:
    def __init__(self, name, entry_type, extends, implements_list, statement_list):
        self.name = name
        self.entry_type = entry_type
        self.extends = extends
        self.implements_list = implements_list
        self.statement_list = statement_list

    def out(self, config):
        res = ['\n']
        entries = []
        if self.entry_type is not None:
            entries.append(self.entry_type)
        entries.append('class')
        res.append(' '.join(entries))
        res.append(' %s' % self.name)
        if self.extends is not None:
            res.append(' extends ')
            res.append(self.extends)
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
        res.append('}')
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
            for statement in self.statement_list:
                res.append(statement.out(config))
                res.append('\n')
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
        return "%s => %s" % (self.key.out(config), self.value.out(config))

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
