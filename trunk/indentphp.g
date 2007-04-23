#!/usr/bin/env python

# vim:set ft=python

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

    rule file:                              {{ result = PHPFile() }}
                            ( html          {{ result.addPart(html) }}
                            | script        {{ result.addPart(script) }}
                            )*
                            END             {{ return result }}

    rule html:                              {{ result = HTML() }} (
                              CHAR          {{ result.addPart(CHAR) }}
                            | WHITESPACE    {{ result.addPart(WHITESPACE) }}
                            )+              {{ return result }}

    rule script:            PHPSTART        {{ result = Script() }}
                            ( whitespace    {{ result.addPart(whitespace) }}
                            | slash_comment {{ result.addPart(slash_comment) }}
                            | hash_comment  {{ result.addPart(hash_comment) }}
                            | statement     {{ result.addPart(statement) }}
                            | function_declaration_statement
                                            {{ result.addPart(function_declaration_statement) }}
                            )*
                            PHPEND          {{ return result }}

    rule opt_comment:                       {{ result = CommentList() }}
                            ( whitespace
                            | slash_comment {{ result.addPart(slash_comment) }}
                            | hash_comment  {{ result.addPart(hash_comment) }}
                            )*              {{ return result }}

    rule slash_comment:     "//" comment_to_eol
                                            {{ return SlashComment(comment_to_eol) }}

    rule hash_comment:      "#" comment_to_eol
                                            {{ return HashComment(comment_to_eol) }}

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
                            "}"             {{ return FunctionDeclaration(IDENTIFIER, is_reference, opt_parameter_list, function_comment, statement) }}

    rule opt_parameter_list:                {{ result = ParameterList() }}
                            [ parameter_list
                                            {{ result = parameter_list }}
                            ]               {{ return result }}
    
    rule parameter_list:                    {{ result = ParameterList() }}
                            parameter       {{ result.addParam(parameter) }}
                            ( "," opt_whitespace parameter
                                            {{ result.addParam(parameter) }}
                            )*              {{ return result }}

    rule parameter:                         {{ defarg = None }}
                            "\$" IDENTIFIER opt_whitespace
                            [ "=" opt_whitespace static_scalar
                                            {{ defarg = static_scalar }}
                            ]
                            opt_whitespace  {{ return Parameter(IDENTIFIER, defarg) }}

    rule static_scalar:     (
                            common_scalar   {{ return common_scalar }}
                            | IDENTIFIER    {{ id = IDENTIFIER # a constant }}
                              [ "::"
                              IDENTIFIER    {{ return ClassConstant(id, IDENTIFIER) }}
                              ]             {{ return Constant(id) }}
                            | "\\+" static_scalar
                                            {{ return static_scalar }}
                            | "-" static_scalar
                                            {{ return static_scalar.neg() }}
                            | "array" opt_whitespace
                              opt_static_array_pair_list
                                            {{ return StaticArray(opt_static_array_pair_list) }}
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
                            opt_whitespace  {{ return StaticArrayElement(key, value) }}
                            

    rule common_scalar:     (
                            NUMBER          {{ return StaticNumber(NUMBER) }}
                            | CONSTANT_DQ_STRING
                                            {{ return StaticString(CONSTANT_DQ_STRING) }}
                            | CONSTANT_SQ_STRING
                                            {{ return StaticString(CONSTANT_SQ_STRING) }}
                            | '__LINE__'    {{ return CurrentLine() }}
                            | '__FILE__'    {{ return CurrentFile() }}
                            | '__CLASS__'   {{ return CurrentClass() }}
                            | '__METHOD__'  {{ return CurrentMethod() }}
                            | '__FUNCTION__'
                                            {{ return CurrentFunction() }}
                            )

    rule statement:         "statement;"    {{ return Statement() }}

    rule comment_to_eol:                    {{ result = [] }}
                            (
                            CHAR            {{ result.append(CHAR) }}
                            )*
                            eol             {{ return ''.join(result) }}

    rule eol:               (
                            CR              {{ result = CR }}
                            [ LF            {{ result = CR + LF }}
                            ]
                            | LF            {{ result = LF }}
                            )               {{ return result }}

    rule opt_whitespace:                    {{ result = None }}
                            [ whitespace    {{ result = whitespace }}
                            ]               {{ return result }}
    rule whitespace:                        {{ result = Whitespace() }}
                            (
                            WHITESPACE      {{ result.addPart(WHITESPACE) }}
                            )+              {{ return result }}

%%


class PHPFile:
    def __init__(self):
        self.parts = []

    def addPart(self, part):
        self.parts.append(part)

    def out(self):
        res = []
        for part in self.parts:
            res.append(part.out())
        return "".join(res)

class HTML:
    def __init__(self):
        self.parts = []

    def addPart(self, part):
        self.parts.append(part)

    def out(self):
        res = []
        for part in self.parts:
            res.append(part)
        return "".join(res)

class Script:
    def __init__(self):
        self.parts = []

    def addPart(self, part):
        self.parts.append(part)

    def out(self):
        res = ['<?php\n']
        for part in self.parts:
            res.append(part.out())
        res.append('\n?>')
        return "".join(res)

class Whitespace:
    def __init__(self):
        self.parts = []

    def addPart(self, part):
        self.parts.append(part)

    def out(self):
        return ""

class CommentList:
    def __init__(self):
        self.parts = []

    def addPart(self, part):
        self.parts.append(part)

    def out(self):
        res = ["\n"]
        for part in self.parts:
            res.append(part.out())
        return "".join(res)

class SlashComment:
    def __init__(self, text):
        self.text = text

    def out(self):
        return "// %s\n" % self.text

class HashComment:
    def __init__(self, text):
        self.text = text

    def out(self):
        return "# %s\n" % self.text

class ParameterList:
    def __init__(self):
        self.params = []

    def addParam(self, param):
        self.params.append(param)

    def out(self, indent):
        if len(self.params) == 0:
            return ""
        pos = indent
        res = []
        for i, param in enumerate(self.params):
            # new line if line length would be > lineLength and this is not the first parameter
            if i != 0:
                # calculate space for param:
                # space, param, comma (if not last param), ")" if last param
                space = 1
                comma_or_closing_paren = 1
                if pos + space + len(param.out()) + comma_or_closing_paren > lineLength:
                    res.append("\n%s" % (" " * indent))
                    pos = indent
                else:
                    res.append(" ")
                    pos += 1
            res.append(param.out())
            pos += len(param.out())
            if i < len(self.params):
                res.append(',')
                pos += 1
        return "".join(res)

class Parameter:
    def __init__(self, name, default_value):
        self.name = name
        self.default_value = default_value

    def out(self):
        res = ["$%s" % self.name]
        if self.default_value:
            res.append(" = ")
            res.append(self.default_value.out())
        return "".join(res)

class Constant:
    def __init__(self, name):
        self.name = name
        self.negated = False

    def neg(self):
        self.negated = not self.negated

    def out(self):
        res = []
        if self.negated:
            res.append('-')
        res.append(self.name)
        return "".join(res)

class ClassConstant:
    def __init__(self, class_name, name):
        self.class_name = class_name
        self.name = name
        self.negated = False

    def neg(self):
        self.negated = not self.negated

    def out(self):
        res = []
        if self.negated:
            res.append('-')
        res.append("%s::%s" % (self.class_name, self.name))
        return "".join(res)

class StaticString:
    def __init__(self, expr):
        self.expr = expr

    def out(self):
        return self.expr

class StaticNumber:
    def __init__(self, expr):
        self.expr = expr
        self.negate = False

    def neg(self):
        self.negate = not self.negate

    def out(self):
        return self.expr

class CurrentLine:
    def out(self):
        return '__LINE__';

class CurrentFile:
    def out(self):
        return '__FILE__';

class CurrentClass:
    def out(self):
        return '__CLASS__';

class CurrentMethod:
    def out(self):
        return '__METHOD__';

class CurrentFunction:
    def out(self):
        return '__FUNCTION__';

class StaticArray:
    def __init__(self, elements = []):
        self.elements = elements

    def out(self):
        res = []
        for element in self.elements:
            res.append(element.out())
        return "array(%s)" % ", ".join(res)

class StaticArrayElement:
    def __init__(self, key, value = None):
        self.key = key
        self.value = value

    def out(self):
        res = [self.key.out()]
        if self.value:
            res.append(' => ')
            res.append(self.value.out())
        return "".join(res)

class Statement:
    def out(self):
        return "statement;\n"

class FunctionDeclaration:
    def __init__(self, name, is_reference, params, comments, body):
        self.name = name
        self.is_reference = is_reference
        self.params = params
        self.comments = comments
        self.body = body

    def out(self):
        res = [self.comments.out()]
        ref = ''
        if self.is_reference:
            ref = "&"
        fun = 'function %s%s(' % (ref, self.name)
        res.append(fun)
        res.append(self.params.out(len(fun)))
        res.append(')\n{\n%s' % strIndent)
        res.append(self.body.out())
        res.append('}\n')
        return "".join(res)

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
            # new line if line length would be > lineLength and this is not the first parameter
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
    ast = parse('file', """<html><head><title><?php
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
    sys.stdout.write(ast.out())

if __name__ == '__main__':
    main()
