# src/parser/parser.py

from parser.ast_nodes import ProgramNode, VariableDeclarationNode, AssignmentNode, LiteralNode, BinOpNode
from parser.semantic import SemanticAnalyzer, SemanticError

class SyntaxErrorCustom(Exception):
    """Sözdizimi hataları için özel istisna sınıfı."""
    pass

class Parser:
    def __init__(self, tokens, symbol_table):
        self.tokens = tokens
        self.current_index = 0
        # Sembol tablosunu hem kendi güncellemelerimiz hem de semantic kontrol için alıyoruz
        self.symbol_table = symbol_table
        self.semantic_analyzer = SemanticAnalyzer(symbol_table)

    def current_token(self):
        """O anda incelenen token'ı döner."""
        if self.current_index < len(self.tokens):
            return self.tokens[self.current_index]
        return None

    def match(self, expected_type, expected_value=None):
        """
        Beklenen token tipi ve (varsa) değeri uyuşuyorsa indeksi 1 artırır ve token'ı döner.
        Uyuşmuyorsa arkadaşının UI'da göstereceği Syntax Error fırlatır.
        """
        token = self.current_token()
        if token is None:
            raise SyntaxErrorCustom(f"Syntax Error: Kodun sonuna gelindi fakat '{expected_type}' bekleniyordu.")
        
        if token['type'] == expected_type:
            if expected_value is not None and token['value'] != expected_value:
                raise SyntaxErrorCustom(f"Syntax Error (Satır {token['line']}): '{expected_value}' bekleniyordu, fakat '{token['value']}' geldi.")
            
            self.current_index += 1 # Sonraki token'a geç
            return token
        else:
            raise SyntaxErrorCustom(f"Syntax Error (Satır {token['line']}): '{expected_type}' bekleniyordu, fakat '{token['type']}' geldi.")

    def parse(self):
        """Parser'ı başlatan ana metod."""
        program = ProgramNode()
        while self.current_token() is not None:
            statement = self.parse_statement()
            if statement:
                program.statements.append(statement)
        return program

    def parse_statement(self):
        """BNF: <statement> ::= <var_declaration> | <assignment>"""
        token = self.current_token()
        if token['type'] == "KEYWORD" and token['value'] in ["int", "float"]:
            return self.parse_var_declaration()
        elif token['type'] == "IDENTIFIER":
            return self.parse_assignment()
        else:
            raise SyntaxErrorCustom(f"Syntax Error (Satır {token['line']}): Geçersiz başlangıç ifadesi '{token['value']}'.")

    def parse_var_declaration(self):
        """BNF: <var_declaration> ::= <KEYWORD> <IDENTIFIER> ";" """
        type_token = self.match("KEYWORD") # 'int' veya 'float'
        var_token = self.match("IDENTIFIER") # 'x', 'y' vb.
        self.match("DELIMITER", ";") # Satır sonu kontrolü

        # 1. Öğrencinin sembol tablosuna değişkeni kaydediyoruz (Hafıza kaydı)
        self.symbol_table.insert(var_token['value'], type_token['value'], var_token['line'])

        return VariableDeclarationNode(type_token['value'], var_token['value'], type_token['line'])

    def parse_assignment(self):
        """BNF: <assignment> ::= <IDENTIFIER> "=" <expression> ";" """
        var_token = self.match("IDENTIFIER")
        line = var_token['line']

        # SEMANTIC KONTROL: Değişken atanmadan önce tanımlanmış mı?
        self.semantic_analyzer.check_variable_declared(var_token['value'], line)

        self.match("OPERATOR", "=")
        
        # Eşittir sağındaki matematiksel ifadeyi veya sayıyı çöz
        expr_node = self.parse_expression()
        
        self.match("DELIMITER", ";")

        # SEMANTIC KONTROL: Tip uyuşmazlığı var mı? (Node tipine bakarak)
        # Eğer düz sayıysa tipi LiteralNode içinden, işlemse işlem sonucundan tahmin edilir
        if isinstance(expr_node, LiteralNode):
            self.semantic_analyzer.check_type_mismatch(var_token['value'], expr_node.value_type, line)

        return AssignmentNode(var_token['value'], expr_node, line)

    def parse_expression(self):
        """BNF: <expression> ::= <term> ( ("+" | "-") <term> )* """
        left = self.parse_term()

        while self.current_token() and self.current_token()['type'] == "OPERATOR" and self.current_token()['value'] in ["+", "-"]:
            op_token = self.current_token()
            self.current_index += 1
            right = self.parse_term()
            left = BinOpNode(left, op_token['value'], right, op_token['line'])
        
        return left

    def parse_term(self):
        """BNF: <term> ::= <factor> ( ("*" | "/") <factor> )* """
        left = self.parse_factor()

        while self.current_token() and self.current_token()['type'] == "OPERATOR" and self.current_token()['value'] in ["*", "/"]:
            op_token = self.current_token()
            self.current_index += 1
            right = self.parse_factor()
            left = BinOpNode(left, op_token['value'], right, op_token['line'])
        
        return left

    def parse_factor(self):
        """BNF: <factor> ::= <LITERAL> | <IDENTIFIER>"""
        token = self.current_token()
        if token['type'] == "LITERAL":
            self.current_index += 1
            # Sayının int mi float mı olduğunu anlamak için nokta kontrolü yapabiliriz
            v_type = "FLOAT" if "." in str(token['value']) else "INTEGER"
            return LiteralNode(token['value'], v_type, token['line'])
        
        elif token['type'] == "IDENTIFIER":
            self.current_index += 1
            # Semantic kontrol: İşlem içinde kullanılan değişken tanımlı mı?
            self.semantic_analyzer.check_variable_declared(token['value'], token['line'])
            
            # Değişkenin tipini sembol tablosundan çekip sanal bir literal gibi üretiyoruz
            var_info = self.symbol_table.lookup(token['value'])
            v_type = "FLOAT" if var_info['type'] == "float" else "INTEGER"
            return LiteralNode(token['value'], v_type, token['line'])
        
        else:
            raise SyntaxErrorCustom(f"Syntax Error (Satır {token['line']}): Sayı veya değişken bekleniyordu, '{token['value']}' geldi.")