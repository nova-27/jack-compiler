from jack import CompilationEngine
from jack import JackTokenizer
import sys
import os

if __name__ == '__main__':
    src_files = []

    if len(sys.argv) < 2:
        sys.exit('please specify source(s)')

    if os.path.isfile(sys.argv[1]):
        src_files.append(sys.argv[1])
    elif os.path.isdir(sys.argv[1]):
        for f in os.listdir(sys.argv[1]):
            f_path = os.path.join(sys.argv[1], f)
            if not os.path.isfile(f_path):
                continue
            if not f_path.endswith('.jack'):
                continue
            src_files.append(f_path)
    else:
        sys.exit('file/directory not found')

    for src_file in src_files:
        tokenizer = JackTokenizer(open(src_file, 'r'))

        dst_file = src_file[:src_file.rfind('.')] + '.xml'
        dst = open(dst_file, 'w')

        engine = CompilationEngine(tokenizer, dst)
        engine.compile_class()
