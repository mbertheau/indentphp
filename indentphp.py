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

strIndent = '    '

# tokenizer

from ply import lex, yacc
from ply.lex import TOKEN
import re

states = (
    ('php','exclusive'),
)

tokens = (
    'SCRIPTSTART',
    'SCRIPTEND',
    'PHP',
    'HTMLCHAR'
)

@TOKEN(r'<\?php')
def t_SCRIPTSTART(t):
    t.lexer.begin('php')
    return t

@TOKEN(r'\?>')
def t_php_SCRIPTEND(t):
    t.lexer.begin('INITIAL')
    return t

t_HTMLCHAR = r'.'
t_php_PHP = r'\ ;\n?'

def t_error(t):
    print "lexing error"

def t_php_error(t):
    print "lexing error in php"

lex.lex(debug=0, reflags=re.S)

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

def p_scriptwithoutend(p):
    """scriptwithoutend : SCRIPTSTART php
    """
    p[0] = p[2]

def p_script(p):
    """script : SCRIPTSTART php SCRIPTEND
    """
    p[0] = p[2]

def p_php(p):
    """php : PHP
    """
    p[0] = Script(p[1])

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
    print "Syntax error"

yacc.yacc(debug=1)

# ast classes

class File:
    def __init__(self, parts, part = None):
        self.parts = parts
        if part is not None:
            self.parts.append(part)

    def out(self):
        res = []
        for part in self.parts:
            res.append(part.out())
        res = "".join(res)
        if res[-1] != "\n":
            res = res + "\n"
        return res

class Script:
    def __init__(self, script):
        if script[-1] == '\n':
            self.script = script[:-1]
        else:
            self.script = script

    def out(self):
        return "<?php\n%s\n?>" % self.script

class HTML:
    def __init__(self, s):
        self.s = s

    def out(self):
        return self.s

# main

import sys

def indentstring(s):
    return yacc.parse(s).out()

def indentfile(infilename, outfilename):
    outf = file(outfilename, 'w')
    outf.write(indentstring(open(infilename).read()))
    outf.close()

def main():
    onlytokens = False
    fname = sys.argv[1]
    if sys.argv[1] == '--tokens':
        onlytokens = True
        fname = sys.argv[2]

    s = open(fname).read()

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
