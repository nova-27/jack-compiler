from jack.tokenizer import JackTokenizer, TokenType
from xml.sax.saxutils import escape
import sys

if __name__ == '__main__':
    src = open(sys.argv[1], 'r')
    tokenizer = JackTokenizer(src)

    dst = open('out.xml', 'w')
    dst.write('<tokens>\n')
    while True:
        tokenizer.advance()
        if tokenizer.token_type == TokenType.EOF:
            break
        dst.write(f'<{tokenizer.token_type.value}> {escape(tokenizer.token_value)} </{tokenizer.token_type.value}>\n')
    dst.write('</tokens>')