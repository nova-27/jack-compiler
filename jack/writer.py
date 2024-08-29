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
        self.out.write(f'function {name} {local_cnt}')

    def write_call(self, name: str, arg_cnt: int):
        self.out.write(f'call {name} {arg_cnt}')

    def write_push(self, segment: VMSegment, index: int):
        self.out.write(f'push {segment.value} {index}')

    def write_pop(self, segment: VMSegment, index: int):
        self.out.write(f'pop {segment.value} {index}')

    def write_arithmetic(self, command: Operator):
        self.out.write(command.name.lower())

    @staticmethod
    def skind2seg(skind: SymbolKind):
        if skind == SymbolKind.VAR:
            return VMSegment.LOCAL
        elif skind == SymbolKind.FIELD:
            return VMSegment.THIS
        else:
            return VMSegment(skind)
