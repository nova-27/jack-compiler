from typing import TextIO


class VMWriter:
    def __init__(self, out: TextIO):
        self.out = out

    def write_function(self, name: str, local_cnt: int):
        self.out.write(f'function {name} {local_cnt}')
