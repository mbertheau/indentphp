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
    t.lexer.php_start = t.lexer.lexpos
    t.lexer.begin('php')
    t.lexer.skip(len('<?php'))

@TOKEN(r'\?>')
def t_php_SCRIPTEND(t):
    t.lexer.php_end = t.lexer.lexpos
    t.value = t.lexer.lexdata[t.lexer.php_start:t.lexer.lexpos - len('?>')]
    t.type = 'PHP'
    t.lexer.begin('INITIAL')
    return t

@TOKEN(r'.')
def t_HTMLCHAR(t):
    return t

def t_error(t):
    t.lexer.skip(1)

def t_php_error(t):
    # skip php contents for now; we capture it in t_php_SCRIPTEND
    t.lexer.skip(1)

lex.lex(debug=0, reflags=re.S)

# parser

import types

start = 'file'

def p_file_1(p):
    """file : file html
    """
    p[0] = File(HTML(p[2]), p[1])

def p_file_2(p):
    """file : file PHP
    """
    p[0] = File(Script(p[2]), p[1])

def p_file_3(p):
    """file : html
    """
    p[0] = File(HTML(p[1]))

def p_file_4(p):
    """file : PHP
    """
    p[0] = File(Script(p[1]))

def p_file_5(p):
    """file :
    """
    p[0] = File()

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
    def __init__(self, part = None, oldfile = None):
        self.parts = []
        if oldfile is not None:
            self.parts = oldfile.parts
        if part is not None:
            self.parts.append(part)

    def out(self):
        res = []
        for part in self.parts:
            res.append(part.out())
        return "".join(res)

class Script:
    def __init__(self, script):
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
    sys.stdout.write(indentstring(open(sys.argv[1]).read()))

if __name__ == '__main__':
    main()
