from typing import TextIO

from jack.tokenizer import JackTokenizer, TokenType
from jack.util import check_type, write_token_and_advance, check_value


class ExpressionCompiler:
    def __init__(self, tokenizer: JackTokenizer, out: TextIO):
        self.tokenizer = tokenizer
        self.out = out

    def compile_expression(self):
        # TODO
        self.out.write('<expression>\n')
        self._compile_term()
        self.out.write('</expression>\n')

    def _compile_term(self):
        # TODO
        self.out.write('<term>\n')
        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER, TokenType.KEYWORD)
        write_token_and_advance(self.tokenizer, self.out)
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
