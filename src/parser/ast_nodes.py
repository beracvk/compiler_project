# src/parser/ast_nodes.py

class ASTNode:
    """Tüm AST düğümleri için temel taban sınıf."""
    def to_dict(self):
        """Ağaç yapısını UI veya terminalde kolayca göstermek için sözlüğe çevirir."""
        raise NotImplementedError

class ProgramNode(ASTNode):
    """Kod dosyasının tamamını (satır satır tüm ifadeleri) temsil eder."""
    def __init__(self):
        self.statements = []  # İçinde birden fazla satır/ifade barındırır

    def to_dict(self):
        return {"Node": "Program", "Statements": [s.to_dict() for s in self.statements]}

class VariableDeclarationNode(ASTNode):
    """int x; veya float y; gibi tanımlamaları temsil eder."""
    def __init__(self, datatype, var_name, line):
        self.datatype = datatype  # "int" veya "float"
        self.var_name = var_name  # "x", "sayi" vb.
        self.line = line

    def to_dict(self):
        return {"Node": "VariableDeclaration", "Type": self.datatype, "Name": self.var_name, "Line": self.line}

class AssignmentNode(ASTNode):
    """x = 5; veya y = 3.14; gibi değer atamalarını temsil eder."""
    def __init__(self, var_name, value_node, line):
        self.var_name = var_name
        self.value_node = value_node  # Bir LiteralNode veya BinOpNode olabilir
        self.line = line

    def to_dict(self):
        return {"Node": "Assignment", "Variable": self.var_name, "Value": self.value_node.to_dict(), "Line": self.line}

class LiteralNode(ASTNode):
    """5, 10, 3.14 veya "merhaba" gibi doğrudan ham değerleri temsil eder."""
    def __init__(self, value, value_type, line):
        self.value = value        # Örn: 5 veya "test"
        self.value_type = value_type  # "INTEGER", "FLOAT" veya "STRING"
        self.line = line

    def to_dict(self):
        return {"Node": "Literal", "Value": self.value, "Type": self.value_type, "Line": self.line}

class BinOpNode(ASTNode):
    """x + 5, a * b veya x > 10 gibi ikili işlemleri temsil eder."""
    def __init__(self, left, operator, right, line):
        self.left = left          # Sol taraf (Node)
        self.operator = operator  # "+", "-", "*", "/", ">", "==" vb.
        self.right = right        # Sağ taraf (Node)
        self.line = line

    def to_dict(self):
        return {
            "Node": "BinaryOperation",
            "Left": self.left.to_dict(),
            "Operator": self.operator,
            "Right": self.right.to_dict(),
            "Line": self.line
        }
    
class IfNode(ASTNode):
    """if (x > 5) { ... } else { ... } yapılarını temsil eder."""
    def __init__(self, condition, true_block, false_block, line):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block
        self.line = line

    def to_dict(self):
        return {
            "Node": "IfStatement",
            "Condition": self.condition.to_dict(),
            "TrueBlock": [stmt.to_dict() for stmt in self.true_block],
            # Eğer else bloğu yoksa None döner, varsa listeyi çevirir
            "FalseBlock": [stmt.to_dict() for stmt in self.false_block] if self.false_block else None,
            "Line": self.line
        }

class WhileNode(ASTNode):
    """while (x > 0) { ... } döngülerini temsil eder."""
    def __init__(self, condition, block, line):
        self.condition = condition
        self.block = block
        self.line = line

    def to_dict(self):
        return {
            "Node": "WhileStatement",
            "Condition": self.condition.to_dict(),
            "Block": [stmt.to_dict() for stmt in self.block],
            "Line": self.line
        }

class PrintNode(ASTNode):
    """print("mesaj"); veya print(x); fonksiyonlarını temsil eder."""
    def __init__(self, value_node, line):
        self.value_node = value_node
        self.line = line

    def to_dict(self):
        return {
            "Node": "PrintStatement",
            "Value": self.value_node.to_dict(),
            "Line": self.line
        }