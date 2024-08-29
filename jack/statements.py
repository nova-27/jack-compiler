from jack.expression import ExpressionCompiler
from jack.symbol import SymbolTable
from jack.tokenizer import JackTokenizer, TokenType
from jack.util import check_type, check_value
from jack.writer import VMWriter, VMSegment, Operator


class StatementsCompiler:
    def __init__(self, tokenizer: JackTokenizer, writer: VMWriter, symbol_table: SymbolTable):
        self.tokenizer = tokenizer
        self.writer = writer
        self.symbol_table = symbol_table

        self.if_index = 0
        self.while_index = 0

    def compile_statements(self):
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

    def _compile_let_statement(self):
        self.tokenizer.advance()

        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
        seg = VMWriter.skind2seg(self.symbol_table.kind_of(self.tokenizer.token_value))
        index = self.symbol_table.index_of(self.tokenizer.token_value)
        self.tokenizer.advance()

        is_array = False

        if self.tokenizer.token_value == '[':
            self.tokenizer.advance()

            self.writer.write_push(seg, index)
            ExpressionCompiler(self.tokenizer, self.writer, self.symbol_table).compile_expression()
            self.writer.write_arithmetic(Operator.ADD)
            self.writer.write_pop(VMSegment.TEMP, 0)

            check_value(self.tokenizer.token_value, ']')
            self.tokenizer.advance()
            is_array = True

        check_value(self.tokenizer.token_value, '=')
        self.tokenizer.advance()

        ExpressionCompiler(self.tokenizer, self.writer, self.symbol_table).compile_expression()

        check_value(self.tokenizer.token_value, ';')
        self.tokenizer.advance()

        if is_array:
            self.writer.write_push(VMSegment.TEMP, 0)
            self.writer.write_pop(VMSegment.POINTER, 1)
            self.writer.write_pop(VMSegment.THAT, 0)
        else:
            self.writer.write_pop(seg, index)

    def _compile_if_statement(self):
        self.tokenizer.advance()

        check_value(self.tokenizer.token_value, '(')
        self.tokenizer.advance()

        ExpressionCompiler(self.tokenizer, self.writer, self.symbol_table).compile_expression()
        self.writer.write_arithmetic(Operator.NOT)
        self.writer.write_if(f'IF{self.if_index}')

        check_value(self.tokenizer.token_value, ')')
        self.tokenizer.advance()

        check_value(self.tokenizer.token_value, '{')
        self.tokenizer.advance()

        self.compile_statements()

        check_value(self.tokenizer.token_value, '}')
        self.tokenizer.advance()

        if self.tokenizer.token_value == 'else':
            self.tokenizer.advance()

            self.writer.write_goto(f'IF{self.if_index + 1}')
            self.writer.write_label(f'IF{self.if_index}')

            check_value(self.tokenizer.token_value, '{')
            self.tokenizer.advance()

            self.compile_statements()

            check_value(self.tokenizer.token_value, '}')
            self.tokenizer.advance()

            self.writer.write_label(f'IF{self.if_index + 1}')
            self.if_index += 2
        else:
            self.writer.write_label(f'IF{self.if_index}')
            self.if_index += 1

    def _compile_while_statement(self):
        self.tokenizer.advance()

        check_value(self.tokenizer.token_value, '(')
        self.tokenizer.advance()

        self.writer.write_label(f'WHILE{self.while_index + 1}')
        ExpressionCompiler(self.tokenizer, self.writer, self.symbol_table).compile_expression()
        self.writer.write_arithmetic(Operator.NOT)
        self.writer.write_if(f'WHILE{self.while_index}')

        check_value(self.tokenizer.token_value, ')')
        self.tokenizer.advance()

        check_value(self.tokenizer.token_value, '{')
        self.tokenizer.advance()

        self.compile_statements()
        self.writer.write_goto(f'WHILE{self.while_index + 1}')

        check_value(self.tokenizer.token_value, '}')
        self.tokenizer.advance()

        self.writer.write_label(f'WHILE{self.while_index}')
        self.while_index += 2

    def _compile_do_statement(self):
        self.tokenizer.advance()

        ExpressionCompiler(self.tokenizer, self.writer, self.symbol_table).compile_subroutine_call()
        self.writer.write_pop(VMSegment.TEMP, 0)

        check_value(self.tokenizer.token_value, ';')
        self.tokenizer.advance()

    def _compile_return_statement(self):
        self.tokenizer.advance()

        if self.tokenizer.token_value != ';':
            ExpressionCompiler(self.tokenizer, self.writer, self.symbol_table).compile_expression()
        self.writer.write_return()

        check_value(self.tokenizer.token_value, ';')
        self.tokenizer.advance()
