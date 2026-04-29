"""
parser.py — Universal SQL Parser for Mini SQL Compiler
Uses sqlglot (production-grade SQL parser) to parse ANY valid SQL query.
Converts sqlglot's AST to our internal format for downstream pipeline.

Keeps PLY-style grammar trace for educational display.

Syllabus Mapping:
  - Unit 2: Context Free Grammars (CFG)
  - Unit 2: Bottom Up Parsing — LALR(1)
  - Unit 2: Parser Generator — YACC
  - Unit 2: Syntax Analysis
"""

import sqlglot
from sqlglot import exp
from errors import ErrorCollector


# ============================================================
#  Grammar Rules Trace — Records which production rules are applied
# ============================================================
grammar_trace = []


def reset_trace():
    global grammar_trace
    grammar_trace = []


def add_trace(rule_name, production):
    grammar_trace.append({
        'rule': rule_name,
        'production': production
    })


# ============================================================
#  Error Collector
# ============================================================
parse_errors = ErrorCollector()


def reset_errors():
    global parse_errors
    parse_errors = ErrorCollector()


# ============================================================
#  AST Converter — sqlglot AST → our internal dict format
# ============================================================

def _extract_column_name(node):
    """Extract column display string from a sqlglot expression node."""
    if node is None:
        return '*'
    sql = node.sql()
    return sql


def _extract_columns(select_node):
    """Extract column list from SELECT statement."""
    columns = []
    expressions = select_node.expressions
    if not expressions:
        return [{'expr': '*', 'alias': None}]

    for expr in expressions:
        alias = expr.alias if hasattr(expr, 'alias') and expr.alias else None
        # Get the inner expression if it's an Alias wrapper
        if isinstance(expr, exp.Alias):
            inner = expr.this
            alias = expr.alias
            expr_str = inner.sql()
        else:
            expr_str = expr.sql()
            alias = None

        is_agg = isinstance(expr.this if isinstance(expr, exp.Alias) else expr,
                            (exp.Avg, exp.Count, exp.Sum, exp.Min, exp.Max, exp.AggFunc))

        columns.append({
            'expr': expr_str,
            'alias': alias,
            'is_agg': is_agg,
        })

    return columns


def _extract_table(from_clause, parsed):
    """Extract table info including JOINs from the parsed statement."""
    if from_clause is None:
        return ''

    # Get the main table
    main_table = from_clause.this if hasattr(from_clause, 'this') else from_clause
    tbl_name = main_table.name if hasattr(main_table, 'name') else str(main_table)
    tbl_alias = main_table.alias if hasattr(main_table, 'alias') and main_table.alias else None

    result = {
        'name': tbl_name,
        'alias': tbl_alias or None,
        'joins': [],
    }

    # Extract JOINs
    joins = list(parsed.find_all(exp.Join))
    for join in joins:
        join_table = join.this
        jname = join_table.name if hasattr(join_table, 'name') else str(join_table)
        jalias = join_table.alias if hasattr(join_table, 'alias') and join_table.alias else None

        on_clause = join.args.get('on')
        on_info = {}
        if on_clause:
            on_sql = on_clause.sql()
            # Try to extract left = right
            if isinstance(on_clause, exp.EQ):
                on_info = {
                    'type': 'JOIN_COND',
                    'left': on_clause.left.sql(),
                    'right': on_clause.right.sql(),
                }
            else:
                on_info = {
                    'type': 'JOIN_COND',
                    'left': on_sql,
                    'right': '',
                }

        result['joins'].append({
            'type': 'JOIN',
            'table': {'name': jname, 'alias': jalias or None, 'joins': []},
            'on': on_info,
        })

    return result


def _extract_condition(where_node):
    """Recursively convert sqlglot WHERE expression to our condition dict format."""
    if where_node is None:
        return None

    if isinstance(where_node, exp.And):
        return {
            'type': 'AND',
            'left': _extract_condition(where_node.left),
            'right': _extract_condition(where_node.right),
        }

    if isinstance(where_node, exp.Or):
        return {
            'type': 'OR',
            'left': _extract_condition(where_node.left),
            'right': _extract_condition(where_node.right),
        }

    if isinstance(where_node, exp.Not):
        return {
            'type': 'NOT',
            'operand': _extract_condition(where_node.this),
        }

    if isinstance(where_node, exp.Paren):
        return _extract_condition(where_node.this)

    # Comparison operators
    op_map = {
        exp.GT: '>', exp.LT: '<', exp.EQ: '=',
        exp.GTE: '>=', exp.LTE: '<=', exp.NEQ: '!=',
        exp.Like: 'LIKE', exp.Is: 'IS',
    }

    for cls, op_str in op_map.items():
        if isinstance(where_node, cls):
            left = where_node.left.sql() if hasattr(where_node, 'left') else ''
            right = where_node.right.sql() if hasattr(where_node, 'right') else ''
            return {
                'type': 'COMPARISON',
                'left': left,
                'operator': op_str,
                'right': right,
            }

    # IN expression
    if isinstance(where_node, exp.In):
        return {
            'type': 'COMPARISON',
            'left': where_node.this.sql(),
            'operator': 'IN',
            'right': '(' + ', '.join(e.sql() for e in where_node.expressions) + ')' if where_node.expressions else where_node.args.get('query', where_node).sql() if not where_node.expressions else '',
        }

    # BETWEEN expression
    if isinstance(where_node, exp.Between):
        return {
            'type': 'COMPARISON',
            'left': where_node.this.sql(),
            'operator': 'BETWEEN',
            'right': f"{where_node.args['low'].sql()} AND {where_node.args['high'].sql()}",
        }

    # EXISTS
    if isinstance(where_node, exp.Exists):
        return {
            'type': 'COMPARISON',
            'left': 'EXISTS',
            'operator': '',
            'right': where_node.this.sql(),
        }

    # Fallback: any other expression
    return {
        'type': 'COMPARISON',
        'left': where_node.sql(),
        'operator': '',
        'right': '',
    }


def _extract_order_by(parsed):
    """Extract ORDER BY clause."""
    order = parsed.args.get('order')
    if not order:
        return None

    result = []
    for ordered in order.expressions:
        col_sql = ordered.this.sql()
        desc = ordered.args.get('desc', False)
        result.append({
            'column': col_sql,
            'direction': 'DESC' if desc else 'ASC',
        })

    return result


def _extract_group_by(parsed):
    """Extract GROUP BY clause."""
    group = parsed.args.get('group')
    if not group:
        return None

    return [g.sql() for g in group.expressions]


def _extract_having(parsed):
    """Extract HAVING clause."""
    having = parsed.args.get('having')
    if not having:
        return None
    return _extract_condition(having.this if isinstance(having, exp.Having) else having)


def _convert_select(parsed):
    """Convert sqlglot SELECT node to our internal AST dict."""
    # Check DISTINCT
    distinct = parsed.args.get('distinct') is not None

    # Columns
    columns = _extract_columns(parsed)

    # Table & JOINs
    from_clause = parsed.args.get('from')
    table = _extract_table(from_clause, parsed)

    # WHERE
    where = parsed.args.get('where')
    condition = _extract_condition(where.this) if where else None

    # ORDER BY
    order_by = _extract_order_by(parsed)

    # GROUP BY
    group_by = _extract_group_by(parsed)

    # HAVING
    having = _extract_having(parsed)

    return {
        'type': 'SELECT',
        'distinct': distinct,
        'columns': columns,
        'table': table,
        'condition': condition,
        'group_by': group_by,
        'having': having,
        'order_by': order_by,
    }


def _convert_insert(parsed):
    """Convert sqlglot INSERT node to our internal AST dict."""
    table_name = parsed.this.name if hasattr(parsed.this, 'name') else str(parsed.this)
    values = []
    expr_node = parsed.expression
    if expr_node and hasattr(expr_node, 'expressions'):
        for row in expr_node.expressions:
            if hasattr(row, 'expressions'):
                for val in row.expressions:
                    values.append(val.sql())
            else:
                values.append(row.sql())

    return {
        'type': 'INSERT',
        'table': table_name,
        'values': values,
    }


def _generate_trace(parsed, depth=0):
    """Walk the sqlglot AST and generate grammar-rule-like trace entries."""
    if parsed is None:
        return

    node_type = type(parsed).__name__

    # Map sqlglot node types to grammar rule descriptions
    trace_map = {
        'Select': ('select_stmt', 'query -> SELECT columns FROM table_refs [WHERE] [GROUP BY] [HAVING] [ORDER BY]'),
        'Insert': ('insert_stmt', 'query -> INSERT INTO table VALUES (value_list)'),
        'From': ('from_clause', 'from_clause -> FROM table_ref'),
        'Where': ('where_clause', 'where_clause -> WHERE condition'),
        'Join': ('join_clause', 'join_clause -> JOIN table_ref ON condition'),
        'Order': ('order_clause', 'order_clause -> ORDER BY order_list'),
        'Group': ('group_clause', 'group_clause -> GROUP BY group_list'),
        'Having': ('having_clause', 'having_clause -> HAVING condition'),
        'Column': ('column_expr', None),
        'Star': ('column_expr', 'column_expr -> *'),
        'Table': ('table_ref', None),
        'Alias': ('alias', None),
        'And': ('condition', 'condition -> condition AND condition'),
        'Or': ('condition', 'condition -> condition OR condition'),
        'Not': ('condition', 'condition -> NOT condition'),
        'EQ': ('expression', 'expression -> value = value'),
        'GT': ('expression', 'expression -> value > value'),
        'LT': ('expression', 'expression -> value < value'),
        'GTE': ('expression', 'expression -> value >= value'),
        'LTE': ('expression', 'expression -> value <= value'),
        'NEQ': ('expression', 'expression -> value != value'),
        'Like': ('expression', 'expression -> value LIKE pattern'),
        'In': ('expression', 'expression -> value IN (subquery|list)'),
        'Between': ('expression', 'expression -> value BETWEEN low AND high'),
        'Exists': ('expression', 'expression -> EXISTS (subquery)'),
        'Subquery': ('subquery', 'subquery -> ( SELECT ... )'),
        'Avg': ('agg_func', 'agg_func -> AVG(expr)'),
        'Count': ('agg_func', 'agg_func -> COUNT(expr)'),
        'Sum': ('agg_func', 'agg_func -> SUM(expr)'),
        'Min': ('agg_func', 'agg_func -> MIN(expr)'),
        'Max': ('agg_func', 'agg_func -> MAX(expr)'),
        'Distinct': ('distinct', 'opt_distinct -> DISTINCT'),
        'Ordered': ('order_item', None),
        'Paren': ('paren', 'paren -> ( expression )'),
        'Literal': ('value', None),
        'Identifier': ('identifier', None),
        'Dot': ('qualified_name', 'qualified_name -> table.column'),
    }

    if node_type in trace_map:
        rule, prod = trace_map[node_type]
        if prod:
            add_trace(rule, prod)
        elif node_type == 'Column':
            col_sql = parsed.sql()
            add_trace('column_expr', f'column_expr -> {col_sql}')
        elif node_type == 'Table':
            tbl_name = parsed.name if hasattr(parsed, 'name') else str(parsed)
            alias = parsed.alias if hasattr(parsed, 'alias') and parsed.alias else ''
            if alias:
                add_trace('table_ref', f'table_ref -> {tbl_name} {alias} (alias)')
            else:
                add_trace('table_ref', f'table_ref -> {tbl_name}')
        elif node_type == 'Alias':
            add_trace('alias', f'alias -> ... AS {parsed.alias}')
        elif node_type == 'Ordered':
            desc = parsed.args.get('desc', False)
            add_trace('order_item', f'order_item -> {parsed.this.sql()} {"DESC" if desc else "ASC"}')
        elif node_type == 'Literal':
            add_trace('value', f'value -> {parsed.sql()}')
        elif node_type == 'Identifier':
            add_trace('identifier', f'identifier -> {parsed.name}')

    # Recurse into children
    for _, child_nodes in parsed.args.items():
        if isinstance(child_nodes, list):
            for child in child_nodes:
                if isinstance(child, exp.Expression):
                    _generate_trace(child, depth + 1)
        elif isinstance(child_nodes, exp.Expression):
            _generate_trace(child_nodes, depth + 1)


# ============================================================
#  Parse Function — Main interface for the compiler
# ============================================================
def parse_query(query):
    """
    Parse ANY SQL query string using sqlglot.
    Three-layer validation:
      1. Pre-validation  — catches obvious structural errors (quotes, parens, commas)
      2. sqlglot strict   — catches syntax errors via RAISE error level
      3. Round-trip check — catches silently dropped/modified tokens

    Returns:
        tuple: (ast_dict, grammar_trace_list, error_collector)
    """
    reset_trace()
    reset_errors()

    # ── Layer 0: Empty check ──
    cleaned = query.strip().rstrip(';').strip()
    if not cleaned:
        parse_errors.add_syntax_error(
            message="Empty query — nothing to compile",
            hint="Type a SQL query, e.g.: SELECT name FROM students"
        )
        return None, list(grammar_trace), parse_errors

    # ── Layer 1: Pre-validation (structural checks) ──
    validation_error = _pre_validate_sql(cleaned)
    if validation_error:
        parse_errors.add_syntax_error(
            message=validation_error['message'],
            hint=validation_error['hint']
        )
        return None, list(grammar_trace), parse_errors

    # ── Layer 2: sqlglot strict parse ──
    try:
        parsed_list = sqlglot.parse(query, error_level=sqlglot.ErrorLevel.RAISE)
        if not parsed_list or parsed_list[0] is None:
            parse_errors.add_syntax_error(
                message="Could not parse query — empty or invalid SQL",
                hint="Check SQL format — Example: SELECT name FROM students WHERE age > 18"
            )
            return None, list(grammar_trace), parse_errors

        parsed = parsed_list[0]

        # ── Layer 3: Round-trip token verification ──
        roundtrip_error = _roundtrip_verify(cleaned, parsed)
        if roundtrip_error:
            parse_errors.add_syntax_error(
                message=roundtrip_error['message'],
                hint=roundtrip_error['hint']
            )
            return None, list(grammar_trace), parse_errors

        # ── Generate grammar trace by walking the AST ──
        _generate_trace(parsed)

        # ── Convert to our internal AST format ──
        if isinstance(parsed, exp.Select):
            result = _convert_select(parsed)
        elif isinstance(parsed, exp.Insert):
            result = _convert_insert(parsed)
        elif isinstance(parsed, exp.Update):
            result = _convert_update(parsed)
        elif isinstance(parsed, exp.Delete):
            result = _convert_delete(parsed)
        elif isinstance(parsed, exp.Create):
            result = _convert_create(parsed)
        else:
            result = {
                'type': type(parsed).__name__.upper(),
                'sql': parsed.sql(),
                'columns': [],
                'table': '',
                'condition': None,
                'group_by': None,
                'having': None,
                'order_by': None,
            }

        return result, list(grammar_trace), parse_errors

    except sqlglot.errors.ParseError as e:
        if hasattr(e, 'errors') and e.errors:
            first_err = e.errors[0]
            desc = first_err.get('description', 'Syntax error')
            line = first_err.get('line', 1)
            col = first_err.get('col', 0)
            parse_errors.add_syntax_error(
                message=f"Syntax Error: {desc} at Line {line}, Column {col}",
                hint="Check the exact position mentioned above. Look for missing quotes, missing commas, or wrong keywords."
            )
        else:
            err_msg = str(e)
            clean_msg = err_msg.split('. ')[0] if '. ' in err_msg else err_msg
            parse_errors.add_syntax_error(
                message=f"SQL Syntax Error: {clean_msg}",
                hint="Check your SQL syntax. Common issues: missing commas, unmatched parentheses, misspelled keywords."
            )
        return None, list(grammar_trace), parse_errors

    except Exception as e:
        parse_errors.add_syntax_error(
            message=f"Parser exception: {str(e)}",
            hint="Query mein koi unexpected structure hai — basic SQL format check karein"
        )
        return None, list(grammar_trace), parse_errors


# ============================================================
#  Layer 1: Pre-Validation — Structural checks before parsing
# ============================================================

def _pre_validate_sql(query):
    """
    Pre-validate SQL string for structural errors that sqlglot cannot catch.
    Returns dict with 'message' and 'hint' if error found, else None.
    """
    import re
    upper = query.upper().strip()

    # ── Unmatched quotes ──
    single_quotes = query.count("'")
    if single_quotes % 2 != 0:
        return {
            'message': "Syntax Error: Unmatched single quote (') — string literal not properly closed",
            'hint': "Every opening ' must have a closing '. Example: WHERE name = 'Rahul'"
        }
    double_quotes = query.count('"')
    if double_quotes % 2 != 0:
        return {
            'message': 'Syntax Error: Unmatched double quote (") — identifier not properly closed',
            'hint': 'Every opening " must have a closing ". Example: "column_name"'
        }

    # ── Unmatched parentheses ──
    open_p = query.count('(')
    close_p = query.count(')')
    if open_p > close_p:
        return {
            'message': f"Syntax Error: {open_p - close_p} unmatched opening parenthesis '(' — missing closing ')'",
            'hint': "Every '(' must have a matching ')'. Check subqueries and function calls."
        }
    if close_p > open_p:
        return {
            'message': f"Syntax Error: {close_p - open_p} unmatched closing parenthesis ')' — missing opening '('",
            'hint': "Every ')' must have a matching '('. Check subqueries and function calls."
        }

    # ── Consecutive commas: SELECT ,,name  or  VALUES(1,,2) ──
    # Remove content inside quotes first so 'a,,b' doesn't false-positive
    no_strings = re.sub(r"'[^']*'", "''", query)
    if ',,' in no_strings.replace(' ', ''):
        return {
            'message': "Syntax Error: Consecutive commas found — empty column/value between commas",
            'hint': "Remove the extra comma. Example: SELECT name, age FROM students"
        }

    # ── Leading comma after keyword: SELECT , name ──
    if re.search(r'\b(SELECT|BY|SET|VALUES\s*\()\s*,', upper):
        return {
            'message': "Syntax Error: Unexpected comma — missing value/column before comma",
            'hint': "Columns/values should start with a name. Example: SELECT name, age FROM students"
        }

    # ── Trailing comma before keyword: name, FROM / name, WHERE / name, ORDER ──
    if re.search(r',\s*(FROM|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|ON|SET|VALUES)\b', upper):
        kw = re.search(r',\s*(FROM|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|ON|SET|VALUES)\b', upper).group(1)
        return {
            'message': f"Syntax Error: Trailing comma before {kw} — extra comma after last item",
            'hint': f"Remove the comma before {kw}"
        }

    # ── Empty clause body: SELECT FROM / WHERE ORDER / FROM WHERE ──
    clause_pairs = [
        (r'SELECT\s+(FROM)\b', "No columns specified between SELECT and FROM", "Add column names or * after SELECT"),
        (r'FROM\s+(WHERE|ORDER|GROUP|HAVING|LIMIT)\b', "FROM without table name", "Specify a table after FROM. Example: FROM students"),
        (r'WHERE\s+(ORDER|GROUP|HAVING|LIMIT)\b', "Empty WHERE clause — no condition after WHERE", "Add a condition. Example: WHERE age > 18"),
        (r'WHERE\s*$', "WHERE clause is empty — no condition specified", "Add a condition. Example: WHERE age > 18"),
        (r'ON\s+(WHERE|ORDER|GROUP|HAVING|JOIN|AND|OR)\b', "Empty ON clause — no join condition", "Add a join condition. Example: ON s.id = c.id"),
        (r'SET\s+(WHERE)\b', "Empty SET clause — no assignments", "Add assignments. Example: SET age = 21"),
        (r'ORDER\s+BY\s*$', "ORDER BY clause is empty", "Add column. Example: ORDER BY name ASC"),
        (r'GROUP\s+BY\s*$', "GROUP BY clause is empty", "Add column. Example: GROUP BY department"),
    ]
    for pattern, msg, hint in clause_pairs:
        if re.search(pattern, upper):
            return {'message': f"Syntax Error: {msg}", 'hint': hint}

    # ── INSERT without INTO ──
    if upper.startswith('INSERT') and 'INTO' not in upper:
        return {
            'message': "Syntax Error: INSERT without INTO — correct syntax is INSERT INTO",
            'hint': "Example: INSERT INTO students VALUES (1, 'Rahul', 20)"
        }

    # ── DELETE without FROM ──
    if upper.startswith('DELETE') and 'FROM' not in upper:
        return {
            'message': "Syntax Error: DELETE without FROM — correct syntax is DELETE FROM",
            'hint': "Example: DELETE FROM students WHERE age < 18"
        }

    # ── UPDATE without SET ──
    if upper.startswith('UPDATE') and 'SET' not in upper:
        return {
            'message': "Syntax Error: UPDATE without SET — must specify columns to update",
            'hint': "Example: UPDATE students SET age = 21 WHERE name = 'Rahul'"
        }

    return None


# ============================================================
#  Layer 3: Round-trip Token Verification
#  Catches ANY error sqlglot silently accepts by comparing tokens
# ============================================================

def _roundtrip_verify(original_sql, parsed_ast):
    """
    Verify the parse by round-tripping: regenerate SQL from AST,
    then compare meaningful tokens. If tokens were silently dropped
    or changed, that means the original SQL had an error.

    Returns dict with 'message'/'hint' if mismatch found, else None.
    """
    import re

    try:
        regenerated = parsed_ast.sql()
    except Exception:
        return None  # If regeneration itself fails, let other layers handle it

    # Tokenize both into comparable word-level tokens
    def tokenize(sql):
        """Extract meaningful tokens: keywords, identifiers, operators, values."""
        sql = sql.strip().rstrip(';').strip()
        # Split on whitespace and punctuation but keep the pieces
        tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_.]*|'[^']*'|\"[^\"]*\"|\d+(?:\.\d+)?|[<>=!]+|[(),*;]", sql)
        # Normalize: uppercase keywords, keep identifiers as-is for case-insensitive comparison
        return [t.upper() for t in tokens]

    orig_tokens = tokenize(original_sql)
    regen_tokens = tokenize(regenerated)

    # Find tokens in original that are completely missing from regenerated
    # Use a multiset comparison (count-based) to handle duplicates properly
    from collections import Counter
    orig_counts = Counter(orig_tokens)
    regen_counts = Counter(regen_tokens)

    missing = {}
    for token, count in orig_counts.items():
        diff = count - regen_counts.get(token, 0)
        if diff > 0:
            missing[token] = diff

    # Filter out noise: semicolons, AS keyword (sqlglot may add/remove), parentheses for style
    noise = {';', 'AS', '(', ')', 'INNER', 'OUTER'}
    missing = {k: v for k, v in missing.items() if k not in noise}

    if missing:
        # Build a helpful message showing what was dropped
        dropped = []
        for token, count in missing.items():
            if count > 1:
                dropped.append(f"'{token}' (x{count})")
            else:
                dropped.append(f"'{token}'")

        dropped_str = ", ".join(dropped[:5])  # Show max 5 to keep message readable
        extra = f" and {len(dropped) - 5} more" if len(dropped) > 5 else ""

        return {
            'message': f"Syntax Error: Invalid or misplaced tokens detected — {dropped_str}{extra} could not be parsed correctly",
            'hint': f"The parser could not place these tokens in a valid SQL structure. Check spelling, order of clauses, and missing keywords. Regenerated interpretation: {regenerated}"
        }

    return None


# ============================================================
#  Additional statement converters (UPDATE, DELETE, CREATE)
# ============================================================

def _convert_update(parsed):
    """Convert UPDATE statement."""
    table_name = parsed.this.name if hasattr(parsed.this, 'name') else str(parsed.this)
    sets = []
    for s in parsed.expressions:
        sets.append(s.sql())

    where = parsed.args.get('where')
    condition = _extract_condition(where.this) if where else None

    return {
        'type': 'UPDATE',
        'table': table_name,
        'sets': sets,
        'condition': condition,
        'columns': [{'expr': s, 'alias': None} for s in sets],
        'group_by': None, 'having': None, 'order_by': None,
    }


def _convert_delete(parsed):
    """Convert DELETE statement."""
    table_name = parsed.this.name if hasattr(parsed.this, 'name') else str(parsed.this)
    where = parsed.args.get('where')
    condition = _extract_condition(where.this) if where else None

    return {
        'type': 'DELETE',
        'table': table_name,
        'condition': condition,
        'columns': [],
        'group_by': None, 'having': None, 'order_by': None,
    }


def _convert_create(parsed):
    """Convert CREATE TABLE statement."""
    table_expr = parsed.this
    table_name = table_expr.name if hasattr(table_expr, 'name') else str(table_expr)
    col_defs = []
    if hasattr(table_expr, 'expressions'):
        for col_def in table_expr.expressions:
            col_defs.append(col_def.sql())

    return {
        'type': 'CREATE',
        'table': table_name,
        'columns': [{'expr': c, 'alias': None} for c in col_defs],
        'condition': None,
        'group_by': None, 'having': None, 'order_by': None,
    }


# ============================================================
#  Grammar Rules Display (educational — static)
# ============================================================
def get_grammar_rules():
    """Get comprehensive CFG grammar rules for display."""
    rules = [
        "query          -> select_stmt | insert_stmt | update_stmt | delete_stmt | create_stmt",
        "select_stmt    -> SELECT [DISTINCT] columns FROM table_refs [WHERE condition] [GROUP BY group_list] [HAVING condition] [ORDER BY order_list] [LIMIT number]",
        "columns        -> * | column_list",
        "column_list    -> column_expr | column_expr , column_list",
        "column_expr    -> value | value AS IDENTIFIER | agg_func | agg_func AS IDENTIFIER | ( subquery ) [AS IDENTIFIER]",
        "agg_func       -> (AVG|COUNT|SUM|MIN|MAX) ( value | * )",
        "value          -> NUMBER | STRING | IDENTIFIER | IDENTIFIER.IDENTIFIER | agg_func | ( subquery )",
        "table_refs     -> table_ref | table_ref join_clauses",
        "table_ref      -> IDENTIFIER [IDENTIFIER|AS IDENTIFIER] | ( subquery ) AS IDENTIFIER",
        "join_clauses   -> join_clause | join_clause join_clauses",
        "join_clause    -> [LEFT|RIGHT|INNER|OUTER|CROSS] JOIN table_ref ON condition",
        "condition      -> expression | condition AND condition | condition OR condition | NOT condition | ( condition ) | EXISTS ( subquery ) | value IN ( subquery | value_list )",
        "expression     -> value operator value | value BETWEEN value AND value | value LIKE pattern | value IS [NOT] NULL",
        "operator       -> = | != | > | < | >= | <=",
        "subquery       -> ( select_stmt )",
        "order_list     -> order_item | order_item , order_list",
        "order_item     -> value [ASC|DESC]",
        "group_list     -> value | value , group_list",
        "insert_stmt    -> INSERT INTO IDENTIFIER [(column_list)] VALUES ( value_list ) | INSERT INTO IDENTIFIER select_stmt",
        "update_stmt    -> UPDATE IDENTIFIER SET assignment_list [WHERE condition]",
        "delete_stmt    -> DELETE FROM IDENTIFIER [WHERE condition]",
        "create_stmt    -> CREATE TABLE IDENTIFIER ( column_def_list )",
        "value_list     -> value | value , value_list",
    ]
    return rules


# ============================================================
#  Module test
# ============================================================
if __name__ == '__main__':
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    test_queries = [
        "SELECT name, age FROM students WHERE age > 18",
        "SELECT * FROM courses",
        "INSERT INTO students VALUES (1, 'Rahul', 20)",
        "SELECT s.name, s.age FROM students s WHERE s.age > 18",
        "SELECT s.name FROM students s JOIN courses c ON s.course_id = c.course_id",
        "SELECT s.name FROM students s JOIN courses c ON s.id = c.id WHERE s.age > 18 ORDER BY s.name ASC",
        "SELECT DISTINCT name FROM students",
        "SELECT c.name, AVG(s.marks) AS avg_marks FROM students s JOIN courses c ON s.cid = c.cid GROUP BY c.name HAVING AVG(s.marks) > 90",
        # Subqueries
        "SELECT name, marks FROM students WHERE marks > (SELECT AVG(marks) FROM students)",
        "SELECT * FROM students WHERE grade = (SELECT grade FROM students WHERE name = 'Rahul')",
        # Complex
        "SELECT s.student_id, s.name FROM students s JOIN courses c ON s.course_id = c.course_id JOIN teachers t ON c.teacher_id = t.teacher_id WHERE s.age > 18 AND s.grade = 'A' ORDER BY s.student_id ASC",
        # CREATE / UPDATE / DELETE
        "CREATE TABLE students (id INT, name VARCHAR(50), age INT)",
        "UPDATE students SET age = 21 WHERE name = 'Rahul'",
        "DELETE FROM students WHERE age < 18",
        # Error case
        "SELECT FROM",
    ]

    for query in test_queries:
        q = query.strip()
        print(f"\nQuery: {q[:90]}{'...' if len(q) > 90 else ''}")
        print("=" * 95)

        ast, trace, errors = parse_query(q)

        if errors.has_errors():
            for e in errors.errors:
                print(f"  ERROR: {e.message}")
        elif ast:
            print(f"  VALID | Type: {ast.get('type')} | Trace: {len(trace)} rules | Keys: {list(ast.keys())}")
        else:
            print(f"  VALID (empty AST)")
