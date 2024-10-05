from enum import Enum
from typing import TextIO

CHUNK_SIZE = 1024
SYMBOL = ('{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~')
KEYWORD = (
    'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
    'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return')
COMMENT = (('//', '\n'), ('/*', '*/'))
TOKEN_SEPARATORS = (' ',) + SYMBOL + tuple(e[0] for e in COMMENT)


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
            self.buffer = self.stream.read(CHUNK_SIZE).lstrip()
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
            self.buffer = self.buffer[1:].lstrip()
            return

        if self.buffer[0] == '"':
            self.token_type = TokenType.STRING_CONST
            self.buffer = self.buffer[1:]
            self.token_value = self._read_until('"')[0]
            return

        (self.token_value, separator) = self._read_until(*TOKEN_SEPARATORS)
        self.buffer = (separator + self.buffer).lstrip()

        if self.token_value in KEYWORD:
            self.token_type = TokenType.KEYWORD
            return

        if self.token_value.isdecimal():
            self.token_type = TokenType.INT_CONST
            return

        self.token_type = TokenType.IDENTIFIER

    def look_ahead(self):
        skipped_type = self.token_type
        skipped_value = self.token_value

        self.advance()
        result = (self.token_type, self.token_value)

        self.buffer = self.token_value + ' ' + self.buffer
        self.token_type = skipped_type
        self.token_value = skipped_value

        return result

    def _read_until(self, *keys: str) -> tuple[str, str]:
        """
        Reads from the buffer until one of the specified keys is found.
        :param keys: the key(s) to search for
        :return: the substring before the found key and the key itself
        """
        key, index = min(((key, self.buffer.find(key)) for key in keys if self.buffer.find(key) != -1),
                         key=lambda x: x[1],
                         default=('', -1))

        if index == -1:
            self.buffer += self.stream.read(CHUNK_SIZE)
            return self._read_until(*keys)

        before_key = self.buffer[:index]
        self.buffer = self.buffer[index + len(key):].lstrip()
        return before_key, key
