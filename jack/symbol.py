from collections import OrderedDict
from enum import Enum


class SymbolKind(Enum):
    STATIC = 'static'
    FIELD = 'field'
    ARG = 'argument'
    VAR = 'var'
    NONE = 'none'


class SubroutineKind(Enum):
    CONSTRUCTOR = 'constructor'
    FUNCTION = 'function'
    METHOD = 'method'


class SymbolAttrs:
    def __init__(self, skind: SymbolKind, stype: str):
        self.skind = skind
        self.stype = stype


class SymbolTable:
    def __init__(self):
        self._class_name = ''
        self._class_symbols: OrderedDict[str, SymbolAttrs] = OrderedDict()
        self._subroutine_kind = SubroutineKind.FUNCTION
        self._subroutine_name = ''
        self._subroutine_symbols: OrderedDict[str, SymbolAttrs] = OrderedDict()
        self.if_index = 0
        self.while_index = 0

    def set_class_name(self, name: str):
        self._class_name = name

    def get_class_name(self) -> str:
        return self._class_name

    def start_subroutine(self, kind: SubroutineKind, name: str):
        self._subroutine_kind = kind
        self._subroutine_name = name
        self._subroutine_symbols = OrderedDict()
        self.if_index = 0
        self.while_index = 0

    def get_vm_func_name(self) -> str:
        return f'{self._class_name}.{self._subroutine_name}'

    def get_subroutine_kind(self) -> SubroutineKind:
        return self._subroutine_kind

    def register(self, name: str, skind: SymbolKind, stype: str):
        attrs = SymbolAttrs(skind, stype)

        if skind in (SymbolKind.STATIC, SymbolKind.FIELD):
            self._class_symbols[name] = attrs
        else:
            self._subroutine_symbols[name] = attrs

    def get_var_cnt(self, skind: SymbolKind) -> int:
        cnt = 0

        if skind == SymbolKind.VAR:
            for attrs in self._subroutine_symbols.values():
                if attrs.skind != skind:
                    continue
                cnt += 1
        elif skind == SymbolKind.FIELD:
            for attrs in self._class_symbols.values():
                if attrs.skind != skind:
                    continue
                cnt += 1

        return cnt

    def kind_of(self, name: str) -> SymbolKind:
        if name in self._subroutine_symbols:
            return self._subroutine_symbols[name].skind
        elif name in self._class_symbols:
            return self._class_symbols[name].skind
        else:
            return SymbolKind.NONE

    def type_of(self, name: str) -> str:
        if name in self._subroutine_symbols:
            return self._subroutine_symbols[name].stype
        elif name in self._class_symbols:
            return self._class_symbols[name].stype
        else:
            return ''

    def index_of(self, name: str) -> int:
        kind = self.kind_of(name)
        cnt = 0

        if name in self._subroutine_symbols:
            for n, a in self._subroutine_symbols.items():
                if a.skind != kind:
                    continue
                if n == name:
                    break
                cnt += 1
        elif name in self._class_symbols:
            for n, a in self._class_symbols.items():
                if a.skind != kind:
                    continue
                if n == name:
                    break
                cnt += 1

        return cnt
