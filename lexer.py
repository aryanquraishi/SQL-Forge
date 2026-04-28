"""
lexer.py — PLY Lexer for Mini SQL Compiler
Performs Lexical Analysis: SQL query → Token Stream
Uses Regular Expressions and PLY's lex module (internally uses DFA/Finite Automata).

Syllabus Mapping:
  - Unit 1: Role of Lexical Analyzer
  - Unit 1: Specification of Tokens
  - Unit 1: Regular Expressions
  - Unit 1: Finite Automata (DFA used internally by PLY)
  - Unit 1: Lex (PLY lex module)
"""

import ply.lex as lex
from errors import ErrorCollector, LexerError


# ============================================================
#  Reserved Words — SQL Keywords
# ============================================================
reserved = {
    'select':   'SELECT',
    'from':     'FROM',
    'where':    'WHERE',
    'insert':   'INSERT',
    'into':     'INTO',
    'values':   'VALUES',
    'and':      'AND',
    'or':       'OR',
    'not':      'NOT',
    'create':   'CREATE',
    'table':    'TABLE',
    'delete':   'DELETE',
    'update':   'UPDATE',
    'set':      'SET',
    'in':       'IN',
    'like':     'LIKE',
    'between':  'BETWEEN',
    'is':       'IS',
    'null':     'NULL',
    'order':    'ORDER',
    'by':       'BY',
    'asc':      'ASC',
    'desc':     'DESC',
    'group':    'GROUP',
    'having':   'HAVING',
    'as':       'AS',
    'join':     'JOIN',
    'on':       'ON',
    'distinct': 'DISTINCT',
}


# ============================================================
#  Token List — All possible token types
# ============================================================
tokens = [
    'IDENTIFIER',
    'NUMBER',
    'STRING',
    'COMMA',
    'SEMICOLON',
    'LPAREN',
    'RPAREN',
    'STAR',
    'DOT',
    'GTE',      # >=
    'LTE',      # <=
    'NEQ',      # !=
    'GT',       # >
    'LT',       # <
    'EQ',       # =
    'PLUS',     # +
    'MINUS',    # -
    'DIVIDE',   # /
] + list(reserved.values())


# ============================================================
#  Regex Patterns — Token Definitions with Regular Expressions
#  These patterns map directly to Unit 1: Regular Expressions
# ============================================================

# Token regex patterns stored for UI display (regex breakdown feature)
TOKEN_PATTERNS = {
    'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*',
    'NUMBER': r'\d+(\.\d+)?',
    'STRING': r"'[^']*'",
    'COMMA': r',',
    'SEMICOLON': r';',
    'LPAREN': r'\(',
    'RPAREN': r'\)',
    'STAR': r'\*',
    'DOT': r'\.',
    'GTE': r'>=',
    'LTE': r'<=',
    'NEQ': r'!=',
    'GT': r'>',
    'LT': r'<',
    'EQ': r'=',
    'PLUS': r'\+',
    'MINUS': r'-',
    'DIVIDE': r'/',
    'KEYWORD': 'Reserved Word Lookup',
}


# ============================================================
#  Multi-character operators — defined as functions for precedence
#  (Functions are matched BEFORE string patterns in PLY)
# ============================================================

def t_GTE(t):
    r'>='
    return t

def t_LTE(t):
    r'<='
    return t

def t_NEQ(t):
    r'!='
    return t


# ============================================================
#  Single-character tokens — defined as strings
# ============================================================
t_GT       = r'>'
t_LT       = r'<'
t_EQ       = r'='
t_COMMA    = r','
t_SEMICOLON = r';'
t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_PLUS     = r'\+'
t_MINUS    = r'-'
t_DIVIDE   = r'/'
t_DOT      = r'\.'


# ============================================================
#  STAR token — separate from multiplication for SQL SELECT *
# ============================================================
def t_STAR(t):
    r'\*'
    return t


# ============================================================
#  STRING token — single-quoted strings like 'hello'
# ============================================================
def t_STRING(t):
    r"'[^']*'"
    return t


# ============================================================
#  NUMBER token — integers and decimals
# ============================================================
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t


# ============================================================
#  IDENTIFIER token — also handles reserved word lookup
#  This is the PLY-recommended approach (Unit 1: Specification of Tokens)
# ============================================================
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Case-insensitive keyword matching
    t.type = reserved.get(t.value.lower(), 'IDENTIFIER')
    return t


# ============================================================
#  Ignored characters and special rules
# ============================================================

# Whitespace — ignored (spaces and tabs)
t_ignore = ' \t'

# Track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# SQL single-line comments
def t_COMMENT(t):
    r'--[^\n]*'
    pass  # Discard comments


# ============================================================
#  Error handling — illegal characters
# ============================================================
def t_error(t):
    # Store error info instead of printing
    if hasattr(t.lexer, 'error_collector'):
        t.lexer.error_collector.add_lexer_error(
            char=t.value[0],
            position=t.lexpos,
            line=t.lineno
        )
    t.lexer.skip(1)


# ============================================================
#  Build the PLY Lexer
# ============================================================
lexer = lex.lex()


# ============================================================
#  Tokenize Function — Main interface for the compiler
# ============================================================
def tokenize(query):
    """
    Tokenize a SQL query string.
    
    Args:
        query (str): The SQL query to tokenize
    
    Returns:
        tuple: (tokens_list, error_collector)
            - tokens_list: List of dicts with {type, value, line, position, regex_pattern, category}
            - error_collector: ErrorCollector with any lexer errors
    """
    error_collector = ErrorCollector()
    lexer.error_collector = error_collector
    
    # Reset lexer state
    lexer.lineno = 1
    lexer.input(query)
    
    tokens_list = []
    
    while True:
        tok = lexer.token()
        if not tok:
            break
        
        # Determine category for UI display
        if tok.type in reserved.values():
            category = 'KEYWORD'
        elif tok.type == 'IDENTIFIER':
            category = 'IDENTIFIER'
        elif tok.type == 'NUMBER':
            category = 'NUMBER'
        elif tok.type == 'STRING':
            category = 'STRING'
        elif tok.type in ('GT', 'LT', 'EQ', 'GTE', 'LTE', 'NEQ'):
            category = 'OPERATOR'
        elif tok.type in ('PLUS', 'MINUS', 'STAR', 'DIVIDE'):
            category = 'ARITHMETIC'
        else:
            category = 'SYMBOL'
        
        # Get the regex pattern used for this token
        if tok.type in reserved.values():
            regex_used = TOKEN_PATTERNS['KEYWORD']
        else:
            regex_used = TOKEN_PATTERNS.get(tok.type, 'N/A')
        
        token_info = {
            'type': tok.type,
            'value': tok.value if not isinstance(tok.value, (int, float)) else tok.value,
            'display_value': str(tok.value),
            'line': tok.lineno,
            'position': tok.lexpos,
            'regex_pattern': regex_used,
            'category': category
        }
        
        tokens_list.append(token_info)
    
    return tokens_list, error_collector


def get_token_patterns():
    """
    Get all token regex patterns for UI display.
    
    Returns:
        dict: Token type → regex pattern mapping
    """
    return TOKEN_PATTERNS.copy()


def get_reserved_words():
    """
    Get all reserved/keyword words.
    
    Returns:
        dict: lowercase word → token type mapping
    """
    return reserved.copy()


# ============================================================
#  Module test
# ============================================================
if __name__ == '__main__':
    test_query = "SELECT name, age FROM students WHERE age > 18"
    print(f"Query: {test_query}")
    print("=" * 60)
    
    tokens_result, errors = tokenize(test_query)
    
    print(f"{'Token':<15} {'Type':<15} {'Category':<12} {'Position':<10} {'Regex Pattern'}")
    print("─" * 80)
    for tok in tokens_result:
        print(f"{str(tok['value']):<15} {tok['type']:<15} {tok['category']:<12} {tok['position']:<10} {tok['regex_pattern']}")
    
    if errors.has_errors():
        print("\nErrors:")
        print(errors.get_summary())
    else:
        print(f"\n✅ Tokenization successful — {len(tokens_result)} tokens found")
