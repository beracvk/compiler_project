# src/ui/ui.py

import sys
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox

# Add parent directory to sys.path to easily import lexer and parser
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer.lexer import Lexer
from lexer.symbol_table import SymbolTable
from parser.parser import Parser, SyntaxErrorCustom
from parser.semantic import SemanticError
from main import SymbolTableAdapter

class CompilerIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("BERA HATİCE")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)
        
        # Modern Dark Theme Colors
        self.bg_dark = "#1e1e1e"       # Editor background (VS Code style)
        self.bg_sidebar = "#252526"    # Sidebar/Tabs background
        self.bg_status = "#007acc"     # Status bar blue
        self.fg_light = "#d4d4d4"      # Light text
        self.fg_gray = "#858585"       # Muted text
        self.accent_color = "#0e639c"  # Button accent
        self.err_color = "#f44336"     # Error red
        self.succ_color = "#4caf50"    # Success green

        self.setup_styles()
        self.create_widgets()
        self.load_default_code()

    def setup_styles(self):
        # Configure overall ttk styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure frames and panes
        self.style.configure(".", background=self.bg_sidebar, foreground=self.fg_light)
        self.style.configure("TFrame", background=self.bg_sidebar)
        self.style.configure("TPanedwindow", background=self.bg_dark)
        
        # Tab styling (Notebook)
        self.style.configure("TNotebook", background=self.bg_sidebar, borderwidth=0)
        self.style.configure("TNotebook.Tab", 
                             background=self.bg_sidebar, 
                             foreground=self.fg_light, 
                             padding=[12, 6], 
                             font=("Segoe UI", 10))
        self.style.map("TNotebook.Tab",
                       background=[("selected", self.bg_dark)],
                       foreground=[("selected", "#ffffff")])
        
        # Button styling
        self.style.configure("TButton", 
                             background=self.accent_color, 
                             foreground="#ffffff", 
                             font=("Segoe UI", 10, "bold"), 
                             borderwidth=0, 
                             padding=[15, 8])
        self.style.map("TButton",
                       background=[("active", "#1177bb"), ("pressed", "#0b4c78")])
        
        # Treeview (Tables) styling
        self.style.configure("Treeview", 
                             background="#2d2d2d", 
                             fieldbackground="#2d2d2d", 
                             foreground=self.fg_light, 
                             rowheight=25,
                             font=("Consolas", 10))
        self.style.configure("Treeview.Heading", 
                             background=self.bg_sidebar, 
                             foreground=self.fg_light, 
                             font=("Segoe UI", 9, "bold"))
        self.style.map("Treeview", 
                       background=[("selected", self.accent_color)],
                       foreground=[("selected", "#ffffff")])

    def create_widgets(self):
        # --- Top Menu/Toolbar ---
        self.toolbar = tk.Frame(self.root, bg=self.bg_sidebar, height=50)
        self.toolbar.pack(fill=tk.X, side=tk.TOP)
        self.toolbar.pack_propagate(False)

        # Title Label
        title_label = tk.Label(self.toolbar, 
                               text="⚡ bera hatice compiler", 
                               fg="#ffffff", 
                               bg=self.bg_sidebar, 
                               font=("Segoe UI", 12, "bold"))
        title_label.pack(side=tk.LEFT, padx=15)

        # Buttons
        self.btn_compile = ttk.Button(self.toolbar, text="Kodu Derle (Compile)", command=self.compile_code)
        self.btn_compile.pack(side=tk.LEFT, padx=10, pady=6)

        self.btn_clear = ttk.Button(self.toolbar, text="Temizle", command=self.clear_all)
        self.btn_clear.pack(side=tk.LEFT, padx=5, pady=6)
        
        # Quick Load Examples Combobox
        tk.Label(self.toolbar, text="Örnek Yükle:", fg=self.fg_light, bg=self.bg_sidebar, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(30, 5))
        self.example_var = tk.StringVar()
        self.example_combo = ttk.Combobox(self.toolbar, textvariable=self.example_var, values=["Başarılı Senaryo", "Hatalı Senaryo (Semantik/Sözdizimi)", "Lexer Hataları"], state="readonly", width=30)
        self.example_combo.pack(side=tk.LEFT, padx=5, pady=6)
        self.example_combo.bind("<<ComboboxSelected>>", self.on_example_selected)

        # --- Main Layout (Paned Window Split) ---
        self.main_pane = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        # -- Left Side: Editor Area --
        self.editor_frame = tk.Frame(self.main_pane, bg=self.bg_dark)
        self.main_pane.add(self.editor_frame, weight=3)

        # Editor header
        editor_header = tk.Frame(self.editor_frame, bg="#1a1a1a", height=30)
        editor_header.pack(fill=tk.X)
        editor_header.pack_propagate(False)
        tk.Label(editor_header, text="KOD EDİTÖRÜ (C-Like Language)", fg=self.fg_gray, bg="#1a1a1a", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=10)

        # Editor Text and Line Numbers
        self.editor_container = tk.Frame(self.editor_frame, bg=self.bg_dark)
        self.editor_container.pack(fill=tk.BOTH, expand=True)

        # Line numbers sidebar
        self.line_numbers = tk.Text(self.editor_container, width=4, padx=5, takefocus=0, border=0,
                                    background="#1e1e1e", fg=self.fg_gray, state="disabled", 
                                    font=("Consolas", 11), selectbackground="#1e1e1e")
        self.line_numbers.pack(fill=tk.Y, side=tk.LEFT)

        # Code text area
        self.code_text = tk.Text(self.editor_container, wrap=tk.NONE, border=0,
                                 background=self.bg_dark, fg="#d4d4d4",
                                 insertbackground="#ffffff", font=("Consolas", 11),
                                 undo=True, maxundo=100)
        self.code_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Vertical scrollbar
        scrollbar_y = tk.Scrollbar(self.editor_container, command=self.on_scroll_y, bg=self.bg_dark)
        scrollbar_y.pack(fill=tk.Y, side=tk.RIGHT)
        self.code_text.config(yscrollcommand=scrollbar_y.set)
        self.line_numbers.config(yscrollcommand=scrollbar_y.set)

        # Bindings for line numbers and syntax styling
        self.code_text.bind("<KeyRelease>", self.on_key_release)
        self.code_text.bind("<MouseWheel>", self.update_line_numbers)
        self.code_text.bind("<Button-1>", self.update_line_numbers)

        # -- Right Side: Analysis Area (Notebook) --
        self.analysis_frame = tk.Frame(self.main_pane, bg=self.bg_sidebar)
        self.main_pane.add(self.analysis_frame, weight=2)

        self.notebook = ttk.Notebook(self.analysis_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: AST Viewer
        self.ast_tab = tk.Frame(self.notebook, bg=self.bg_dark)
        self.notebook.add(self.ast_tab, text=" AST Görseli ")
        
        self.ast_text = tk.Text(self.ast_tab, wrap=tk.WORD, state="disabled",
                                background="#252526", fg="#9cdcfe", border=0,
                                font=("Consolas", 10))
        self.ast_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 2: Symbol Table
        self.symbol_tab = tk.Frame(self.notebook, bg=self.bg_dark)
        self.notebook.add(self.symbol_tab, text=" Sembol Tablosu ")

        self.sym_tree = ttk.Treeview(self.symbol_tab, columns=("Name", "Type", "Address", "Line"), show="headings")
        self.sym_tree.heading("Name", text="Değişken Adı")
        self.sym_tree.heading("Type", text="Veri Tipi")
        self.sym_tree.heading("Address", text="Bellek Adresi")
        self.sym_tree.heading("Line", text="Tanımlandığı Satır")
        self.sym_tree.column("Name", width=100, anchor=tk.CENTER)
        self.sym_tree.column("Type", width=80, anchor=tk.CENTER)
        self.sym_tree.column("Address", width=100, anchor=tk.CENTER)
        self.sym_tree.column("Line", width=100, anchor=tk.CENTER)
        self.sym_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 3: Lexer Tokens
        self.tokens_tab = tk.Frame(self.notebook, bg=self.bg_dark)
        self.notebook.add(self.tokens_tab, text=" Token Tablosu ")

        self.token_tree = ttk.Treeview(self.tokens_tab, columns=("Line", "Type", "Value"), show="headings")
        self.token_tree.heading("Line", text="Satır No")
        self.token_tree.heading("Type", text="Token Tipi")
        self.token_tree.heading("Value", text="Değeri / Lexeme")
        self.token_tree.column("Line", width=80, anchor=tk.CENTER)
        self.token_tree.column("Type", width=180, anchor=tk.W)
        self.token_tree.column("Value", width=180, anchor=tk.W)
        self.token_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Bottom Pane: Compiler Logs / Console ---
        self.bottom_frame = tk.Frame(self.root, bg="#1a1a1a", height=150)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.bottom_frame.pack_propagate(False)

        console_title = tk.Frame(self.bottom_frame, bg="#252526", height=25)
        console_title.pack(fill=tk.X)
        console_title.pack_propagate(False)
        tk.Label(console_title, text="DERLEYİCİ ÇIKTI KONSOLU", fg=self.fg_gray, bg="#252526", font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT, padx=10)

        self.console_text = tk.Text(self.bottom_frame, background="#111111", fg="#cccccc", border=0,
                                    font=("Consolas", 10), state="disabled", wrap=tk.WORD)
        self.console_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tags for colored console log output
        self.console_text.tag_config("success", foreground=self.succ_color, font=("Consolas", 10, "bold"))
        self.console_text.tag_config("error", foreground=self.err_color, font=("Consolas", 10, "bold"))
        self.console_text.tag_config("info", foreground="#569cd6")
        self.console_text.tag_config("header", foreground="#c586c0", font=("Consolas", 10, "bold"))

        # --- Status Bar ---
        self.status_bar = tk.Frame(self.root, bg=self.bg_status, height=22)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="Hazır", fg="#ffffff", bg=self.bg_status, font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT, padx=10)

    # --- Scrolling & Line Numbers Control ---
    def on_scroll_y(self, *args):
        self.code_text.yview(*args)
        self.line_numbers.yview(*args)
        self.update_line_numbers()

    def on_key_release(self, event=None):
        self.update_line_numbers()
        self.highlight_syntax()

    def update_line_numbers(self, event=None):
        # Calculate line count and update sidebar Text widget
        line_count = int(self.code_text.index('end-1c').split('.')[0])
        line_num_content = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_num_content)
        self.line_numbers.config(state="disabled")
        
        # Match scroll position exactly
        self.line_numbers.yview_moveto(self.code_text.yview()[0])

    # --- Syntax Highlighting for the Code Editor (Modern UI Feel) ---
    def highlight_syntax(self):
        # Clear existing tags
        for tag in ["keyword", "literal", "string", "operator", "comment"]:
            self.code_text.tag_remove(tag, "1.0", tk.END)
            
        self.code_text.tag_config("keyword", foreground="#569cd6", font=("Consolas", 11, "bold"))
        self.code_text.tag_config("literal", foreground="#b5cea8")
        self.code_text.tag_config("string", foreground="#ce9178")
        self.code_text.tag_config("operator", foreground="#d4d4d4")
        self.code_text.tag_config("comment", foreground="#6a9955")

        code = self.code_text.get("1.0", tk.END)
        
        # Simple local regex-free lexical highlighter for instant feedback in editor
        keywords = {"int", "float", "if", "else", "while", "print"}
        
        # Lex and tag simple tokens
        lines = code.split('\n')
        for line_idx, line in enumerate(lines, 1):
            # Comments
            if "//" in line:
                cmt_start = line.find("//")
                self.code_text.tag_add("comment", f"{line_idx}.{cmt_start}", f"{line_idx}.end")
                line = line[:cmt_start] # ignore the commented part for other highlights
                
            words = []
            word = ""
            start_col = 0
            
            # Simple word extraction for basic highlight coloring
            for col_idx, ch in enumerate(line):
                if ch.isalnum() or ch == '_':
                    if not word:
                        start_col = col_idx
                    word += ch
                else:
                    if word:
                        words.append((word, start_col))
                        word = ""
                    # Literals & Strings highlights
                    if ch == '"':
                        # Find matching quote
                        end_quote = line.find('"', col_idx + 1)
                        if end_quote != -1:
                            self.code_text.tag_add("string", f"{line_idx}.{col_idx}", f"{line_idx}.{end_quote + 1}")
            if word:
                words.append((word, start_col))
                
            for w, start in words:
                if w in keywords:
                    self.code_text.tag_add("keyword", f"{line_idx}.{start}", f"{line_idx}.{start + len(w)}")
                elif w.isdigit() or ('.' in w and w.replace('.', '', 1).isdigit()):
                    self.code_text.tag_add("literal", f"{line_idx}.{start}", f"{line_idx}.{start + len(w)}")

    # --- Loading & Managing Example Templates ---
    def load_default_code(self):
        # Starts with successful scenario by default
        self.example_combo.current(0)
        self.on_example_selected()

    def on_example_selected(self, event=None):
        selected = self.example_var.get()
        self.code_text.delete("1.0", tk.END)
        
        if selected == "Başarılı Senaryo":
            code = (
                "int x;\n"
                "int y;\n"
                "float result;\n"
                "x = 10;\n"
                "y = 3;\n"
                "result = x + y * 2;\n"
                "if (result > 15) {\n"
                "    print(\"Result is large\");\n"
                "} else {\n"
                "    print(\"Result is small\");\n"
                "}\n"
                "while (x > 0) {\n"
                "    x = x - 1;\n"
                "}\n"
            )
        elif selected == "Hatalı Senaryo (Semantik/Sözdizimi)":
            code = (
                "int x;\n"
                "int x; // Hata: Değişken tekrar tanımlandı\n"
                "z = 5; // Hata: Tanımsız değişken\n"
                "int y;\n"
                "y = 3.14; // Hata: float'ın int'e atanması\n"
                "if (y > ) { // Hata: Geçersiz sözdizimi\n"
                "    print(\"test\");\n"
                "}\n"
            )
        elif selected == "Lexer Hataları":
            code = (
                "int x = 10 @; // Hata: Geçersiz karakter @\n"
                "float y = 5.5;\n"
                "string s = \"this is an unclosed string; // Hata: Kapatılmamış string\n"
                "float z = # 3.14; // Hata: Geçersiz karakter #\n"
            )
        else:
            code = ""
            
        self.code_text.insert("1.0", code)
        self.on_key_release()

    def clear_all(self):
        self.code_text.delete("1.0", tk.END)
        self.ast_text.config(state="normal")
        self.ast_text.delete("1.0", tk.END)
        self.ast_text.config(state="disabled")
        
        # Clear Treeviews
        for item in self.sym_tree.get_children():
            self.sym_tree.delete(item)
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)
            
        # Clear Console
        self.console_text.config(state="normal")
        self.console_text.delete("1.0", tk.END)
        self.console_text.config(state="disabled")
        
        self.update_line_numbers()
        self.status_label.config(text="Temizlendi", bg=self.bg_status)
        self.status_bar.config(bg=self.bg_status)

    def write_console(self, text, tag="info"):
        self.console_text.config(state="normal")
        self.console_text.insert(tk.END, text + "\n", tag)
        self.console_text.see(tk.END)
        self.console_text.config(state="disabled")

    # --- Core Pipeline Execution (Lexer -> Parser & Semantic Checks) ---
    def compile_code(self):
        # 1. Reset visual outputs
        self.ast_text.config(state="normal")
        self.ast_text.delete("1.0", tk.END)
        self.ast_text.config(state="disabled")
        
        for item in self.sym_tree.get_children():
            self.sym_tree.delete(item)
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)
            
        self.console_text.config(state="normal")
        self.console_text.delete("1.0", tk.END)
        self.console_text.config(state="disabled")

        self.write_console("=================================================================", "header")
        self.write_console(" DERLEME BAŞLATILIYOR... ", "header")
        self.write_console("=================================================================\n", "header")

        source_code = self.code_text.get("1.0", tk.END).strip()
        if not source_code:
            self.write_console("❌ HATA: Derlenecek kod bulunmamaktadır!", "error")
            self.status_label.config(text="Hata: Kod bulunmuyor")
            self.status_bar.config(bg=self.err_color)
            return

        # ------------------ 1. ADIM: LEXICAL ANALİZ (LEXER) ------------------
        self.write_console("[AŞAMA 1] Sözcük Analizi (Lexical Analysis) çalıştırılıyor...")
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()

        # Populate Token Table Visual
        for t in tokens:
            if t.type != "EOF":
                self.token_tree.insert("", tk.END, values=(t.line, t.type, t.value))

        if lexer.errors:
            self.write_console("❌ Sözcük Analiz Hataları Bulundu (Lexical Errors):", "error")
            for err in lexer.errors:
                self.write_console(f"  - {err}", "error")
            self.write_console("\nSözcük analiz hataları nedeniyle derleme işlemi durduruldu.", "error")
            
            self.status_label.config(text="Derleme Durduruldu (Sözcük Analiz Hatası)")
            self.status_bar.config(bg=self.err_color)
            return
        else:
            self.write_console("✅ Sözcük Analizi Başarıyla Tamamlandı!\n", "success")

        # ------------------ 2. ADIM: SENTAKS & SEMANTİK ANALİZ (PARSER) ------------------
        self.write_console("[AŞAMA 2] Sözdizimi & Anlam Analizi (Syntax & Semantic) çalıştırılıyor...")
        
        # Adapt tokens to parser dict format
        adapted_tokens = []
        for t in tokens:
            if t.type == "EOF":
                continue
            
            t_type = t.type
            if t_type in ("INTEGER_LITERAL", "FLOAT_LITERAL"):
                t_type = "LITERAL"
                
            adapted_tokens.append({
                'type': t_type,
                'value': t.value,
                'line': t.line
            })

        raw_symbol_table = SymbolTable()
        symbol_table_adapter = SymbolTableAdapter(raw_symbol_table)
        parser = Parser(adapted_tokens, symbol_table_adapter)

        try:
            ast = parser.parse()
            self.write_console("✅ Sözdizimi & Anlam Analizi Başarıyla Tamamlandı!\n", "success")
            self.write_console("🎉 TEBRİKLER! Derleme Tamamen Başarılı!", "success")
            
            # Populate AST Tab
            self.ast_text.config(state="normal")
            self.ast_text.insert("1.0", json.dumps(ast.to_dict(), indent=2, ensure_ascii=False))
            self.ast_text.config(state="disabled")

            # Populate Symbol Table Visual
            all_syms = raw_symbol_table.all_symbols()
            if all_syms:
                for sym in all_syms:
                    self.sym_tree.insert("", tk.END, values=(sym.name, sym.var_type, sym.address, sym.line))
            
            self.status_label.config(text="Derleme BAŞARILI!")
            self.status_bar.config(bg=self.succ_color)

        except SyntaxErrorCustom as se:
            self.write_console("❌ Sözdizimi Hatası Tespit Edildi (Syntax Error):", "error")
            self.write_console(f"  [SÖZDİZİMİ HATASI] {se}", "error")
            self.status_label.config(text="Derleme Başarısız (Sözdizimi Hatası)")
            self.status_bar.config(bg=self.err_color)
            
        except SemanticError as sme:
            self.write_console("❌ Anlam Bilgisi Hatası Tespit Edildi (Semantic Error):", "error")
            self.write_console(f"  [SEMANTİK HATA] {sme}", "error")
            self.status_label.config(text="Derleme Başarısız (Semantik Hata)")
            self.status_bar.config(bg=self.err_color)
            
        except Exception as ex:
            self.write_console("❌ Beklenmeyen Bir Hata Oluştu:", "error")
            self.write_console(f"  {ex}", "error")
            self.status_label.config(text="Derleme Başarısız (Sistem Hatası)")
            self.status_bar.config(bg=self.err_color)

def main():
    root = tk.Tk()
    app = CompilerIDE(root)
    root.mainloop()

if __name__ == "__main__":
    main()
