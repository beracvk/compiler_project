class TokenType:
    KEYWORD         = "KEYWORD"
    IDENTIFIER      = "IDENTIFIER"
    INTEGER_LITERAL = "INTEGER_LITERAL"
    FLOAT_LITERAL   = "FLOAT_LITERAL"
    STRING_LITERAL  = "STRING_LITERAL"
    OPERATOR        = "OPERATOR"
    DELIMITER       = "DELIMITER"
    UNKNOWN         = "UNKNOWN"
    EOF             = "EOF"

KEYWORDS           = {'int', 'float', 'if', 'else', 'while', 'print'}
SINGLE_OPERATORS   = {'+', '-', '*', '/'}
DOUBLE_OPERATORS   = {'==', '!=', '<=', '>=', '&&', '||'}
AMBIGUOUS_OPERATORS= {'=', '<', '>', '!'}
DELIMITERS         = {';', '(', ')', '{', '}'}


class Token:
    def __init__(self, type, value, line):
        self.type  = type
        self.value = value
        self.line  = line

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line})"


class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.pos    = 0
        self.line   = 1
        self.tokens = []
        self.errors = []

    def current_char(self):
        return self.source[self.pos] if self.pos < len(self.source) else None

    def peek(self):
        return self.source[self.pos + 1] if self.pos + 1 < len(self.source) else None

    def advance(self):
        if self.current_char() == '\n':
            self.line += 1
        self.pos += 1

    def tokenize(self):
        while self.current_char() is not None:
            ch = self.current_char()

            if ch in ' \t\r\n':
                self.advance()

            elif ch == '/' and self.peek() == '/':
                while self.current_char() and self.current_char() != '\n':
                    self.advance()

            elif ch.isdigit():
                self.read_number()

            elif ch.isalpha() or ch == '_':
                self.read_word()

            elif ch == '"':
                self.read_string()

            elif ch in AMBIGUOUS_OPERATORS:
                self.read_ambiguous_operator()

            elif ch in SINGLE_OPERATORS:
                self.tokens.append(Token(TokenType.OPERATOR, ch, self.line))
                self.advance()

            elif ch in DELIMITERS:
                self.tokens.append(Token(TokenType.DELIMITER, ch, self.line))
                self.advance()

            else:
                self.errors.append(f"Line {self.line}: Invalid character '{ch}'")
                self.tokens.append(Token(TokenType.UNKNOWN, ch, self.line))
                self.advance()

        self.tokens.append(Token(TokenType.EOF, "EOF", self.line))
        return self.tokens

    def read_number(self):
        start_line = self.line
        num = ""
        is_float = False

        while self.current_char() and self.current_char().isdigit():
            num += self.current_char()
            self.advance()

        if self.current_char() == '.' and self.peek() and self.peek().isdigit():
            is_float = True
            num += '.'
            self.advance()
            while self.current_char() and self.current_char().isdigit():
                num += self.current_char()
                self.advance()

        ttype = TokenType.FLOAT_LITERAL if is_float else TokenType.INTEGER_LITERAL
        self.tokens.append(Token(ttype, num, start_line))

    def read_word(self):
        start_line = self.line
        word = ""

        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            word += self.current_char()
            self.advance()

        ttype = TokenType.KEYWORD if word in KEYWORDS else TokenType.IDENTIFIER
        self.tokens.append(Token(ttype, word, start_line))

    def read_string(self):
        start_line = self.line
        self.advance()  # opening "
        value = ""

        while self.current_char() and self.current_char() != '"':
            if self.current_char() == '\n':
                self.errors.append(f"Line {start_line}: String not closed before newline")
                break
            value += self.current_char()
            self.advance()

        if self.current_char() == '"':
            self.advance()  # closing "
        else:
            self.errors.append(f"Line {start_line}: Unterminated string literal")

        self.tokens.append(Token(TokenType.STRING_LITERAL, value, start_line))

    def read_ambiguous_operator(self):
        start_line = self.line
        ch = self.current_char()
        two_char = ch + (self.peek() or "")

        if two_char in DOUBLE_OPERATORS:
            self.tokens.append(Token(TokenType.OPERATOR, two_char, start_line))
            self.advance()
            self.advance()
        else:
            self.tokens.append(Token(TokenType.OPERATOR, ch, start_line))
            self.advance()