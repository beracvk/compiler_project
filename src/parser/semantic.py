# src/parser/semantic.py

class SemanticError(Exception):
    """Anlam analizi (Semantic) hataları için özel istisna sınıfı."""
    pass

class SemanticAnalyzer:
    def __init__(self, symbol_table):
        """
        Arkadaşının (1. Öğrenci) ürettiği SymbolTable nesnesini alır.
        Sembol tablosunun şu yapıda bir metodu olduğunu varsayıyoruz:
        symbol_table.lookup(var_name) -> Varsa bilgi döner, yoksa None döner.
        """
        self.symbol_table = symbol_table

    def check_variable_declared(self, var_name, line):
        """Bir değişken tanımlanmadan kullanılmaya çalışılıyor mu?"""
        if not self.symbol_table.lookup(var_name):
            raise SemanticError(f"Semantic Error (Satır {line}): '{var_name}' değişkeni tanımlanmadan kullanılmış!")

    def check_type_mismatch(self, var_name, value_type, line):
        """
        Değişkenin tipi ile ona atanmaya çalışılan değerin tipi uyuşuyor mu?
        Örn: int x = 3.14; hatası yakalanır.
        """
        var_info = self.symbol_table.lookup(var_name)
        if var_info:
            expected_type = var_info['type'] # "int" veya "float"
            
            # Tipleri normalize edip karşılaştırıyoruz
            if expected_type == "int" and value_type != "INTEGER":
                raise SemanticError(f"Semantic Error (Satır {line}): 'int' tipindeki '{var_name}' değişkenine float değer atanamaz!")
            if expected_type == "float" and value_type != "FLOAT" and value_type != "INTEGER":
                # Not: Genelde float'a int atanabilir ama katı kural için bunu da engelleyebilirsin.
                raise SemanticError(f"Semantic Error (Satır {line}): 'float' tipindeki '{var_name}' değişkenine geçersiz atama!")