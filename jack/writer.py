from enum import Enum
from typing import TextIO

from jack.symbol import SymbolKind


class VMSegment(Enum):
    CONST = 'constant'
    ARG = 'argument'
    LOCAL = 'local'
    STATIC = 'static'
    THIS = 'this'
    THAT = 'that'
    POINTER = 'pointer'
    TEMP = 'temp'


class Operator(Enum):
    ADD = '+'
    SUB = '-'
    NEG = '-'
    EQ = '='
    GT = '>'
    LT = '<'
    AND = '&'
    OR = '|'
    NOT = '~'


class VMWriter:
    def __init__(self, out: TextIO):
        self.out = out

    def write_function(self, name: str, local_cnt: int):
        self.out.write(f'function {name} {local_cnt}\n')

    def write_call(self, name: str, arg_cnt: int):
        self.out.write(f'call {name} {arg_cnt}\n')

    def write_push(self, segment: VMSegment, index: int):
        self.out.write(f'push {segment.value} {index}\n')

    def write_pop(self, segment: VMSegment, index: int):
        self.out.write(f'pop {segment.value} {index}\n')

    def write_arithmetic(self, command: Operator):
        self.out.write(command.name.lower() + '\n')

    def write_return(self):
        self.out.write('return\n')

    def write_if(self, label: str):
        self.out.write(f'if-goto {label}\n')

    def write_goto(self, label: str):
        self.out.write(f'goto {label}\n')

    def write_label(self, label: str):
        self.out.write(f'label {label}\n')

    @staticmethod
    def skind2seg(skind: SymbolKind):
        if skind == SymbolKind.VAR:
            return VMSegment.LOCAL
        elif skind == SymbolKind.FIELD:
            return VMSegment.THIS
        else:
            return VMSegment(skind)
