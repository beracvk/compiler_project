# src/parser/parser.py

from parser.ast_nodes import (
    ProgramNode, VariableDeclarationNode, AssignmentNode, 
    LiteralNode, BinOpNode, IfNode, WhileNode, PrintNode
)
from parser.semantic import SemanticAnalyzer, SemanticError

class SyntaxErrorCustom(Exception):
    """Sözdizimi hataları için özel istisna sınıfı."""
    pass

class Parser:
    def __init__(self, tokens, symbol_table):
        self.tokens = tokens
        self.current_index = 0
        self.symbol_table = symbol_table
        self.semantic_analyzer = SemanticAnalyzer(symbol_table)

    def current_token(self):
        if self.current_index < len(self.tokens):
            return self.tokens[self.current_index]
        return None

    def match(self, expected_type, expected_value=None):
        token = self.current_token()
        if token is None:
            raise SyntaxErrorCustom(f"Syntax Error: Kodun sonuna gelindi fakat '{expected_type}' bekleniyordu.")
        
        if token['type'] == expected_type:
            if expected_value is not None and token['value'] != expected_value:
                raise SyntaxErrorCustom(f"Syntax Error (Satır {token['line']}): '{expected_value}' bekleniyordu, fakat '{token['value']}' geldi.")
            
            self.current_index += 1
            return token
        else:
            raise SyntaxErrorCustom(f"Syntax Error (Satır {token['line']}): '{expected_type}' bekleniyordu, fakat '{token['type']}' geldi.")

    def parse(self):
        program = ProgramNode()
        while self.current_token() is not None:
            statement = self.parse_statement()
            if statement:
                program.statements.append(statement)
        return program

    def parse_statement(self):
        token = self.current_token()
        if token['type'] == "KEYWORD":
            if token['value'] in ["int", "float"]:
                return self.parse_var_declaration()
            elif token['value'] == "if":
                return self.parse_if_statement()
            elif token['value'] == "while":
                return self.parse_while_statement()
            elif token['value'] == "print":
                return self.parse_print_statement()
            else:
                raise SyntaxErrorCustom(f"Syntax Error (Satır {token['line']}): Geçersiz keyword '{token['value']}'.")
        elif token['type'] == "IDENTIFIER":
            return self.parse_assignment()
        else:
            raise SyntaxErrorCustom(f"Syntax Error (Satır {token['line']}): Geçersiz başlangıç ifadesi '{token['value']}'.")

    def parse_var_declaration(self):
        type_token = self.match("KEYWORD")
        var_token = self.match("IDENTIFIER")
        
        # Sembol tablosuna değişkeni önce kaydediyoruz (böylece atama varsa tip kontrolü yapılabilir)
        self.symbol_table.insert(var_token['value'], type_token['value'], var_token['line'])
        
        init_expr = None
        token = self.current_token()
        if token and token['type'] == "OPERATOR" and token['value'] == "=":
            self.match("OPERATOR", "=")
            init_expr = self.parse_expression()
            
            if isinstance(init_expr, LiteralNode):
                try:
                    self.semantic_analyzer.check_type_mismatch(var_token['value'], init_expr.value_type, var_token['line'])
                except AttributeError:
                    pass
                    
        self.match("DELIMITER", ";")
        return VariableDeclarationNode(type_token['value'], var_token['value'], type_token['line'], init_expr)

    def parse_assignment(self):
        var_token = self.match("IDENTIFIER")
        line = var_token['line']

        self.semantic_analyzer.check_variable_declared(var_token['value'], line)
        self.match("OPERATOR", "=")
        expr_node = self.parse_expression()
        self.match("DELIMITER", ";")

        if isinstance(expr_node, LiteralNode):
            try:
                self.semantic_analyzer.check_type_mismatch(var_token['value'], expr_node.value_type, line)
            except AttributeError:
                pass

        return AssignmentNode(var_token['value'], expr_node, line)

    def parse_expression(self):
        left = self.parse_arithmetic()
        token = self.current_token()
        
        # Karşılaştırma operatörleri desteği
        if token and token['type'] == "OPERATOR" and token['value'] in [">", "<", "==", ">=", "<=", "!="]:
            op_token = self.match("OPERATOR")
            right = self.parse_arithmetic()
            left = BinOpNode(left, op_token['value'], right, op_token['line'])
            
        return left

    def parse_arithmetic(self):
        left = self.parse_term()
        while self.current_token() and self.current_token()['type'] == "OPERATOR" and self.current_token()['value'] in ["+", "-"]:
            op_token = self.match("OPERATOR")
            right = self.parse_term()
            left = BinOpNode(left, op_token['value'], right, op_token['line'])
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current_token() and self.current_token()['type'] == "OPERATOR" and self.current_token()['value'] in ["*", "/"]:
            op_token = self.match("OPERATOR")
            right = self.parse_factor()
            left = BinOpNode(left, op_token['value'], right, op_token['line'])
        return left

    def parse_factor(self):
        token = self.current_token()
        if token['type'] == "LITERAL":
            self.current_index += 1
            v_type = "FLOAT" if "." in str(token['value']) else "INTEGER"
            return LiteralNode(token['value'], v_type, token['line'])
            
        elif token['type'] == "STRING_LITERAL":
            self.current_index += 1
            return LiteralNode(token['value'], "STRING", token['line'])
            
        elif token['type'] == "IDENTIFIER":
            self.current_index += 1
            self.semantic_analyzer.check_variable_declared(token['value'], token['line'])
            var_info = self.symbol_table.lookup(token['value'])
            
            v_type = "FLOAT" if (var_info and var_info.get('type') == "float") else "INTEGER"
            return LiteralNode(token['value'], v_type, token['line'])
        
        else:
            raise SyntaxErrorCustom(f"Syntax Error (Satır {token['line']}): Beklenmeyen ifade '{token['value']}'.")

    # --- YENİ EKLENEN METODLAR (Bloklar, If, While ve Print) ---

    def parse_block(self):
        self.match("DELIMITER", "{")
        statements = []
        while self.current_token() and not (self.current_token()['type'] == "DELIMITER" and self.current_token()['value'] == "}"):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        self.match("DELIMITER", "}")
        return statements

    def parse_if_statement(self):
        if_token = self.match("KEYWORD", "if")
        self.match("DELIMITER", "(")
        condition = self.parse_expression()
        self.match("DELIMITER", ")")
        
        true_block = self.parse_block()
        false_block = None
        
        token = self.current_token()
        if token and token['type'] == "KEYWORD" and token['value'] == "else":
            self.match("KEYWORD", "else")
            false_block = self.parse_block()
            
        return IfNode(condition, true_block, false_block, if_token['line'])

    def parse_while_statement(self):
        while_token = self.match("KEYWORD", "while")
        self.match("DELIMITER", "(")
        condition = self.parse_expression()
        self.match("DELIMITER", ")")
        
        block = self.parse_block()
        return WhileNode(condition, block, while_token['line'])

    def parse_print_statement(self):
        print_token = self.match("KEYWORD", "print")
        self.match("DELIMITER", "(")
        
        value_node = self.parse_expression()
            
        self.match("DELIMITER", ")")
        self.match("DELIMITER", ";")
        
        return PrintNode(value_node, print_token['line'])