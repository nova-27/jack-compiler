from typing import TextIO

from jack.statements import StatementsCompiler
from jack.tokenizer import JackTokenizer, TokenType
from jack.util import check_value, write_token_and_advance, check_type


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer, out: TextIO):
        self.tokenizer = tokenizer
        self.tokenizer.advance()
        self.out = out

    def compile_class(self):
        self.out.write('<class>\n')

        check_value(self.tokenizer.token_value, 'class')
        write_token_and_advance(self.tokenizer, self.out)

        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
        write_token_and_advance(self.tokenizer, self.out)

        check_value(self.tokenizer.token_value, '{')
        write_token_and_advance(self.tokenizer, self.out)

        while True:
            if self.tokenizer.token_value not in ('static', 'field'):
                break
            self._compile_class_var_dec()
        while True:
            if self.tokenizer.token_value not in ('constructor', 'function', 'method'):
                break
            self._compile_subroutine_dec()

        check_value(self.tokenizer.token_value, '}')
        write_token_and_advance(self.tokenizer, self.out)

        self.out.write('</class>\n')

    def _compile_class_var_dec(self):
        self.out.write('<classVarDec>\n')

        write_token_and_advance(self.tokenizer, self.out)

        self._compile_type()

        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
        write_token_and_advance(self.tokenizer, self.out)

        while True:
            if self.tokenizer.token_value != ',':
                break
            write_token_and_advance(self.tokenizer, self.out)

            check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
            write_token_and_advance(self.tokenizer, self.out)

        check_value(self.tokenizer.token_value, ';')
        write_token_and_advance(self.tokenizer, self.out)

        self.out.write('</classVarDec>\n')

    def _compile_type(self):
        check_type(self.tokenizer.token_type, TokenType.KEYWORD, TokenType.IDENTIFIER)

        if self.tokenizer.token_type == TokenType.KEYWORD:
            check_value(self.tokenizer.token_value, 'int', 'char', 'boolean')

        write_token_and_advance(self.tokenizer, self.out)

    def _compile_subroutine_dec(self):
        self.out.write('<subroutineDec>\n')

        write_token_and_advance(self.tokenizer, self.out)

        if self.tokenizer.token_value == 'void':
            write_token_and_advance(self.tokenizer, self.out)
        else:
            self._compile_type()

        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
        write_token_and_advance(self.tokenizer, self.out)

        check_value(self.tokenizer.token_value, '(')
        write_token_and_advance(self.tokenizer, self.out)

        self._compile_parameter_list()

        check_value(self.tokenizer.token_value, ')')
        write_token_and_advance(self.tokenizer, self.out)

        self._compile_subroutine_body()

        self.out.write('</subroutineDec>\n')

    def _compile_parameter_list(self):
        self.out.write('<parameterList>\n')

        if self.tokenizer.token_value != ')':
            self._compile_type()

            check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
            write_token_and_advance(self.tokenizer, self.out)

            while True:
                if self.tokenizer.token_value != ',':
                    break
                write_token_and_advance(self.tokenizer, self.out)

                self._compile_type()

                check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
                write_token_and_advance(self.tokenizer, self.out)

        self.out.write('</parameterList>\n')

    def _compile_subroutine_body(self):
        self.out.write('<subroutineBody>\n')

        check_value(self.tokenizer.token_value, '{')
        write_token_and_advance(self.tokenizer, self.out)

        while True:
            if self.tokenizer.token_value != 'var':
                break
            self._compile_var_dec()

        StatementsCompiler(self.tokenizer, self.out).compile_statements()

        check_value(self.tokenizer.token_value, '}')
        write_token_and_advance(self.tokenizer, self.out)

        self.out.write('</subroutineBody>\n')

    def _compile_var_dec(self):
        self.out.write('<varDec>\n')

        write_token_and_advance(self.tokenizer, self.out)

        self._compile_type()

        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
        write_token_and_advance(self.tokenizer, self.out)

        while True:
            if self.tokenizer.token_value != ',':
                break
            write_token_and_advance(self.tokenizer, self.out)

            check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
            write_token_and_advance(self.tokenizer, self.out)

        check_value(self.tokenizer.token_value, ';')
        write_token_and_advance(self.tokenizer, self.out)

        self.out.write('</varDec>\n')
