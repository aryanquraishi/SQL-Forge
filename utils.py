"""
utils.py — Utility Functions for Mini SQL Compiler
Query formatter, syntax highlighter, and export report generator.
"""

import re
from datetime import datetime


# ============================================================
#  Syntax Highlighter — Color-coded HTML output
# ============================================================

# Color scheme for token categories
TOKEN_COLORS = {
    'KEYWORD': '#C084FC',      # Purple
    'IDENTIFIER': '#60A5FA',   # Blue
    'OPERATOR': '#FB923C',     # Orange
    'NUMBER': '#4ADE80',       # Green
    'STRING': '#FACC15',       # Yellow
    'SYMBOL': '#94A3B8',       # Gray
    'ARITHMETIC': '#FB923C',   # Orange
}


def highlight_query(tokens):
    """
    Generate syntax-highlighted HTML from token list.
    
    Args:
        tokens (list): List of token dicts from lexer
    
    Returns:
        str: HTML string with colored spans
    """
    if not tokens:
        return ""
    
    parts = []
    last_end = 0
    
    # Sort tokens by position to handle spacing
    sorted_tokens = sorted(tokens, key=lambda t: t.get('position', 0))
    
    for tok in sorted_tokens:
        pos = tok.get('position', 0)
        value = tok.get('display_value', str(tok.get('value', '')))
        category = tok.get('category', 'SYMBOL')
        color = TOKEN_COLORS.get(category, '#94A3B8')
        
        # Add whitespace between tokens
        if pos > last_end:
            spaces = pos - last_end
            parts.append(' ' * spaces)
        
        # Add colored token
        parts.append(f'<span style="color:{color};font-weight:{"bold" if category == "KEYWORD" else "normal"}">{value}</span>')
        last_end = pos + len(value)
    
    html = ''.join(parts)
    return f'<code style="font-family:\'JetBrains Mono\',\'Fira Code\',monospace;font-size:1.1em;letter-spacing:0.5px;">{html}</code>'


# ============================================================
#  Query Formatter — Clean SQL formatting
# ============================================================

def format_query(query):
    """
    Format a messy SQL query into clean, readable format.
    
    Args:
        query (str): Raw SQL query
    
    Returns:
        str: Formatted SQL query
    """
    # Normalize whitespace
    query = re.sub(r'\s+', ' ', query.strip())
    
    # Uppercase keywords
    keywords = ['SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES',
                'AND', 'OR', 'NOT', 'ORDER', 'BY', 'GROUP', 'HAVING',
                'JOIN', 'ON', 'AS', 'DISTINCT', 'SET', 'UPDATE', 'DELETE',
                'CREATE', 'TABLE', 'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL',
                'ASC', 'DESC']
    
    for kw in keywords:
        pattern = re.compile(r'\b' + kw + r'\b', re.IGNORECASE)
        query = pattern.sub(kw, query)
    
    # Add newlines before major keywords
    for kw in ['FROM', 'WHERE', 'AND', 'OR', 'ORDER BY', 'GROUP BY', 'HAVING', 'VALUES']:
        query = re.sub(r'\s+' + kw + r'\b', '\n' + kw, query)
    
    # Add spaces around operators
    query = re.sub(r'\s*([><=!]+)\s*', r' \1 ', query)
    
    # Add space after commas
    query = re.sub(r',\s*', ', ', query)
    
    # Add semicolon if missing
    if not query.rstrip().endswith(';'):
        query = query.rstrip() + ';'
    
    return query


# ============================================================
#  Export Report Generator
# ============================================================

def generate_report(result):
    """
    Generate a downloadable text report of compilation results.
    
    Args:
        result: CompileResult object
    
    Returns:
        str: Formatted report text
    """
    lines = []
    sep = "═" * 65
    thin_sep = "─" * 65
    
    lines.append(sep)
    lines.append("   MINI SQL COMPILER — COMPILATION REPORT")
    lines.append(sep)
    lines.append(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"   Query: {result.query}")
    lines.append(f"   Status: {'VALID' if result.is_valid else 'INVALID'}")
    lines.append(f"   Compile Time: {result.compile_time_ms:.2f} ms")
    lines.append(sep)
    
    # 1. Lexical Analysis
    lines.append("\n1. LEXICAL ANALYSIS")
    lines.append(thin_sep)
    lines.append(f"   {'Token':<20} {'Type':<15} {'Category':<12} {'Position'}")
    lines.append("   " + "─" * 55)
    for tok in result.tokens:
        lines.append(f"   {str(tok['value']):<20} {tok['type']:<15} {tok['category']:<12} {tok['position']}")
    lines.append(f"\n   Total Tokens: {len(result.tokens)}")
    
    # 2. Token Statistics
    lines.append("\n2. TOKEN STATISTICS")
    lines.append(thin_sep)
    for cat, count in result.token_stats.items():
        lines.append(f"   {cat:<15} : {count}")
    
    # 3. Symbol Table
    if result.symbol_table_data:
        lines.append("\n3. SYMBOL TABLE")
        lines.append(thin_sep)
        lines.append(f"   {'Name':<15} {'Category':<18} {'Freq':<8} {'Contexts'}")
        lines.append("   " + "─" * 50)
        for entry in result.symbol_table_data:
            ctx = ", ".join(entry.get('contexts', []))
            lines.append(f"   {entry['name']:<15} {entry['category']:<18} {entry['frequency']:<8} {ctx}")
    
    # 4. Syntax Analysis
    lines.append("\n4. SYNTAX ANALYSIS")
    lines.append(thin_sep)
    lines.append(f"   {result.syntax_message}")
    
    if result.is_valid and result.grammar_trace:
        lines.append("\n   Grammar Rules Applied:")
        for i, t in enumerate(result.grammar_trace, 1):
            lines.append(f"   {i:>3}. {t['production']}")
    
    # 5. Errors (if any)
    if result.errors:
        lines.append("\n   ERRORS:")
        for err in result.errors:
            lines.append(f"   ❌ {err['message']}")
            if err.get('hint'):
                lines.append(f"      Hint: {err['hint']}")
    
    if result.is_valid:
        # 6. Parse Tree
        lines.append("\n5. PARSE TREE")
        lines.append(thin_sep)
        for line in result.parse_tree_str.split('\n'):
            lines.append(f"   {line}")
        lines.append(f"\n   Depth: {result.tree_depth} | Nodes: {result.tree_node_count}")
        
        # 7. Postfix
        if result.postfix:
            lines.append("\n6. POSTFIX NOTATION")
            lines.append(thin_sep)
            lines.append(f"   {result.postfix}")
        
        # 8. TAC
        if result.tac_string:
            lines.append("\n7. THREE ADDRESS CODE")
            lines.append(thin_sep)
            lines.append(result.tac_string)
        
        # 9. Quadruples
        if result.quadruples:
            lines.append("\n8. QUADRUPLES")
            lines.append(thin_sep)
            lines.append(f"   {'#':<4} {'Operator':<12} {'Arg1':<15} {'Arg2':<15} {'Result'}")
            lines.append("   " + "─" * 50)
            for q in result.quadruples:
                lines.append(f"   {q['index']:<4} {q['operator']:<12} {str(q['arg1']):<15} {str(q['arg2']):<15} {q['result']}")
    
    # Footer
    lines.append("\n" + sep)
    lines.append("   Generated by Mini SQL Compiler")
    lines.append("   M.Sc. Compiler Design Project")
    lines.append(sep)
    
    return "\n".join(lines)


# ============================================================
#  Sample Queries
# ============================================================

SAMPLE_QUERIES = [
    {"label": "✅ Basic SELECT", "query": "SELECT name FROM students"},
    {"label": "✅ Multiple Columns", "query": "SELECT name, age, grade FROM students"},
    {"label": "✅ WHERE Condition", "query": "SELECT name FROM students WHERE age > 18"},
    {"label": "✅ WHERE with String", "query": "SELECT name FROM employees WHERE department = 'CS'"},
    {"label": "✅ SELECT All (*)", "query": "SELECT * FROM courses"},
    {"label": "✅ WHERE with AND", "query": "SELECT name FROM students WHERE age > 18 AND grade = 'A'"},
    {"label": "✅ WHERE with OR", "query": "SELECT name FROM students WHERE dept = 'CS' OR dept = 'IT'"},
    {"label": "✅ Operators (>=)", "query": "SELECT name FROM students WHERE age >= 21"},
    {"label": "✅ INSERT INTO", "query": "INSERT INTO students VALUES (1, 'Rahul', 20)"},
    {"label": "❌ Missing Columns", "query": "SELECT FROM students"},
    {"label": "❌ Missing FROM", "query": "SELECT name students"},
    {"label": "❌ Missing Table", "query": "SELECT name FROM WHERE age > 18"},
    {"label": "❌ Trailing Comma", "query": "SELECT name, FROM students"},
]
