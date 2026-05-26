class Symbol:
    def __init__(self, name, var_type, line, address=None):
        self.name     = name
        self.var_type = var_type
        self.line     = line
        self.address  = address

    def __repr__(self):
        return f"Symbol({self.name}, {self.var_type}, line={self.line}, addr={self.address})"


class SymbolTable:
    def __init__(self):
        self.symbols         = {}
        self.address_counter = 0

    def add(self, name, var_type, line):
        if name in self.symbols:
            return False, f"Line {line}: '{name}' already declared (first at line {self.symbols[name].line})"
        addr = f"0x{self.address_counter:03d}"
        self.address_counter += 4
        self.symbols[name] = Symbol(name, var_type, line, addr)
        return True, None

    def lookup(self, name):
        return self.symbols.get(name, None)

    def all_symbols(self):
        return list(self.symbols.values())