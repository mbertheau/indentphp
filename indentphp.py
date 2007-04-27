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

from ply import lex
from ply.lex import TOKEN

states = (
    ('php','exclusive'),
)

tokens = (
    'HTML',
    'SCRIPTSTART',
    'SCRIPTEND',
    'PHP',
)

@TOKEN(r'<\?php')
def t_SCRIPTSTART(t):
    t.lexer.php_start = t.lexer.lexpos
    try:
        t.value = t.lexer.lexdata[t.lexer.php_end:t.lexer.lexpos - len('<?php')]
    except AttributeError:
        t.value = t.lexer.lexdata[0:t.lexer.lexpos - len('<?php')]
    t.type = 'HTML'
    t.lexer.begin('php')
    return t

@TOKEN(r'\?>')
def t_php_SCRIPTEND(t):
    t.lexer.php_end = t.lexer.lexpos
    t.value = t.lexer.lexdata[t.lexer.php_start:t.lexer.lexpos - len('?>')]
    t.type = 'PHP'
    t.lexer.begin('INITIAL')
    return t

def t_error(t):
    t.lexer.skip(1)

def t_php_error(t):
    t.lexer.skip(1)

lex.lex(debug=1)

# main

import sys

lex.input(file(sys.argv[1]).read())

while 1:
    tok = lex.token()
    if not tok:
        break
    print tok
