#!/usr/bin/env python

# vim: set ft=python

# indentphp is (c) 2007 by Markus Bertheau
# indentphp is distributed under the GNU General Public License Version 2

# configuration

strIndent = '    '
lineLength = 80

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
    token NUMBER:           "(0x[0-9a-fA-F]+|[0-9]+|[0-9]*[\.][0-9]+|[0-9]+[\.][0-9]*)([eE][+-]?[0-9]+)?"
    token IDENTIFIER:       "[a-zA-Z_][a-zA-Z_0-9]*"
    token CONSTANT_DQ_STRING: "\"([^$\"\\\\]|(\\\\.))*\""
    token CONSTANT_SQ_STRING: "\'([^$\'\\\\]|(\\\\.))*\'"
    token CHAR:             "."

    rule main:                              {{ result = [] }}
                            ( html          {{ result.append(html) }}
                            | script        {{ result.append(script) }}
                            )*
                            END             {{ return result }}

    rule html:                              {{ result = [] }} (
                              CHAR          {{ result.append(CHAR) }}
                            | WHITESPACE    {{ result.append(WHITESPACE) }}
                            )+              {{ return ('html', ''.join(result)) }}

    rule script:            PHPSTART        {{ result = [] }}
                            ( whitespace    {{ result.append(whitespace) }}
                            | slash_comment {{ result.append(slash_comment) }}
                            | hash_comment  {{ result.append(hash_comment) }}
                            | statement     {{ result.append(statement) }}
                            | function_declaration_statement
                                            {{ result.append(('function', function_declaration_statement)) }}
                            )*
                            PHPEND          {{ return ('php', result) }}

    rule opt_comment:                       {{ result = [] }}
                            ( whitespace
                            | slash_comment {{ result.append(slash_comment) }}
                            | hash_comment  {{ result.append(hash_comment) }}
                            )*              {{ return result }}

    rule slash_comment:     "//" comment_to_eol
                                            {{ return ('slash_comment', comment_to_eol) }}

    rule hash_comment:      "#" comment_to_eol
                                            {{ return ('hash_comment', comment_to_eol) }}

    rule function_declaration_statement:    {{ is_reference = False; function_comment = None }}
                            "function"
                            whitespace
                            [
                                "&"         {{ is_reference = True }}
                            ]
                            IDENTIFIER opt_whitespace
                            "\\(" opt_parameter_list "\\)"
                            opt_comment     {{ function_comment = opt_comment }}
                            "{" opt_whitespace
                            statement opt_whitespace
                            "}"             {{ return (is_reference, IDENTIFIER, opt_parameter_list, function_comment, statement) }}

    rule opt_parameter_list:                {{ result = None }}
                            [ parameter_list
                                            {{ result = parameter_list }}
                            ]               {{ return result }}
    
    rule parameter_list:                    {{ result = [] }}
                            parameter       {{ result.append(parameter) }}
                            ( "," opt_whitespace parameter
                                            {{ result.append(parameter) }}
                            )*              {{ return result }}

    rule parameter:                         {{ defarg = None }}
                            "\$" IDENTIFIER opt_whitespace
                            [ "=" opt_whitespace static_scalar
                                            {{ defarg = static_scalar }}
                            ]
                            opt_whitespace  {{ return ('parameter', IDENTIFIER, defarg) }}

    rule static_scalar:     (
                            common_scalar   {{ return common_scalar }}
                            | IDENTIFIER    {{ id = IDENTIFIER # a constant }}
                              [ "::"
                              IDENTIFIER    {{ return id + "::" + IDENTIFIER }}
                              ]             {{ return id }}
                            | "\\+" static_scalar
                                            {{ return static_scalar }}
                            | "-" static_scalar
                                            {{ return "-" + static_scalar }}
                            | "array" opt_whitespace
                              opt_static_array_pair_list
                                            {{ return ('array', opt_static_array_pair_list) }}
                            )

    rule opt_static_array_pair_list:
                                            {{ result = [] }}
                            "\\(" opt_whitespace
                            static_array_pair_list
                                            {{ return static_array_pair_list }}

    rule static_array_pair_list:
                                            {{ result = [] }}
                            ( "\\)"         {{ return result }}
                            | static_array_element
                                            {{ result.append(static_array_element); static_array_element = None }}
                              ( "," opt_whitespace
                                ( "\\)"     {{ return result }}
                                | static_array_pair_list
                                            {{ result += static_array_pair_list; static_array_pair_list = None }}
                                )
                              | "\\)"       {{ return result }}
                              )
                            )
                            {{ return result }}
                            
    rule static_array_element:
                                            {{ value = None }}
                            static_scalar opt_whitespace
                                            {{ key = static_scalar }}
                            [ "=>" opt_whitespace static_scalar
                                            {{ value = static_scalar }}
                            ]
                            opt_whitespace  {{ return ('array_element', key, value) }}
                            

    rule common_scalar:     (
                            NUMBER          {{ return NUMBER }}
                            | CONSTANT_DQ_STRING
                                            {{ return CONSTANT_DQ_STRING }}
                            | CONSTANT_SQ_STRING
                                            {{ return CONSTANT_SQ_STRING }}
                            | '__LINE__'    {{ return '__LINE__' }}
                            | '__FILE__'    {{ return '__FILE__' }}
                            | '__CLASS__'   {{ return '__CLASS__' }}
                            | '__METHOD__'  {{ return '__METHOD__' }}
                            | '__FUNCTION__'
                                            {{ return '__FUNCTION__' }}
                            )

    rule statement:         "statement;"    {{ return ('statement', 'statement;') }}

    rule comment_to_eol:                    {{ result = [] }}
                            (
                            CHAR            {{ result.append(CHAR) }}
                            )*
                            eol             {{ return (''.join(result), eol) }}

    rule eol:               (
                            CR              {{ result = CR }}
                            [ LF            {{ result = CR + LF }}
                            ]
                            | LF            {{ result = LF }}
                            )               {{ return result }}

    rule opt_whitespace:                    {{ result = None }}
                            [ whitespace    {{ result = whitespace }}
                            ]               {{ return result }}
    rule whitespace:                        {{ result = [] }}
                            (
                            WHITESPACE      {{ result.append(WHITESPACE) }}
                            )+              {{ return ('whitespace', ''.join(result)) }}

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
        fun = 'function %s%s(' % (ref, function[1])
        sys.stdout.write(fun)
        self.out_parameter_list(function[2], len(fun))
        sys.stdout.write(')\n{\n%s' % strIndent)
        self.out_statement(function[4])
        sys.stdout.write('}\n')
    
    def out_parameter_list(self, parameter_list, indent):
        if parameter_list is None:
            return
        out_parameters = []
        pos = indent
        for i, parameter in enumerate(parameter_list):
            par = self.out_parameter(parameter)
            # new line if line length would be > 80 and this is not the first parameter
            if i != 0:
                # calculate length of param:
                # space, param, 1 = comma (if not last param) or ")" if last,
                space = 1
                comma_or_closing_paren = 1
                if pos + space + len(par) + comma_or_closing_paren > lineLength:
                    sys.stdout.write("\n" + " " * indent)
                    pos = indent
                else:
                    sys.stdout.write(" ")
                    pos += 1
            sys.stdout.write(par)
            pos += len(par)
            if i < len(parameter_list) - 1:
                sys.stdout.write(",")
                pos += 1

    def out_parameter(self, parameter):
        res = "$%s" % parameter[1]
        if parameter[2]:
            res += " = " + self.out_scalar(parameter[2])
        return res

    def out_scalar(self, scalar):
        if type(scalar) == tuple:
            elems = []
            for elem in scalar[1]:
                elems.append(self.out_array_elem(elem))
            return  "array(%s)" % ", ".join(elems)
        else:
            return scalar

    def out_array_elem(self, elem):
        res = elem[1]
        if elem[2]:
            res += " => " + self.out_scalar(elem[2])
        return res

def main():
    #parse('main', file('Postgres.php').read())
    ast = parse('main', """<html><head><title><?php
# hash_comment
// slash_comment
statement;

function f1() {statement;}
function f2() // typo3 style comment
{
    statement;
}

function f3($param) {statement;}
function f4($p1, $p1 = "foobar", $p2 = 5, $p3 = 5,
            $p4 = 5e10, $p6 = 'biae\\'feio',
            $p7 = "ieo\\"ieo", $p8 = __LINE__,
            $p9 = __FILE__, $p10 = __CLASS__,
            $p11 = __METHOD__, $p12 = __FUNCTION__,
            $p13 = CONSTANT, $p14 = Class::class_constant,
            $p15 = +4, $p16 = -4, $p17 = array("a", "b" => "c"),
            $p18 = array(), $p19 = array(4,5,))
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
