"""
parser.py — PLY Parser (YACC) for Mini SQL Compiler
Performs Syntax Analysis: Token Stream → AST (Abstract Syntax Tree)
Uses Context-Free Grammar (CFG) rules with PLY's yacc module.

Syllabus Mapping:
  - Unit 2: Context Free Grammars (CFG)
  - Unit 2: Top Down Parsing / Recursive Descent Parsing
  - Unit 2: Predictive Parsing
  - Unit 2: Bottom Up Parsing — LALR(1) (PLY uses LALR internally)
  - Unit 2: Parser Generator — YACC (PLY yacc module)
  - Unit 2: Syntax Analysis
"""

import ply.yacc as yacc
from lexer import tokens  # Import token list from lexer (required by PLY)
from errors import ErrorCollector


# ============================================================
#  Grammar Rules Trace — Records which production rules are applied
# ============================================================
grammar_trace = []


def reset_trace():
    """Reset the grammar trace for a new parse."""
    global grammar_trace
    grammar_trace = []


def add_trace(rule_name, production):
    """Record a grammar rule application."""
    grammar_trace.append({
        'rule': rule_name,
        'production': production
    })


# ============================================================
#  Error Collector for parser
# ============================================================
parse_errors = ErrorCollector()


def reset_errors():
    """Reset errors for a new parse."""
    global parse_errors
    parse_errors = ErrorCollector()


# ============================================================
#  CFG Grammar Rules — Production Rules
#  Each function defines a grammar rule in BNF format
# ============================================================

# ---- Top-level: query ----

def p_query_select(p):
    '''query : select_stmt'''
    add_trace('query', 'query → select_stmt')
    p[0] = p[1]


def p_query_select_semicolon(p):
    '''query : select_stmt SEMICOLON'''
    add_trace('query', 'query → select_stmt ;')
    p[0] = p[1]


def p_query_insert(p):
    '''query : insert_stmt'''
    add_trace('query', 'query → insert_stmt')
    p[0] = p[1]


def p_query_insert_semicolon(p):
    '''query : insert_stmt SEMICOLON'''
    add_trace('query', 'query → insert_stmt ;')
    p[0] = p[1]


# ---- SELECT statement ----

def p_select_stmt(p):
    '''select_stmt : SELECT columns FROM table_name'''
    add_trace('select_stmt', 'select_stmt → SELECT columns FROM table_name')
    p[0] = {
        'type': 'SELECT',
        'columns': p[2],
        'table': p[4],
        'condition': None
    }


def p_select_stmt_where(p):
    '''select_stmt : SELECT columns FROM table_name WHERE condition'''
    add_trace('select_stmt', 'select_stmt → SELECT columns FROM table_name WHERE condition')
    p[0] = {
        'type': 'SELECT',
        'columns': p[2],
        'table': p[4],
        'condition': p[6]
    }


# ---- Columns ----

def p_columns_star(p):
    '''columns : STAR'''
    add_trace('columns', 'columns → *')
    p[0] = ['*']


def p_columns_list(p):
    '''columns : column_list'''
    add_trace('columns', 'columns → column_list')
    p[0] = p[1]


def p_column_list_single(p):
    '''column_list : IDENTIFIER'''
    add_trace('column_list', 'column_list → IDENTIFIER')
    p[0] = [p[1]]


def p_column_list_multiple(p):
    '''column_list : IDENTIFIER COMMA column_list'''
    add_trace('column_list', 'column_list → IDENTIFIER COMMA column_list')
    p[0] = [p[1]] + p[3]


# ---- Table name ----

def p_table_name(p):
    '''table_name : IDENTIFIER'''
    add_trace('table_name', 'table_name → IDENTIFIER')
    p[0] = p[1]


# ---- WHERE condition ----

def p_condition_expression(p):
    '''condition : expression'''
    add_trace('condition', 'condition → expression')
    p[0] = p[1]


def p_condition_and(p):
    '''condition : expression AND condition'''
    add_trace('condition', 'condition → expression AND condition')
    p[0] = {
        'type': 'AND',
        'left': p[1],
        'right': p[3]
    }


def p_condition_or(p):
    '''condition : expression OR condition'''
    add_trace('condition', 'condition → expression OR condition')
    p[0] = {
        'type': 'OR',
        'left': p[1],
        'right': p[3]
    }


# ---- Comparison expression ----

def p_expression(p):
    '''expression : IDENTIFIER operator value'''
    add_trace('expression', f'expression → IDENTIFIER({p[1]}) operator({p[2]}) value({p[3]})')
    p[0] = {
        'type': 'COMPARISON',
        'left': p[1],
        'operator': p[2],
        'right': p[3]
    }


# ---- Operators ----

def p_operator_gt(p):
    '''operator : GT'''
    add_trace('operator', 'operator → >')
    p[0] = '>'


def p_operator_lt(p):
    '''operator : LT'''
    add_trace('operator', 'operator → <')
    p[0] = '<'


def p_operator_eq(p):
    '''operator : EQ'''
    add_trace('operator', 'operator → =')
    p[0] = '='


def p_operator_gte(p):
    '''operator : GTE'''
    add_trace('operator', 'operator → >=')
    p[0] = '>='


def p_operator_lte(p):
    '''operator : LTE'''
    add_trace('operator', 'operator → <=')
    p[0] = '<='


def p_operator_neq(p):
    '''operator : NEQ'''
    add_trace('operator', 'operator → !=')
    p[0] = '!='


# ---- Values ----

def p_value_number(p):
    '''value : NUMBER'''
    add_trace('value', f'value → NUMBER({p[1]})')
    p[0] = p[1]


def p_value_string(p):
    '''value : STRING'''
    add_trace('value', f'value → STRING({p[1]})')
    p[0] = p[1]


def p_value_identifier(p):
    '''value : IDENTIFIER'''
    add_trace('value', f'value → IDENTIFIER({p[1]})')
    p[0] = p[1]


# ---- INSERT statement ----

def p_insert_stmt(p):
    '''insert_stmt : INSERT INTO IDENTIFIER VALUES LPAREN value_list RPAREN'''
    add_trace('insert_stmt', 'insert_stmt → INSERT INTO IDENTIFIER VALUES ( value_list )')
    p[0] = {
        'type': 'INSERT',
        'table': p[3],
        'values': p[6]
    }


# ---- Value list for INSERT ----

def p_value_list_single(p):
    '''value_list : value'''
    add_trace('value_list', 'value_list → value')
    p[0] = [p[1]]


def p_value_list_multiple(p):
    '''value_list : value COMMA value_list'''
    add_trace('value_list', 'value_list → value COMMA value_list')
    p[0] = [p[1]] + p[3]


# ============================================================
#  Error Handling — Detailed error messages with position
# ============================================================

def p_error(p):
    """Handle syntax errors with detailed messages."""
    global parse_errors
    
    if p:
        # Determine context-specific error
        error_context = _detect_error_context(p)
        
        parse_errors.add_syntax_error(
            message=error_context['message'],
            token_value=str(p.value),
            position=p.lexpos,
            line=p.lineno,
            expected=error_context.get('expected'),
            hint=error_context.get('hint')
        )
    else:
        # Unexpected end of input
        parse_errors.add_syntax_error(
            message="Unexpected end of query — query is incomplete",
            hint="Check that your query has all required parts: SELECT columns FROM table"
        )


def _detect_error_context(p):
    """Detect the specific type of syntax error for better messages."""
    token_type = p.type
    token_value = str(p.value)
    
    if token_type == 'FROM':
        return {
            'message': f"Unexpected '{token_value}' — missing column names after SELECT",
            'expected': "Column names (e.g., name, age) or * for all columns",
            'hint': "SELECT ke baad column names likhein — Example: SELECT name, age FROM students"
        }
    
    elif token_type == 'WHERE':
        return {
            'message': f"Unexpected '{token_value}' — missing table name before WHERE",
            'expected': "Table name (IDENTIFIER) after FROM keyword",
            'hint': "FROM ke baad table ka naam likhein — Example: SELECT name FROM students WHERE ..."
        }
    
    elif token_type == 'IDENTIFIER' and p.lexpos > 0:
        return {
            'message': f"Unexpected identifier '{token_value}'",
            'expected': "Keyword like FROM, WHERE, or a comma between column names",
            'hint': "Check ki FROM keyword likha hai ya column names ke beech comma hai"
        }
    
    elif token_type in ('GT', 'LT', 'EQ', 'GTE', 'LTE', 'NEQ'):
        return {
            'message': f"Unexpected operator '{token_value}'",
            'expected': "Operator should be in WHERE condition: column operator value",
            'hint': "Operators sirf WHERE clause mein use hote hain — Example: WHERE age > 18"
        }
    
    elif token_type == 'COMMA':
        return {
            'message': "Unexpected comma — possible trailing comma in column list",
            'expected': "Column name after comma",
            'hint': "Comma ke baad ek aur column name likhein ya extra comma hatao"
        }
    
    elif token_type == 'SELECT':
        return {
            'message': "Unexpected SELECT keyword",
            'expected': "Only one SELECT statement allowed",
            'hint': "Ek query mein sirf ek SELECT hona chahiye"
        }
    
    else:
        return {
            'message': f"Syntax error at '{token_value}' (type: {token_type})",
            'expected': "Valid SQL syntax",
            'hint': "Check SQL format — Example: SELECT column FROM table WHERE condition"
        }


# ============================================================
#  Build the PLY Parser (suppress warnings for unused tokens)
# ============================================================
import logging
_log = logging.getLogger('ply')
_log.setLevel(logging.ERROR)

parser = yacc.yacc(debug=False, write_tables=True, outputdir='.', errorlog=_log)


# ============================================================
#  Parse Function — Main interface for the compiler
# ============================================================
def parse_query(query):
    """
    Parse a SQL query string.
    
    Args:
        query (str): The SQL query to parse
    
    Returns:
        tuple: (ast, grammar_trace_list, error_collector)
            - ast: Dictionary representing the AST (or None on error)
            - grammar_trace_list: List of applied grammar rules
            - error_collector: ErrorCollector with any parse errors
    """
    # Reset state
    reset_trace()
    reset_errors()
    
    try:
        result = parser.parse(query)
    except Exception as e:
        parse_errors.add_syntax_error(
            message=f"Parser exception: {str(e)}",
            hint="Query mein koi unexpected structure hai — basic SQL format check karein"
        )
        result = None
    
    return result, list(grammar_trace), parse_errors


def get_grammar_rules():
    """
    Get all defined CFG grammar rules for display.
    
    Returns:
        list: List of grammar rule strings in BNF format
    """
    rules = [
        "query        → select_stmt | insert_stmt",
        "select_stmt  → SELECT columns FROM table_name",
        "             | SELECT columns FROM table_name WHERE condition",
        "columns      → * | column_list",
        "column_list  → IDENTIFIER | IDENTIFIER , column_list",
        "table_name   → IDENTIFIER",
        "condition    → expression | expression AND condition | expression OR condition",
        "expression   → IDENTIFIER operator value",
        "operator     → > | < | = | >= | <= | !=",
        "value        → NUMBER | STRING | IDENTIFIER",
        "insert_stmt  → INSERT INTO IDENTIFIER VALUES ( value_list )",
        "value_list   → value | value , value_list",
    ]
    return rules


# ============================================================
#  Module test
# ============================================================
if __name__ == '__main__':
    test_queries = [
        "SELECT name, age FROM students WHERE age > 18",
        "SELECT * FROM courses",
        "INSERT INTO students VALUES (1, 'Rahul', 20)",
        "SELECT FROM students",  # Error case
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("=" * 60)
        
        ast, trace, errors = parse_query(query)
        
        if errors.has_errors():
            print(errors.get_summary())
        else:
            print(f"✅ Valid — AST: {ast}")
            print(f"Grammar trace ({len(trace)} rules):")
            for i, t in enumerate(trace, 1):
                print(f"  {i}. {t['production']}")
