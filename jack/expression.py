from typing import TextIO

from jack.tokenizer import JackTokenizer, TokenType
from jack.util import check_type, write_token_and_advance, check_value


class ExpressionCompiler:
    def __init__(self, tokenizer: JackTokenizer, out: TextIO):
        self.tokenizer = tokenizer
        self.out = out

    def compile_expression(self):
        self.out.write('<expression>\n')

        self._compile_term()

        while True:
            if self.tokenizer.token_value not in ('+', '-', '*', '/', '&', '|', '<', '>', '='):
                break
            write_token_and_advance(self.tokenizer, self.out)
            self._compile_term()

        self.out.write('</expression>\n')

    def _compile_term(self):
        self.out.write('<term>\n')

        if self.tokenizer.token_type in (TokenType.INT_CONST, TokenType.STRING_CONST):
            write_token_and_advance(self.tokenizer, self.out)
        elif self.tokenizer.token_type == TokenType.KEYWORD:
            check_value(self.tokenizer.token_value, 'true', 'false', 'null', 'this')
            write_token_and_advance(self.tokenizer, self.out)
        elif self.tokenizer.token_type == TokenType.IDENTIFIER:
            next_value = self.tokenizer.look_ahead()[1]

            if next_value == '[':
                write_token_and_advance(self.tokenizer, self.out)
                write_token_and_advance(self.tokenizer, self.out)
                self.compile_expression()
                check_value(self.tokenizer.token_value, ']')
                write_token_and_advance(self.tokenizer, self.out)
            elif next_value in ('(', '.'):
                self.compile_subroutine_call()
            else:
                write_token_and_advance(self.tokenizer, self.out)
        elif self.tokenizer.token_value == '(':
            write_token_and_advance(self.tokenizer, self.out)
            self.compile_expression()
            check_value(self.tokenizer.token_value, ')')
            write_token_and_advance(self.tokenizer, self.out)
        elif self.tokenizer.token_value in ('-', '~'):
            write_token_and_advance(self.tokenizer, self.out)
            self._compile_term()
        else:
            raise SyntaxError(f'unexpected term: {self.tokenizer.token_value}')

        self.out.write('</term>\n')

    def compile_subroutine_call(self):
        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
        write_token_and_advance(self.tokenizer, self.out)

        if self.tokenizer.token_value == '.':
            write_token_and_advance(self.tokenizer, self.out)

            check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
            write_token_and_advance(self.tokenizer, self.out)

        check_value(self.tokenizer.token_value, '(')
        write_token_and_advance(self.tokenizer, self.out)

        self._compile_expression_list()

        check_value(self.tokenizer.token_value, ')')
        write_token_and_advance(self.tokenizer, self.out)

    def _compile_expression_list(self):
        self.out.write('<expressionList>\n')

        if self.tokenizer.token_value != ')':
            self.compile_expression()

            while True:
                if self.tokenizer.token_value != ',':
                    break
                write_token_and_advance(self.tokenizer, self.out)
                self.compile_expression()

        self.out.write('</expressionList>\n')
