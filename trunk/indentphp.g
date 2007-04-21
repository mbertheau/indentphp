#!/usr/bin/env python

# indentphp is (c) 2007 by Markus Bertheau
# indentphp is distributed under the GNU General Public License Version 2

# configuration

strIndent = '    '

# end configuration

from sys import stdout

# grammar

%%

parser Php:
    token END:              "$"
    token PHPSTART:         "<\\?php"
    token PHPEND:           "\\?>"
    token CR:               "\r"
    token LF:               "\n"
    token WHITESPACE:       "[ \t\r\n]"
    token CHAR:             "."

    rule main:              {{ result = [] }}
                            (
                              html {{ result.append(html) }}
                            | script {{ result.append(script) }}
                            )*
                            END {{ return result }}

    rule html:              {{ result = [] }} (
                            CHAR {{ result.append(CHAR) }}
                            )+ {{ return ('html', ''.join(result)) }}

    rule script:            PHPSTART {{ result = [] }}
                            ( 
                            whitespace {{ result.append(('whitespace', whitespace)) }}
                            | slash_comment {{ result.append(('slash_comment', slash_comment)) }}
                            | hash_comment {{ result.append(('hash_comment', hash_comment)) }}
                            | statement {{ result.append(('statement', statement)) }}
                            )*
                            PHPEND {{ return ('php', result) }}

    rule slash_comment:     "//" comment_to_eol {{ return comment_to_eol }}

    rule hash_comment:      "#" comment_to_eol {{ return comment_to_eol }}

    rule statement:         "statement;" {{ return 'statement;' }}

    rule comment_to_eol:    {{ result = [] }}
                            (
                            CHAR {{ result.append(CHAR) }}
                            )*
                            eol {{ return (''.join(result), eol) }}

    rule eol:               (
                            CR {{ result = CR }}
                            [ LF {{ result = CR + LF }} ]
                            | LF {{ result = LF }}
                            ) {{ return result }}

    rule whitespace:        {{ result = [] }}
                            (
                            WHITESPACE {{ result.append(WHITESPACE) }}
                            )+ {{ return ''.join(result) }}

%%

class Writer:
    def __init__(self, ast):
        self.ast = ast

    def out(self):
        for item in self.ast:
            if item[0] == 'html':
                sys.stdout.write(item[1])
            if item[0] == 'php':
                sys.stdout.write('<?php\n')
                self.out_php(item[1])
                sys.stdout.write('\n?>')

    def out_php(self, ast):
        self.indent = 0
        for item in ast:
            if item[0] == 'whitespace':
                pass # skip whitespace
            if item[0] == 'hash_comment':
                sys.stdout.write('# ' + item[1][0].strip() + '\n')
            if item[0] == 'slash_comment':
                sys.stdout.write('// ' + item[1][0].strip() + '\n')
            if item[0] == 'statement':
                sys.stdout.write(item[1] + '\n')

def main():
    #parse('main', file('Postgres.php').read())
    ast = parse('main', """<html><head><title><?php
    
# comment
    //comment2
    statement;
    //comment 3
    ?></title></head></html>""")

    writer = Writer(ast)
    writer.out()

if __name__ == '__main__':
    main()
