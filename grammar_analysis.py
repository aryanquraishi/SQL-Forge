"""
grammar_analysis.py — FIRST/FOLLOW Sets and Parsing Table Generator
Computes FIRST and FOLLOW sets for the SQL grammar.
Displays a simplified LALR(1) parsing table.

Syllabus Mapping:
  - Unit 2: Top Down Parsing — FIRST and FOLLOW sets
  - Unit 2: Predictive Parsing — LL(1) parsing table
  - Unit 2: Bottom Up Parsing — LALR(1) parsing tables
  - Unit 2: Construction of SLR parse tables
"""


# ============================================================
#  Grammar Definition for FIRST/FOLLOW Computation
# ============================================================

# Non-terminals and their productions (matches advanced parser.py)
GRAMMAR = {
    'query': [
        ['select_stmt'],
        ['insert_stmt'],
    ],
    'select_stmt': [
        ['SELECT', 'columns', 'FROM', 'table_refs'],
        ['SELECT', 'columns', 'FROM', 'table_refs', 'WHERE', 'condition'],
        ['SELECT', 'columns', 'FROM', 'table_refs', 'WHERE', 'condition', 'ORDER', 'BY', 'order_list'],
        ['SELECT', 'columns', 'FROM', 'table_refs', 'ORDER', 'BY', 'order_list'],
        ['SELECT', 'columns', 'FROM', 'table_refs', 'WHERE', 'condition', 'GROUP', 'BY', 'group_list'],
        ['SELECT', 'columns', 'FROM', 'table_refs', 'GROUP', 'BY', 'group_list', 'HAVING', 'condition'],
        ['SELECT', 'DISTINCT', 'columns', 'FROM', 'table_refs'],
    ],
    'columns': [
        ['STAR'],
        ['column_list'],
    ],
    'column_list': [
        ['column_expr'],
        ['column_expr', 'COMMA', 'column_list'],
    ],
    'column_expr': [
        ['IDENTIFIER'],
        ['IDENTIFIER', 'DOT', 'IDENTIFIER'],
        ['IDENTIFIER', 'AS', 'IDENTIFIER'],
        ['IDENTIFIER', 'DOT', 'IDENTIFIER', 'AS', 'IDENTIFIER'],
        ['IDENTIFIER', 'LPAREN', 'IDENTIFIER', 'RPAREN'],
        ['IDENTIFIER', 'LPAREN', 'IDENTIFIER', 'DOT', 'IDENTIFIER', 'RPAREN'],
        ['IDENTIFIER', 'LPAREN', 'STAR', 'RPAREN'],
        ['IDENTIFIER', 'LPAREN', 'IDENTIFIER', 'RPAREN', 'AS', 'IDENTIFIER'],
        ['IDENTIFIER', 'LPAREN', 'IDENTIFIER', 'DOT', 'IDENTIFIER', 'RPAREN', 'AS', 'IDENTIFIER'],
    ],
    'table_refs': [
        ['table_ref'],
        ['table_ref', 'join_clauses'],
    ],
    'table_ref': [
        ['IDENTIFIER'],
        ['IDENTIFIER', 'IDENTIFIER'],
        ['IDENTIFIER', 'AS', 'IDENTIFIER'],
    ],
    'join_clauses': [
        ['join_clause'],
        ['join_clause', 'join_clauses'],
    ],
    'join_clause': [
        ['JOIN', 'table_ref', 'ON', 'join_condition'],
    ],
    'join_condition': [
        ['IDENTIFIER', 'DOT', 'IDENTIFIER', 'EQ', 'IDENTIFIER', 'DOT', 'IDENTIFIER'],
        ['IDENTIFIER', 'EQ', 'IDENTIFIER'],
    ],
    'condition': [
        ['expression'],
        ['condition', 'AND', 'condition'],
        ['condition', 'OR', 'condition'],
        ['LPAREN', 'condition', 'RPAREN'],
    ],
    'expression': [
        ['value', 'operator', 'value'],
    ],
    'operator': [
        ['GT'], ['LT'], ['EQ'], ['GTE'], ['LTE'], ['NEQ'],
    ],
    'value': [
        ['NUMBER'], ['STRING'], ['IDENTIFIER'],
        ['IDENTIFIER', 'DOT', 'IDENTIFIER'],
        ['IDENTIFIER', 'LPAREN', 'IDENTIFIER', 'RPAREN'],
        ['IDENTIFIER', 'LPAREN', 'IDENTIFIER', 'DOT', 'IDENTIFIER', 'RPAREN'],
        ['IDENTIFIER', 'LPAREN', 'STAR', 'RPAREN'],
    ],
    'order_list': [
        ['order_item'],
        ['order_item', 'COMMA', 'order_list'],
    ],
    'order_item': [
        ['IDENTIFIER'],
        ['IDENTIFIER', 'ASC'],
        ['IDENTIFIER', 'DESC'],
        ['IDENTIFIER', 'DOT', 'IDENTIFIER'],
        ['IDENTIFIER', 'DOT', 'IDENTIFIER', 'ASC'],
        ['IDENTIFIER', 'DOT', 'IDENTIFIER', 'DESC'],
    ],
    'group_list': [
        ['group_item'],
        ['group_item', 'COMMA', 'group_list'],
    ],
    'group_item': [
        ['IDENTIFIER'],
        ['IDENTIFIER', 'DOT', 'IDENTIFIER'],
    ],
    'insert_stmt': [
        ['INSERT', 'INTO', 'IDENTIFIER', 'VALUES', 'LPAREN', 'value_list', 'RPAREN'],
    ],
    'value_list': [
        ['value'],
        ['value', 'COMMA', 'value_list'],
    ],
}

# All terminals (tokens)
TERMINALS = {
    'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES',
    'AND', 'OR', 'NOT',
    'JOIN', 'ON', 'ORDER', 'BY', 'ASC', 'DESC',
    'GROUP', 'HAVING', 'AS', 'DISTINCT',
    'IDENTIFIER', 'NUMBER', 'STRING',
    'COMMA', 'SEMICOLON', 'LPAREN', 'RPAREN',
    'STAR', 'DOT',
    'GT', 'LT', 'EQ', 'GTE', 'LTE', 'NEQ',
    'PLUS', 'MINUS', 'DIVIDE',
}

# All non-terminals
NON_TERMINALS = set(GRAMMAR.keys())


# ============================================================
#  FIRST Set Computation
# ============================================================

def compute_first_sets():
    """
    Compute FIRST sets for all non-terminals in the grammar.

    FIRST(A) = Set of terminals that can appear as the first symbol
               in any string derived from A.

    Algorithm:
    1. If X is a terminal, FIRST(X) = {X}
    2. If X → ε, add ε to FIRST(X)
    3. If X → Y1 Y2 ... Yk:
       - Add FIRST(Y1) - {ε} to FIRST(X)
       - If ε ∈ FIRST(Y1), add FIRST(Y2) - {ε} to FIRST(X)
       - Continue until no ε, or add ε if all Yi can derive ε

    Returns:
        dict: Non-terminal → set of first terminals
    """
    first = {nt: set() for nt in NON_TERMINALS}

    changed = True
    while changed:
        changed = False

        for nt, productions in GRAMMAR.items():
            for production in productions:
                # Process each symbol in the production
                for symbol in production:
                    if symbol in TERMINALS:
                        # Terminal: add directly
                        if symbol not in first[nt]:
                            first[nt].add(symbol)
                            changed = True
                        break  # Stop after first terminal
                    elif symbol in NON_TERMINALS:
                        # Non-terminal: add its FIRST set
                        before = len(first[nt])
                        first[nt] |= first[symbol] - {'ε'}
                        if len(first[nt]) > before:
                            changed = True

                        # If this non-terminal can't derive ε, stop
                        if 'ε' not in first[symbol]:
                            break
                    else:
                        break

    return first


# ============================================================
#  FOLLOW Set Computation
# ============================================================

def compute_follow_sets(first_sets=None):
    """
    Compute FOLLOW sets for all non-terminals in the grammar.
    """
    if first_sets is None:
        first_sets = compute_first_sets()

    follow = {nt: set() for nt in NON_TERMINALS}

    # Rule 1: Add $ to FOLLOW of start symbol
    follow['query'].add('$')

    changed = True
    while changed:
        changed = False

        for nt, productions in GRAMMAR.items():
            for production in productions:
                for i, symbol in enumerate(production):
                    if symbol not in NON_TERMINALS:
                        continue

                    # Get β (everything after this symbol)
                    beta = production[i + 1:]

                    if beta:
                        # Compute FIRST(β)
                        first_beta = _first_of_sequence(beta, first_sets)

                        # Add FIRST(β) - {ε} to FOLLOW(symbol)
                        before = len(follow[symbol])
                        follow[symbol] |= first_beta - {'ε'}
                        if len(follow[symbol]) > before:
                            changed = True

                        # If ε ∈ FIRST(β), add FOLLOW(A) to FOLLOW(symbol)
                        if 'ε' in first_beta:
                            before = len(follow[symbol])
                            follow[symbol] |= follow[nt]
                            if len(follow[symbol]) > before:
                                changed = True
                    else:
                        # β is empty: add FOLLOW(A) to FOLLOW(symbol)
                        before = len(follow[symbol])
                        follow[symbol] |= follow[nt]
                        if len(follow[symbol]) > before:
                            changed = True

    return follow


def _first_of_sequence(sequence, first_sets):
    """Compute FIRST set for a sequence of symbols."""
    result = set()

    for symbol in sequence:
        if symbol in TERMINALS:
            result.add(symbol)
            return result
        elif symbol in NON_TERMINALS:
            result |= first_sets[symbol] - {'ε'}
            if 'ε' not in first_sets[symbol]:
                return result

    result.add('ε')
    return result


# ============================================================
#  Parsing Table Generation (Simplified — for UI demonstration)
# ============================================================

def generate_parsing_table():
    """
    Generate a simplified LALR(1)-style parsing table.
    Expanded to cover advanced SQL constructs.
    """
    table = [
        {'state': 0, 'SELECT': 'Shift → S1', 'INSERT': 'Shift → S2', 'action': 'Start state'},
        {'state': 1, 'IDENTIFIER': 'Shift → S3', 'STAR': 'Shift → S4', 'DISTINCT': 'Shift → S1a', 'action': 'After SELECT'},
        {'state': 2, 'INTO': 'Shift → S5', 'action': 'After INSERT'},
        {'state': 3, 'COMMA': 'Shift → S6', 'DOT': 'Shift → S3a', 'AS': 'Shift → S3b', 'LPAREN': 'Shift → S3c', 'FROM': 'Reduce columns', 'action': 'After column name'},
        {'state': 4, 'FROM': 'Reduce columns→*', 'action': 'After *'},
        {'state': 5, 'IDENTIFIER': 'Shift → S7', 'action': 'After INTO'},
        {'state': 6, 'IDENTIFIER': 'Shift → S3', 'action': 'After comma (more columns)'},
        {'state': 7, 'VALUES': 'Shift → S8', 'action': 'After table (INSERT)'},
        {'state': 8, 'LPAREN': 'Shift → S9', 'action': 'After VALUES'},
        {'state': 9, 'NUMBER': 'Shift → S10', 'STRING': 'Shift → S10', 'IDENTIFIER': 'Shift → S10', 'action': 'Inside ( )'},
        {'state': 10, 'COMMA': 'Shift → S11', 'RPAREN': 'Reduce value_list', 'action': 'After value'},
        {'state': 11, 'IDENTIFIER': 'Shift → S12', 'action': 'After FROM — table ref'},
        {'state': 12, 'IDENTIFIER': 'Shift → S12a', 'JOIN': 'Shift → S20', 'WHERE': 'Shift → S13', 'ORDER': 'Shift → S30', 'GROUP': 'Shift → S40', '$': 'Reduce select_stmt', 'action': 'After table name (alias?)'},
        {'state': 13, 'IDENTIFIER': 'Shift → S14', 'action': 'After WHERE — condition LHS'},
        {'state': 14, 'DOT': 'Shift → S14a', 'GT': 'Shift → S15', 'LT': 'Shift → S15', 'EQ': 'Shift → S15', 'GTE': 'Shift → S15', 'LTE': 'Shift → S15', 'NEQ': 'Shift → S15', 'action': 'Condition LHS value'},
        {'state': 15, 'NUMBER': 'Shift → S16', 'STRING': 'Shift → S16', 'IDENTIFIER': 'Shift → S16', 'action': 'After operator — RHS'},
        {'state': 16, 'AND': 'Shift → S13', 'OR': 'Shift → S13', 'ORDER': 'Shift → S30', 'GROUP': 'Shift → S40', '$': 'Reduce select_stmt', 'action': 'After condition value'},
        {'state': 20, 'IDENTIFIER': 'Shift → S21', 'action': 'After JOIN — table ref'},
        {'state': 21, 'IDENTIFIER': 'Shift → S21a', 'ON': 'Shift → S22', 'action': 'After JOIN table (alias?)'},
        {'state': 22, 'IDENTIFIER': 'Shift → S23', 'action': 'After ON — join cond LHS'},
        {'state': 23, 'DOT': 'Shift → S24', 'EQ': 'Shift → S25', 'action': 'Join cond LHS'},
        {'state': 24, 'IDENTIFIER': 'Shift → S24a', 'action': 'After t.col in join cond'},
        {'state': 25, 'IDENTIFIER': 'Shift → S26', 'action': 'Join cond RHS'},
        {'state': 26, 'DOT': 'Shift → S27', 'JOIN': 'Shift → S20', 'WHERE': 'Shift → S13', 'ORDER': 'Shift → S30', '$': 'Reduce join', 'action': 'After join cond RHS'},
        {'state': 30, 'BY': 'Shift → S31', 'action': 'After ORDER'},
        {'state': 31, 'IDENTIFIER': 'Shift → S32', 'action': 'After ORDER BY — col'},
        {'state': 32, 'DOT': 'Shift → S32a', 'ASC': 'Shift → S33', 'DESC': 'Shift → S33', 'COMMA': 'Shift → S31', '$': 'Reduce select_stmt', 'action': 'Order column'},
        {'state': 33, 'COMMA': 'Shift → S31', '$': 'Reduce select_stmt', 'action': 'After ASC/DESC'},
        {'state': 40, 'BY': 'Shift → S41', 'action': 'After GROUP'},
        {'state': 41, 'IDENTIFIER': 'Shift → S42', 'action': 'After GROUP BY — col'},
        {'state': 42, 'DOT': 'Shift → S42a', 'COMMA': 'Shift → S41', 'HAVING': 'Shift → S43', '$': 'Reduce select_stmt', 'action': 'Group column'},
        {'state': 43, 'IDENTIFIER': 'Shift → S14', 'action': 'After HAVING — condition'},
    ]
    return table


# ============================================================
#  Formatted Display Functions
# ============================================================

def format_first_sets(first_sets=None):
    """Format FIRST sets as a list of dicts for UI display."""
    if first_sets is None:
        first_sets = compute_first_sets()
    
    result = []
    for nt in sorted(first_sets.keys()):
        terminals = sorted(first_sets[nt])
        result.append({
            'non_terminal': nt,
            'first_set': '{ ' + ', '.join(terminals) + ' }'
        })
    return result


def format_follow_sets(follow_sets=None):
    """Format FOLLOW sets as a list of dicts for UI display."""
    if follow_sets is None:
        follow_sets = compute_follow_sets()
    
    result = []
    for nt in sorted(follow_sets.keys()):
        terminals = sorted(follow_sets[nt])
        result.append({
            'non_terminal': nt,
            'follow_set': '{ ' + ', '.join(terminals) + ' }'
        })
    return result


def get_grammar_as_text():
    """Get the grammar rules as formatted text for display."""
    lines = []
    for nt, productions in GRAMMAR.items():
        for i, prod in enumerate(productions):
            if i == 0:
                lines.append(f"{nt:<15} → {' '.join(prod)}")
            else:
                lines.append(f"{'':>15} | {' '.join(prod)}")
    return "\n".join(lines)


# ============================================================
#  Module test
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("GRAMMAR RULES")
    print("=" * 60)
    print(get_grammar_as_text())
    
    print("\n" + "=" * 60)
    print("FIRST SETS")
    print("=" * 60)
    first = compute_first_sets()
    for item in format_first_sets(first):
        print(f"  FIRST({item['non_terminal']:<15}) = {item['first_set']}")
    
    print("\n" + "=" * 60)
    print("FOLLOW SETS")
    print("=" * 60)
    follow = compute_follow_sets(first)
    for item in format_follow_sets(follow):
        print(f"  FOLLOW({item['non_terminal']:<15}) = {item['follow_set']}")
    
    print("\n" + "=" * 60)
    print("PARSING TABLE (Simplified)")
    print("=" * 60)
    table = generate_parsing_table()
    for row in table:
        state = row.pop('state')
        action = row.pop('action')
        entries = {k: v for k, v in row.items()}
        print(f"  State {state}: {entries}  ({action})")
