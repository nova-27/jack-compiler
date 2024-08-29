from collections import OrderedDict
from enum import Enum


class SymbolKind(Enum):
    STATIC = 'static'
    FIELD = 'field'
    ARG = 'argument'
    VAR = 'var'


class SymbolAttrs:
    def __init__(self, skind: SymbolKind, stype: str):
        self.skind = skind
        self.stype = stype


class SymbolTable:
    def __init__(self):
        self._class_name = ''
        self._class_symbols: OrderedDict[str, SymbolAttrs] = OrderedDict()
        self._subroutine_name = ''
        self._subroutine_symbols: OrderedDict[str, SymbolAttrs] = OrderedDict()

    def set_class_name(self, name: str):
        self._class_name = name

    def start_subroutine(self, name: str):
        self._subroutine_name = name
        self._subroutine_symbols = OrderedDict()

    def get_vm_func_name(self) -> str:
        return f'{self._class_name}.{self._subroutine_name}'

    def register(self, name: str, skind: SymbolKind, stype: str):
        attrs = SymbolAttrs(skind, stype)

        if skind in (SymbolKind.STATIC, SymbolKind.FIELD):
            self._class_symbols[name] = attrs
        else:
            self._subroutine_symbols[name] = attrs

    def get_var_cnt(self, skind: SymbolKind):
        cnt = 0

        if skind == SymbolKind.VAR:
            for attrs in self._subroutine_symbols.values():
                if attrs.skind != skind:
                    continue
                cnt += 1

        return cnt
