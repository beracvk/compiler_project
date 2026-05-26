Language Grammar (BNF)

Based Structure and Blocks
<program> ::= <statement_list>

<statement_list> ::= <statement> 
                   | <statement> <statement_list>

<statement> ::= <var_declaration> 
              | <assignment> 
              | <if_statement> 
              | <while_statement> 
              | <print_statement>

<block> ::= "{" <statement_list> "}"

Variable Definition and Assignment
<var_declaration> ::= <type> <identifier> ";"
<type> ::= "int" | "float"

<assignment> ::= <identifier> "=" <expression> ";"

Control Structures
<if_statement> ::= "if" "(" <expression> ")" <block> 
                 | "if" "(" <expression> ")" <block> "else" <block>

<while_statement> ::= "while" "(" <expression> ")" <block>

<print_statement> ::= "print" "(" <print_value> ")" ";"
<print_value> ::= <expression> | <string_literal>

Mathematical Expressions and Numbers
<expression> ::= <arithmetic_expr> 
               | <arithmetic_expr> <relational_op> <arithmetic_expr>

<arithmetic_expr> ::= <term> 
                    | <term> <add_op> <arithmetic_expr>

<term> ::= <factor> 
         | <factor> <mult_op> <term>

<factor> ::= <identifier> 
           | <number>

<relational_op> ::= ">" | "<" | "==" | ">=" | "<=" | "!="
<add_op> ::= "+" | "-"
<mult_op> ::= "*" | "/"

<identifier> ::= [a-zA-Z][a-zA-Z0-9_]*
<number> ::= [0-9]+ 
           | [0-9]+ "." [0-9]+
<string_literal> ::= '"' [Herhangi Karakterler] '"'