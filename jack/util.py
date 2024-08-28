from typing import TextIO
from xml.sax.saxutils import escape

from jack.tokenizer import JackTokenizer, TokenType


def write_token_and_advance(tokenizer: JackTokenizer, out: TextIO):
    if tokenizer.token_type == TokenType.EOF:
        raise EOFError()

    token_type = tokenizer.token_type.value
    token_value = tokenizer.token_value

    out.write(
        f'<{token_type}> {escape(token_value)} </{token_type}>\n'
    )

    tokenizer.advance()


def check_type(target: TokenType, *expected: TokenType):
    if target not in expected:
        raise SyntaxError(f'expected type: {expected}, but: {target}')


def check_value(target: str, *expected: str):
    if target not in expected:
        raise SyntaxError(f'expected: {expected}, but: {target}')
