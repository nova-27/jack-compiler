from jack.tokenizer import TokenType


def check_type(target: TokenType, *expected: TokenType):
    if target not in expected:
        raise SyntaxError(f'expected type: {expected}, but: {target}')


def check_value(target: str, *expected: str):
    if target not in expected:
        raise SyntaxError(f'expected: {expected}, but: {target}')
