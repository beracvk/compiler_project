import os
import sys
import json

# Add parent directory of 'lexer' and 'parser' to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lexer.lexer import Lexer
from lexer.symbol_table import SymbolTable
from parser.parser import Parser, SyntaxErrorCustom
from parser.semantic import SemanticError

class SymbolTableAdapter:
    """
    Bridges the Lexer's SymbolTable (written by Student 1) 
    with the Parser's expectation of dict-based symbol lookup (written by Student 2).
    """
    def __init__(self, original_table):
        self.table = original_table

    def insert(self, name, var_type, line):
        # SymbolTable.add returns (success, error_msg)
        success, error_msg = self.table.add(name, var_type, line)
        if not success:
            raise SemanticError(error_msg)

    def lookup(self, name):
        symbol = self.table.lookup(name)
        if symbol is None:
            return None
        # Bridge: student 2's parser expects dict with ['type'] key
        return {
            'type': symbol.var_type,
            'name': symbol.name,
            'line': symbol.line,
            'address': symbol.address
        }

def run_pipeline(file_path):
    file_name = os.path.basename(file_path)
    print("=" * 65)
    print(f" TESTING FILE: {file_name} ".center(65, "="))
    print("=" * 65)
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    print("\n--- [SOURCE CODE] ---")
    for idx, line in enumerate(source_code.splitlines(), 1):
        print(f"{idx:3d} | {line}")
    print("-" * 25)

    # ------------------ 1. LEXER PASS ------------------
    print("\n[PASS 1] Running Lexical Analysis...")
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    if lexer.errors:
        print("❌ Lexical Errors Found:")
        for err in lexer.errors:
            print(f"  - {err}")
        print("Stopping compilation due to lexical errors.")
        return False
    else:
        print("✅ Lexical Analysis Successful!")
        print("\n--- [TOKENS TABLE] ---")
        print(f"{'Line':<6} | {'Token Type':<22} | {'Value'}")
        print("-" * 55)
        for t in tokens:
            if t.type != "EOF":
                print(f"{t.line:<6} | {t.type:<22} | {t.value}")
        print("-" * 55)

    # ------------------ 2. PARSER & SEMANTIC PASS ------------------
    print("\n[PASS 2] Running Syntax & Semantic Analysis...")
    
    # Adapt tokens to the parser's expected dict format
    # Also filter out 'EOF' to prevent parsing loop syntax error
    adapted_tokens = []
    for t in tokens:
        if t.type == "EOF":
            continue
        
        t_type = t.type
        # Parser expects "LITERAL" for float/int literals
        if t_type in ("INTEGER_LITERAL", "FLOAT_LITERAL"):
            t_type = "LITERAL"
            
        adapted_tokens.append({
            'type': t_type,
            'value': t.value,
            'line': t.line
        })

    # Instantiate original Symbol Table and wrap it
    raw_symbol_table = SymbolTable()
    symbol_table_adapter = SymbolTableAdapter(raw_symbol_table)

    parser = Parser(adapted_tokens, symbol_table_adapter)

    try:
        ast = parser.parse()
        print("✅ Syntax & Semantic Analysis Successful!")
        
        print("\n--- [ABSTRACT SYNTAX TREE (AST)] ---")
        print(json.dumps(ast.to_dict(), indent=2, ensure_ascii=False))
        print("-" * 45)

        print("\n--- [SYMBOL TABLE (MEMORY ALLOCATION)] ---")
        all_syms = raw_symbol_table.all_symbols()
        if all_syms:
            print(f"{'Name':<10} | {'Type':<8} | {'Address':<8} | {'LineDeclared':<12}")
            print("-" * 45)
            for sym in all_syms:
                print(f"{sym.name:<10} | {sym.var_type:<8} | {sym.address:<8} | {sym.line:<12}")
        else:
            print("No symbols declared.")
        print("-" * 45)
        return True

    except SyntaxErrorCustom as se:
        print(f"❌ Syntax Error Detected:")
        print(f"  [SYNTAX ERROR] {se}")
        return False
    except SemanticError as sme:
        print(f"❌ Semantic Error Detected:")
        print(f"  [SEMANTIC ERROR] {sme}")
        return False
    except Exception as ex:
        print(f"❌ Unexpected Error During Parsing:")
        print(f"  {ex}")
        import traceback
        traceback.print_exc()
        return False

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tests_dir = os.path.join(base_dir, "tests")
    
    test_files = [
        "example_lexer_errors.txt",
        "example_unsuccesful.txt",
        "example_succesful.txt"
    ]
    
    results = {}
    
    for tf in test_files:
        file_path = os.path.join(tests_dir, tf)
        if os.path.exists(file_path):
            success = run_pipeline(file_path)
            results[tf] = "SUCCESS" if success else "FAILED"
            print("\n" + "=" * 65 + "\n")
        else:
            print(f"Warning: Test file {tf} not found at {file_path}")
            
    print("=" * 65)
    print(" SUMMARY OF COMPILATION RUNS ".center(65, "="))
    print("=" * 65)
    for tf, status in results.items():
        icon = "🟢" if status == "SUCCESS" else "🔴"
        print(f" {icon} {tf:<30} : {status}")
    print("=" * 65)

if __name__ == "__main__":
    main()
