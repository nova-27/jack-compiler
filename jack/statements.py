from typing import TextIO

from jack.expression import ExpressionCompiler
from jack.tokenizer import JackTokenizer, TokenType
from jack.util import write_token_and_advance, check_type, check_value


class StatementsCompiler:
    def __init__(self, tokenizer: JackTokenizer, out: TextIO):
        self.tokenizer = tokenizer
        self.out = out

    def compile_statements(self):
        self.out.write('<statements>\n')

        while True:
            if self.tokenizer.token_value == 'let':
                self._compile_let_statement()
            elif self.tokenizer.token_value == 'if':
                self._compile_if_statement()
            elif self.tokenizer.token_value == 'while':
                self._compile_while_statement()
            elif self.tokenizer.token_value == 'do':
                self._compile_do_statement()
            elif self.tokenizer.token_value == 'return':
                self._compile_return_statement()
            else:
                break

        self.out.write('</statements>\n')

    def _compile_let_statement(self):
        self.out.write('<letStatement>\n')

        write_token_and_advance(self.tokenizer, self.out)

        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
        write_token_and_advance(self.tokenizer, self.out)

        if self.tokenizer.token_value == '[':
            write_token_and_advance(self.tokenizer, self.out)

            ExpressionCompiler(self.tokenizer, self.out).compile_expression()

            check_value(self.tokenizer.token_value, ']')
            write_token_and_advance(self.tokenizer, self.out)

        check_value(self.tokenizer.token_value, '=')
        write_token_and_advance(self.tokenizer, self.out)

        ExpressionCompiler(self.tokenizer, self.out).compile_expression()

        check_value(self.tokenizer.token_value, ';')
        write_token_and_advance(self.tokenizer, self.out)

        self.out.write('</letStatement>\n')

    def _compile_if_statement(self):
        self.out.write('<ifStatement>\n')

        write_token_and_advance(self.tokenizer, self.out)

        check_value(self.tokenizer.token_value, '(')
        write_token_and_advance(self.tokenizer, self.out)

        ExpressionCompiler(self.tokenizer, self.out).compile_expression()

        check_value(self.tokenizer.token_value, ')')
        write_token_and_advance(self.tokenizer, self.out)

        check_value(self.tokenizer.token_value, '{')
        write_token_and_advance(self.tokenizer, self.out)

        self.compile_statements()

        check_value(self.tokenizer.token_value, '}')
        write_token_and_advance(self.tokenizer, self.out)

        if self.tokenizer.token_value == 'else':
            write_token_and_advance(self.tokenizer, self.out)

            check_value(self.tokenizer.token_value, '{')
            write_token_and_advance(self.tokenizer, self.out)

            self.compile_statements()

            check_value(self.tokenizer.token_value, '}')
            write_token_and_advance(self.tokenizer, self.out)

        self.out.write('</ifStatement>\n')

    def _compile_while_statement(self):
        self.out.write('<whileStatement>\n')

        write_token_and_advance(self.tokenizer, self.out)

        check_value(self.tokenizer.token_value, '(')
        write_token_and_advance(self.tokenizer, self.out)

        ExpressionCompiler(self.tokenizer, self.out).compile_expression()

        check_value(self.tokenizer.token_value, ')')
        write_token_and_advance(self.tokenizer, self.out)

        check_value(self.tokenizer.token_value, '{')
        write_token_and_advance(self.tokenizer, self.out)

        self.compile_statements()

        check_value(self.tokenizer.token_value, '}')
        write_token_and_advance(self.tokenizer, self.out)

        self.out.write('</whileStatement>\n')

    def _compile_do_statement(self):
        self.out.write('<doStatement>\n')

        write_token_and_advance(self.tokenizer, self.out)

        ExpressionCompiler(self.tokenizer, self.out).compile_subroutine_call()

        check_value(self.tokenizer.token_value, ';')
        write_token_and_advance(self.tokenizer, self.out)

        self.out.write('</doStatement>\n')

    def _compile_return_statement(self):
        self.out.write('<returnStatement>\n')

        write_token_and_advance(self.tokenizer, self.out)

        if self.tokenizer.token_value != ';':
            ExpressionCompiler(self.tokenizer, self.out).compile_expression()

        check_value(self.tokenizer.token_value, ';')
        write_token_and_advance(self.tokenizer, self.out)

        self.out.write('</returnStatement>\n')
