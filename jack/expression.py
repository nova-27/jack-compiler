from typing import TextIO

from jack.symbol import SymbolTable, SymbolKind
from jack.tokenizer import JackTokenizer, TokenType
from jack.util import check_type, check_value
from jack.writer import VMWriter, VMSegment, Operator


class ExpressionCompiler:
    def __init__(self, tokenizer: JackTokenizer, out: TextIO, writer: VMWriter, symbol_table: SymbolTable):
        self.tokenizer = tokenizer
        self.out = out
        self.writer = writer
        self.symbol_table = symbol_table

    def compile_expression(self):
        self.out.write('<expression>\n')

        self._compile_term()

        while True:
            if self.tokenizer.token_value not in ('+', '-', '*', '/', '&', '|', '<', '>', '='):
                break
            op = self.tokenizer.token_value
            self.tokenizer.advance()
            self._compile_term()

            if op == '*':
                self.writer.write_call('Math.multiply', 2)
            elif op == '/':
                self.writer.write_call('Math.divide', 2)
            else:
                self.writer.write_arithmetic(Operator(op))

        self.out.write('</expression>\n')

    def _compile_term(self):
        self.out.write('<term>\n')

        if self.tokenizer.token_type == TokenType.INT_CONST:
            self.writer.write_push(VMSegment.CONST, int(self.tokenizer.token_value))
            self.tokenizer.advance()
        elif self.tokenizer.token_type == TokenType.STRING_CONST:
            text = self.tokenizer.token_value
            self.writer.write_push(VMSegment.CONST, len(text))
            self.writer.write_call('String.new', 1)
            for c in text:
                self.writer.write_push(VMSegment.CONST, ord(c))
                self.writer.write_call('String.appendChar', 2)
            self.tokenizer.advance()
        elif self.tokenizer.token_type == TokenType.KEYWORD:
            check_value(self.tokenizer.token_value, 'true', 'false', 'null', 'this')
            if self.tokenizer.token_value == 'this':
                self.writer.write_push(VMSegment.POINTER, 0)
            else:
                self.writer.write_push(VMSegment.CONST, 0)
                if self.tokenizer.token_value == 'true':
                    self.writer.write_arithmetic(Operator.NEG)
            self.tokenizer.advance()
        elif self.tokenizer.token_type == TokenType.IDENTIFIER:
            next_value = self.tokenizer.look_ahead()[1]

            if next_value == '[':
                # varName [ expression ]
                self.writer.write_push(
                    VMWriter.skind2seg(self.symbol_table.kind_of(self.tokenizer.token_value)),
                    self.symbol_table.index_of(self.tokenizer.token_value)
                )
                self.tokenizer.advance()
                self.tokenizer.advance()

                self.compile_expression()

                self.writer.write_arithmetic(Operator.ADD)
                self.writer.write_pop(VMSegment.POINTER, 1)
                self.writer.write_push(VMSegment.THAT, 0)

                check_value(self.tokenizer.token_value, ']')
                self.tokenizer.advance()
            elif next_value in ('(', '.'):
                # subroutineCall
                self.compile_subroutine_call()
            else:
                # varName
                self.writer.write_push(
                    VMWriter.skind2seg(self.symbol_table.kind_of(self.tokenizer.token_value)),
                    self.symbol_table.index_of(self.tokenizer.token_value)
                )
                self.tokenizer.advance()
        elif self.tokenizer.token_value == '(':
            self.tokenizer.advance()
            self.compile_expression()
            check_value(self.tokenizer.token_value, ')')
            self.tokenizer.advance()
        elif self.tokenizer.token_value in ('-', '~'):
            op = self.tokenizer.token_value
            self.tokenizer.advance()
            self._compile_term()
            self.writer.write_arithmetic(Operator(op))
        else:
            raise SyntaxError(f'unexpected term: {self.tokenizer.token_value}')

        self.out.write('</term>\n')

    def compile_subroutine_call(self):
        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
        class_name = self.tokenizer.token_value
        subroutine_name = self.tokenizer.token_value
        arg_cnt = 0
        self.tokenizer.advance()

        if self.tokenizer.token_value == '.':
            # (className | varName).subroutineName(expressionList)
            self.tokenizer.advance()

            if self.symbol_table.kind_of(class_name) != SymbolKind.NONE:
                # varName.subroutineName(expressionList)
                self.writer.write_push(
                    VMWriter.skind2seg(self.symbol_table.kind_of(class_name)),
                    self.symbol_table.index_of(class_name)
                )

                class_name = self.symbol_table.type_of(class_name)
                arg_cnt += 1

            check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
            subroutine_name = self.tokenizer.token_value
            self.tokenizer.advance()
        else:
            # subroutineName(expressionList)
            class_name = self.symbol_table.get_class_name()
            self.writer.write_push(VMSegment.POINTER, 0)
            arg_cnt += 1

        check_value(self.tokenizer.token_value, '(')
        self.tokenizer.advance()

        arg_cnt += self._compile_expression_list()

        check_value(self.tokenizer.token_value, ')')
        self.tokenizer.advance()

        self.writer.write_call(f'{class_name}.{subroutine_name}', arg_cnt)

    def _compile_expression_list(self) -> int:
        self.out.write('<expressionList>\n')
        exp_cnt = 0

        if self.tokenizer.token_value != ')':
            self.compile_expression()
            exp_cnt += 1

            while True:
                if self.tokenizer.token_value != ',':
                    break
                self.tokenizer.advance()
                self.compile_expression()
                exp_cnt += 1

        self.out.write('</expressionList>\n')
        return exp_cnt
