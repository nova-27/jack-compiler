from typing import TextIO

from jack.statements import StatementsCompiler
from jack.symbol import SymbolTable, SymbolKind
from jack.tokenizer import JackTokenizer, TokenType
from jack.util import check_value, check_type
from jack.writer import VMWriter


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer, out: TextIO):
        self.tokenizer = tokenizer
        self.tokenizer.advance()
        self.out = out
        self.writer = VMWriter(out)
        self.symbol_table = SymbolTable()

    def compile_class(self):
        self.out.write('<class>\n')

        check_value(self.tokenizer.token_value, 'class')
        self.tokenizer.advance()

        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
        self.symbol_table.set_class_name(self.tokenizer.token_value)
        self.tokenizer.advance()

        check_value(self.tokenizer.token_value, '{')
        self.tokenizer.advance()

        while True:
            if self.tokenizer.token_value not in ('static', 'field'):
                break
            self._compile_class_var_dec()
        while True:
            if self.tokenizer.token_value not in ('constructor', 'function', 'method'):
                break
            self._compile_subroutine_dec()

        check_value(self.tokenizer.token_value, '}')
        self.tokenizer.advance()

        self.out.write('</class>\n')

    def _compile_class_var_dec(self):
        self.out.write('<classVarDec>\n')

        skind = SymbolKind(self.tokenizer.token_value)
        self.tokenizer.advance()

        stype = self._compile_type()

        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
        name = self.tokenizer.token_value
        self.tokenizer.advance()

        self.symbol_table.register(name, skind, stype)

        while True:
            if self.tokenizer.token_value != ',':
                break
            self.tokenizer.advance()

            check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
            name = self.tokenizer.token_value
            self.tokenizer.advance()

            self.symbol_table.register(name, skind, stype)

        check_value(self.tokenizer.token_value, ';')
        self.tokenizer.advance()

        self.out.write('</classVarDec>\n')

    def _compile_type(self) -> str:
        check_type(self.tokenizer.token_type, TokenType.KEYWORD, TokenType.IDENTIFIER)

        if self.tokenizer.token_type == TokenType.KEYWORD:
            check_value(self.tokenizer.token_value, 'int', 'char', 'boolean')

        result = self.tokenizer.token_value
        self.tokenizer.advance()

        return result

    def _compile_subroutine_dec(self):
        self.out.write('<subroutineDec>\n')

        self.tokenizer.advance()

        if self.tokenizer.token_value == 'void':
            self.tokenizer.advance()
        else:
            self._compile_type()

        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
        self.symbol_table.start_subroutine(self.tokenizer.token_value)
        self.tokenizer.advance()

        check_value(self.tokenizer.token_value, '(')
        self.tokenizer.advance()

        self._compile_parameter_list()

        check_value(self.tokenizer.token_value, ')')
        self.tokenizer.advance()

        self._compile_subroutine_body()

        self.out.write('</subroutineDec>\n')

    def _compile_parameter_list(self):
        self.out.write('<parameterList>\n')

        if self.tokenizer.token_value != ')':
            stype = self._compile_type()

            check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
            name = self.tokenizer.token_value
            self.tokenizer.advance()

            self.symbol_table.register(name, SymbolKind.ARG, stype)

            while True:
                if self.tokenizer.token_value != ',':
                    break
                self.tokenizer.advance()

                check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
                name = self.tokenizer.token_value
                self.tokenizer.advance()

                self.symbol_table.register(name, SymbolKind.ARG, stype)

        self.out.write('</parameterList>\n')

    def _compile_subroutine_body(self):
        self.out.write('<subroutineBody>\n')

        check_value(self.tokenizer.token_value, '{')
        self.tokenizer.advance()

        while True:
            if self.tokenizer.token_value != 'var':
                break
            self._compile_var_dec()

        self.writer.write_function(self.symbol_table.get_vm_func_name(), self.symbol_table.get_var_cnt(SymbolKind.VAR))

        StatementsCompiler(self.tokenizer, self.out).compile_statements()

        check_value(self.tokenizer.token_value, '}')
        self.tokenizer.advance()

        self.out.write('</subroutineBody>\n')

    def _compile_var_dec(self):
        self.out.write('<varDec>\n')

        self.tokenizer.advance()

        stype = self._compile_type()

        check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
        name = self.tokenizer.token_value
        self.tokenizer.advance()

        self.symbol_table.register(name, SymbolKind.VAR, stype)

        while True:
            if self.tokenizer.token_value != ',':
                break
            self.tokenizer.advance()

            check_type(self.tokenizer.token_type, TokenType.IDENTIFIER)
            name = self.tokenizer.token_value
            self.tokenizer.advance()

            self.symbol_table.register(name, SymbolKind.VAR, stype)

        check_value(self.tokenizer.token_value, ';')
        self.tokenizer.advance()

        self.out.write('</varDec>\n')
