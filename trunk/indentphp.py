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
    'SEMICOLON'
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

reserved = {
    'function' : 'FUNCTION'
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
t_php_SPACE = r'\ '
t_php_TAB = r'\t'
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
    """
#                       | class_declaration_statement
#                       | HALT_COMPILER opt_whitespace '(' opt_whitespace ')' opt_whitespace ';' opt_whitespace
    p[0] = p[1]

def p_statement(p):
    """statement : SEMICOLON opt_whitespace
    """
    p[0] = EmptyStatement()

def p_function_declaration_statement(p):
    """function_declaration_statement : FUNCTION whitespace is_reference opt_whitespace IDENTIFIER opt_whitespace LPAREN opt_whitespace RPAREN opt_whitespace LBRACE opt_whitespace statement_list RBRACE opt_whitespace
    """
    p[0] = FunctionCall(p[5], p[3], [], p[13])

def p_is_reference(p):
    """is_reference :   AMPERSAND
                      |
    """
    p[0] = len(p) > 1

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

class FunctionCall:
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
