import os
from lexer.lexer import Lexer

def run_compiler(source_code):
    print("=" * 50)
    print("PASS 1 - LEXER")
    print("=" * 50)

    lexer  = Lexer(source_code)
    tokens = lexer.tokenize()

    print(f"{'Line':<6} {'Type':<22} {'Value'}")
    print("-" * 45)
    for t in tokens:
        if t.type != "EOF":
            print(f"{t.line:<6} {t.type:<22} {t.value}")

    print("\n" + "=" * 50)
    if lexer.errors:
        print("LEXER ERRORS")
        print("=" * 50)
        for err in lexer.errors:
            print(f"  [ERROR] {err}")
    else:
        print("No lexer errors found!")

if __name__ == "__main__":
    # Robust path resolution to handle running from either workspace root or src directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_path = os.path.join(base_dir, "tests", "example_lexer_errors.txt")
    
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            sample = f.read()
        run_compiler(sample)
    except FileNotFoundError:
        print(f"Error: Could not find sample file at {sample_path}")
