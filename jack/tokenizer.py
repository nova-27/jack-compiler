import re
from enum import Enum
from typing import TextIO

CHUNK_SIZE = 1024
SYMBOL = ('{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~')
KEYWORD = ('class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return')
COMMENT = (('//', '\n'), ('/*', '*/'))

class TokenType(Enum):
    INITIAL = 'INITIAL'
    SYMBOL = 'symbol'
    STRING_CONST = 'stringConstant'
    KEYWORD = 'keyword'
    INT_CONST = 'integerConstant'
    IDENTIFIER = 'identifier'
    EOF = 'EOF'

class JackTokenizer:
    def __init__(self, stream: TextIO):
        self.stream = stream
        self.buffer = ''

        self.token_type = TokenType.INITIAL
        self.token_value = ''

    def advance(self):
        if not self.buffer:
            self.buffer = self.stream.read(CHUNK_SIZE).strip()
            if not self.buffer:
                self.token_type = TokenType.EOF
                self.token_value = ''
                return

        # ignore comments
        for c in COMMENT:
            if not self.buffer.startswith(c[0]):
                continue
            self._read_until(c[1])
            return self.advance()

        if self.buffer[0] in SYMBOL:
            self.token_type = TokenType.SYMBOL
            self.token_value = self.buffer[0]
            self.buffer = self.buffer[1:].strip()
            return

        if self.buffer[0] == '"':
            self.token_type = TokenType.STRING_CONST
            self.buffer = self.buffer[1:]
            self.token_value = self._read_until('"')[:-1]
            return

        # find token separator
        pattern = f'[{re.escape("".join(SYMBOL))}\\s]'
        while not (separator_match := re.search(pattern, self.buffer)):
            self.buffer += self.stream.read(CHUNK_SIZE)

        separator_pos = separator_match.start()
        self.token_value = self.buffer[:separator_pos]
        self.buffer = self.buffer[separator_pos:].strip()

        if self.token_value in KEYWORD:
            self.token_type = TokenType.KEYWORD
            return

        if self.token_value.isdecimal():
            self.token_type = TokenType.INT_CONST
            return

        self.token_type = TokenType.IDENTIFIER

    def _read_until(self, end: str):
        while (end_index := self.buffer.find(end)) == -1:
            self.buffer += self.stream.read(CHUNK_SIZE)

        result = self.buffer[:end_index + len(end)]
        self.buffer = self.buffer[end_index + len(end):].strip()
        return result