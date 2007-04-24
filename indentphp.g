#!/usr/bin/env python

# vim: ft=python

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
                            | class_declaration_statement
                                            {{ result.addPart(class_declaration_statement) }}
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
                            [ "&"           {{ is_reference = True }}
                            ] opt_whitespace
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
                                            {{ static_scalar.neg(); return static_scalar }}
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

    rule class_declaration_statement:       {{ abstract = False; final = False; extends = None; implements = None; statements = []; }}
                            ( "abstract" opt_whitespace "class" opt_whitespace
                                            {{ abstract = True }}
                            | "final" opt_whitespace "class" opt_whitespace 
                                            {{ final = True }}
                            | "class" opt_whitespace
                            )
                            IDENTIFIER opt_whitespace
                                            {{ name = IDENTIFIER }}
                            [ "extends" opt_whitespace IDENTIFIER opt_whitespace
                                            {{ extends = IDENTIFIER }}
                            ]

                            [ "implements" opt_whitespace interface_list opt_whitespace
                                            {{ implements = interface_list }}
                            ]
                            "{" opt_whitespace
                            class_statement_list
                                            {{ statements = class_statement_list }}
                            "}" opt_whitespace
                                            {{ return ClassDeclaration(abstract, final, name, extends, implements, statements) }}

    rule class_statement_list:              {{ result = [] }}
                            ( class_statement opt_whitespace
                                            {{ result.append(class_statement) }}
                            )*              {{ return result }}

    rule class_statement:   ( 
                                class_constant_declaration ";"
                                            {{ return ClassConstantDeclList(class_constant_declaration) }}
                              | "var" opt_whitespace class_variable_declaration_list ";"
                                            {{ return ClassVariableList([], class_variable_declaration_list) }}
                              | member_modifiers opt_whitespace
                              (
                                class_variable_declaration_list ";"
                                            {{ return ClassVariableList(member_modifiers, class_variable_declaration_list) }}
                                | method_declaration<<member_modifiers>>
                                            {{ return method_declaration }}
                              )
                              | method_declaration<<[]>> {{ return method_declaration }}
                              | statement   {{ return statement }}
                            )

    rule method_declaration<<modifiers>>:   {{ is_reference = False }}
                            "function" opt_whitespace
                            [ "&"           {{ is_reference = True }}
                            ] opt_whitespace
                            IDENTIFIER opt_whitespace
                            "\\(" opt_parameter_list "\\)"
                            opt_comment
                            "{" opt_whitespace "}"
                                            {{ return MethodDeclaration(modifiers, IDENTIFIER, is_reference, opt_parameter_list, opt_comment, []) }}

    rule class_constant_declaration:        {{ result = [] }}
                            "const" opt_whitespace
                            IDENTIFIER opt_whitespace "=" opt_whitespace static_scalar opt_whitespace
                                            {{ result.append(ClassConstantDeclaration(IDENTIFIER, static_scalar)) }}
                            ( "," opt_whitespace IDENTIFIER opt_whitespace "=" opt_whitespace static_scalar
                                            {{ result.append(ClassConstantDeclaration(IDENTIFIER, static_scalar)) }}
                            )*              {{ return result }}

    rule class_variable_declaration_list:   {{ result = [] }}
                            class_variable_declaration opt_whitespace
                                            {{ result.append(ClassVariable(class_variable_declaration[0], class_variable_declaration[1])) }}
                            ( "," opt_whitespace
                              class_variable_declaration
                              opt_whitespace
                                            {{ result.append(ClassVariable(class_variable_declaration[0], class_variable_declaration[1])) }}
                            )*              {{ return result }}

    rule class_variable_declaration:        {{ value = None }}
                            "\$" IDENTIFIER  opt_whitespace 
                                            {{ name = IDENTIFIER }}
                            [ "=" opt_whitespace
                              static_scalar {{ value = static_scalar }}
                            ]               {{ return (name, value) }}

    rule member_modifiers:
                            member_modifier opt_whitespace
                                            {{ result = [member_modifier] }}
                            ( member_modifier opt_whitespace
                                            {{ result.append(member_modifier) }}
                            )*              {{ return result }}

    rule member_modifier:
                            ( "public"      {{ return "public" }}
                            | "protected"   {{ return "protected" }}
                            | "private"     {{ return "private" }}
                            | "static"      {{ return "static" }}
                            | "abstract"    {{ return "abstract" }}
                            | "final"       {{ return "final" }}
                            ) opt_whitespace

    rule interface_list:    IDENTIFIER opt_whitespace
                                            {{ result = [IDENTIFIER] }}
                            ( "," opt_whitespace IDENTIFIER opt_whitespace
                                            {{ result.append(IDENTIFIER) }}
                            )*              {{ return result }}

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
        return "// %s\n" % self.text.strip()

class HashComment:
    def __init__(self, text):
        self.text = text

    def out(self):
        return "# %s\n" % self.text.strip()

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
            if i < len(self.params) - 1:
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
        self.negated = False

    def neg(self):
        self.negated = not self.negated

    def out(self):
        res = []
        if self.negated:
            res.append('-')
        res.append(self.expr)
        return "".join(res)

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

class ClassDeclaration:
    def __init__(self, abstract, final, name, extends, implements, statements):
        self.abstract = abstract
        self.final = final
        self.name = name
        self.extends = extends
        self.implements = implements
        self.statements = statements

    def out(self):
        res = ['\n']
        if self.abstract:
            res.append('abstract ')
        if self.final:
            res.append('final ')
        res.append('class %s' % self.name)
        if self.extends:
            res.append(' extends %s' % self.extends)
        res.append('\n{\n')
        for statement in self.statements:
            res.append('    %s' % statement.out())
        res.append('}\n')
        return "".join(res)

class ClassVariableList:
    def __init__(self, modifiers, vars):
        self.modifiers = modifiers
        self.vars = vars

    def out(self):
        res = []
        res.append(" ".join(self.modifiers))
        varsout = []
        for var in self.vars:
            varsout.append(var.out())
        res.append("%s;\n" % " ".join(varsout))
        return "".join(res)

class ClassVariable:
    def __init__(self, name, value = None):
        self.name = name
        self.value = value

    def out(self):
        res = ["$%s" % self.name]
        if self.value:
            res.append(" = %s" % self.value.out())
        return "".join(res)

class ClassConstantDeclList:
    def __init__(self, constants):
        self.constants = constants

    def out(self):
        constout = []
        for constant in self.constants:
            constout.append(constant.out())
        return "const %s;\n" % ", ".join(constout)

class ClassConstantDeclaration:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def out(self):
        return "%s = %s" % (self.name, self.value.out())

class MethodDeclaration:
    def __init__(self, modifiers, name, is_reference, params, comment, body):
        self.modifiers = modifiers
        self.name = name
        self.is_reference = is_reference
        self.params = params
        self.comment = comment
        self.body = body

    def out(self):
        res = []
        for modifier in self.modifiers:
            res.append("%s " % modifier)
        if self.is_reference:
            res.append("&")
        res.append("%s(" % self.name)
        res.append(self.params.out(len("".join(res)) + len(strIndent)))
        res.append(")\n%s{\n%s}\n" % (strIndent, strIndent))
        return "".join(res)

def main():
    #parse('main', file('Postgres.php').read())
    ast = parse('file', """<html><head><title><?php
# hash_comment
// slash_comment
statement;

class a { statement; }
final class b { var $f; var $f = 5; var $f=array("foobar"=>array(5,5),"barbaz"=>array(3,3)); statement; }
abstract class c { const a = 4, b = "das ist ein string"; statement; }
class d extends a { statement; statement; }
class e implements i { statement; }
class f extends a implements i { statement; }
class ftest {
    function f() {}
    private function complicatedName($model = array('RecController', 'UsersController'), $flash = 1, $dontUseMe, $pi_TI_link_PiVarsUR_l) {}
}

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
