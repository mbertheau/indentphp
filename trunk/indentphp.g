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
    token IDENTIFIER:       "[a-zA-Z_][a-zA-Z_0-9]*"
    token CHAR:             "."

    rule main:              {{ result = [] }}
                            (
                              html {{ result.append(html) }}
                            | script {{ result.append(script) }}
                            )*
                            END {{ return result }}

    rule html:              {{ result = [] }} (
                            CHAR {{ result.append(CHAR) }}
                            | WHITESPACE {{ result.append(WHITESPACE) }}
                            )+ {{ return ('html', ''.join(result)) }}

    rule script:            PHPSTART {{ result = [] }}
                            ( 
                            whitespace {{ result.append(whitespace) }}
                            | slash_comment {{ result.append(slash_comment) }}
                            | hash_comment {{ result.append(hash_comment) }}
                            | statement {{ result.append(statement) }}
                            | function_declaration_statement {{ result.append(('function', function_declaration_statement)) }}
                            )*
                            PHPEND {{ return ('php', result) }}

    rule opt_comment:       {{ result = [] }} (
                            whitespace
                            | slash_comment {{ result.append(slash_comment) }}
                            | hash_comment {{ result.append(hash_comment) }}
                            )* {{ return result }}

    rule slash_comment:     "//" comment_to_eol {{ return ('slash_comment', comment_to_eol) }}

    rule hash_comment:      "#" comment_to_eol {{ return ('hash_comment', comment_to_eol) }}

    rule function_declaration_statement: {{ is_reference = False; function_comment = None }}
                            "function"
                            whitespace
                            [ "&" {{ is_reference = True }} ]
                            IDENTIFIER opt_whitespace
                            '\\(' opt_parameter_list '\\)' opt_comment {{ function_comment = opt_comment }}
                            '{' opt_whitespace
                            statement opt_whitespace
                            '}' {{ return (is_reference, IDENTIFIER, opt_parameter_list, function_comment, statement) }}

    rule opt_parameter_list:{{ result = None }}
                            [ parameter_list {{ result = parameter_list }} ]
                            {{ return result }}
    
    rule parameter_list:    {{ result = [] }}
                            parameter {{ result.append(parameter) }}
                            ( ',' opt_whitespace parameter {{ result.append(parameter) }} )*
                            {{ return result }}

    rule parameter:         "\$" IDENTIFIER opt_whitespace {{ return ('parameter', IDENTIFIER) }}

    rule statement:         "statement;" {{ return ('statement', 'statement;') }}

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

    rule opt_whitespace:    {{ result = None }} [ whitespace {{ result = whitespace }} ] {{ return result }}
    rule whitespace:        {{ result = [] }}
                            (
                            WHITESPACE {{ result.append(WHITESPACE) }}
                            )+ {{ return ('whitespace', ''.join(result)) }}

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
                self.out_comment(item)
            if item[0] == 'slash_comment':
                self.out_comment(item)
            if item[0] == 'function':
                self.out_function(item[1])
            if item[0] == 'statement':
                self.out_statement(item)

    def out_statement(self, statement):
        sys.stdout.write(statement[1] + '\n')

    def out_comment(self, comment):
        sys.stdout.write('\n')
        if comment[0] == 'slash_comment':
            sys.stdout.write('// ')
        if comment[0] == 'hash_comment':
            sys.stdout.write('# ')
        sys.stdout.write(comment[1][0].strip() + '\n')

    def out_function(self, function):
        sys.stdout.write('\n')
        if function[3]:
            for comment in function[3]:
                self.out_comment(comment)
        ref = ''
        if function[0]:
            ref = '&'
        sys.stdout.write('function %s%s(' % (ref, function[1]))
        self.out_parameter_list(function[2])
        sys.stdout.write(')\n{\n%s' % strIndent)
        self.out_statement(function[4])
        sys.stdout.write('}\n')
    
    def out_parameter_list(self, parameter_list):
        if parameter_list is None:
            return
        out_parameters = []
        for parameter in parameter_list:
            out_parameters.append(self.out_parameter(parameter))
        sys.stdout.write(", ".join(out_parameters))

    def out_parameter(self, parameter):
        return "$%s" % parameter[1]

def main():
    #parse('main', file('Postgres.php').read())
    ast = parse('main', """<html><head><title><?php
    
# comment
    //comment2
    statement;
    //comment 3
    function foobar($foobar,$barbaz , $quux) // comment for foobar
    { statement; }
#comment for bar typo3 style
    function &bar()
    { statement; }
    ?></title></head></html>
""")

    if not ast:
        return
    print ast
    writer = Writer(ast)
    writer.out()

if __name__ == '__main__':
    main()
