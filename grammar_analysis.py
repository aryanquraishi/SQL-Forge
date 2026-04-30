"""
grammar_analysis.py — FIRST/FOLLOW Sets and Parsing Table Generator
Computes FIRST and FOLLOW sets for the SQL grammar.
Generates a DYNAMIC LALR(1) parsing table based on the actual grammar.

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
        ['update_stmt'],
        ['delete_stmt'],
        ['create_stmt'],
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
    'update_stmt': [
        ['UPDATE', 'IDENTIFIER', 'SET', 'assignment_list'],
        ['UPDATE', 'IDENTIFIER', 'SET', 'assignment_list', 'WHERE', 'condition'],
    ],
    'assignment_list': [
        ['assignment'],
        ['assignment', 'COMMA', 'assignment_list'],
    ],
    'assignment': [
        ['IDENTIFIER', 'EQ', 'value'],
    ],
    'delete_stmt': [
        ['DELETE', 'FROM', 'IDENTIFIER'],
        ['DELETE', 'FROM', 'IDENTIFIER', 'WHERE', 'condition'],
    ],
    'create_stmt': [
        ['CREATE', 'TABLE', 'IDENTIFIER', 'LPAREN', 'column_def_list', 'RPAREN'],
    ],
    'column_def_list': [
        ['column_def'],
        ['column_def', 'COMMA', 'column_def_list'],
    ],
    'column_def': [
        ['IDENTIFIER', 'IDENTIFIER'],
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
    'UPDATE', 'SET', 'DELETE', 'CREATE', 'TABLE',
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
    2. If X -> epsilon, add epsilon to FIRST(X)
    3. If X -> Y1 Y2 ... Yk:
       - Add FIRST(Y1) - {epsilon} to FIRST(X)
       - If epsilon in FIRST(Y1), add FIRST(Y2) - {epsilon} to FIRST(X)
       - Continue until no epsilon, or add epsilon if all Yi can derive epsilon

    Returns:
        dict: Non-terminal -> set of first terminals
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
                        first[nt] |= first[symbol] - {'epsilon'}
                        if len(first[nt]) > before:
                            changed = True

                        # If this non-terminal can't derive epsilon, stop
                        if 'epsilon' not in first[symbol]:
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

                    # Get beta (everything after this symbol)
                    beta = production[i + 1:]

                    if beta:
                        # Compute FIRST(beta)
                        first_beta = _first_of_sequence(beta, first_sets)

                        # Add FIRST(beta) - {epsilon} to FOLLOW(symbol)
                        before = len(follow[symbol])
                        follow[symbol] |= first_beta - {'epsilon'}
                        if len(follow[symbol]) > before:
                            changed = True

                        # If epsilon in FIRST(beta), add FOLLOW(A) to FOLLOW(symbol)
                        if 'epsilon' in first_beta:
                            before = len(follow[symbol])
                            follow[symbol] |= follow[nt]
                            if len(follow[symbol]) > before:
                                changed = True
                    else:
                        # beta is empty: add FOLLOW(A) to FOLLOW(symbol)
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
            result |= first_sets[symbol] - {'epsilon'}
            if 'epsilon' not in first_sets[symbol]:
                return result

    result.add('epsilon')
    return result


# ============================================================
#  Dynamic LALR(1) Parsing Table Generation
#  Builds LR(1) item sets, then merges states with identical
#  cores (but different lookaheads) to form the LALR(1) table.
#  Follows the standard algorithm as described in textbooks/GFG.
# ============================================================

def _augment_grammar(start_nt):
    """Create augmented grammar with S' -> start_nt production."""
    aug = {"S'": [[start_nt]]}
    # Only include non-terminals reachable from start_nt
    reachable = set()
    _find_reachable(start_nt, reachable)
    for nt in reachable:
        if nt in GRAMMAR:
            aug[nt] = GRAMMAR[nt]
    return aug


def _find_reachable(nt, visited):
    """Find all non-terminals reachable from a given non-terminal."""
    if nt in visited or nt not in GRAMMAR:
        return
    visited.add(nt)
    for prod in GRAMMAR[nt]:
        for sym in prod:
            if sym in NON_TERMINALS:
                _find_reachable(sym, visited)


def _build_production_list(grammar):
    """
    Build a numbered list of productions for reduce references.
    Returns list of (nt, production) tuples.
    Production 0 is always S' -> start_nt (augmented).
    """
    prod_list = []
    for nt in grammar:
        for prod in grammar[nt]:
            prod_list.append((nt, prod))
    return prod_list


def _first_of_symbol(symbol, grammar, first_cache, terminals_set):
    """Compute FIRST set for a single symbol."""
    if symbol in first_cache:
        return first_cache[symbol]
    if symbol in terminals_set:
        first_cache[symbol] = {symbol}
        return {symbol}
    if symbol not in grammar:
        first_cache[symbol] = {symbol}
        return {symbol}

    result = set()
    first_cache[symbol] = result  # prevent infinite recursion
    for prod in grammar[symbol]:
        for s in prod:
            f = _first_of_symbol(s, grammar, first_cache, terminals_set)
            result |= (f - {'epsilon'})
            if 'epsilon' not in f:
                break
        else:
            result.add('epsilon')
    first_cache[symbol] = result
    return result


def _first_of_sequence_lr(sequence, grammar, first_cache, terminals_set):
    """Compute FIRST set for a sequence of symbols (for LR(1) lookahead)."""
    result = set()
    for symbol in sequence:
        f = _first_of_symbol(symbol, grammar, first_cache, terminals_set)
        result |= (f - {'epsilon'})
        if 'epsilon' not in f:
            return result
    result.add('epsilon')
    return result


def _lr1_closure(items, grammar, all_nts, first_cache, terminals_set):
    """
    Compute closure of a set of LR(1) items.
    Each item is (nt, prod_idx, dot_pos, lookahead).
    """
    closure = set(items)
    changed = True
    while changed:
        changed = False
        new_items = set()
        for (nt, prod_idx, dot_pos, la) in list(closure):
            prods = grammar.get(nt, [])
            if prod_idx >= len(prods):
                continue
            prod = prods[prod_idx]
            if dot_pos < len(prod):
                next_sym = prod[dot_pos]
                if next_sym in all_nts and next_sym in grammar:
                    # beta = everything after the next_sym in this production
                    beta = list(prod[dot_pos + 1:]) + [la]
                    first_beta = _first_of_sequence_lr(beta, grammar, first_cache, terminals_set)
                    for b_la in first_beta:
                        if b_la == 'epsilon':
                            continue
                        for pi, _ in enumerate(grammar[next_sym]):
                            item = (next_sym, pi, 0, b_la)
                            if item not in closure:
                                new_items.add(item)
        if new_items:
            closure |= new_items
            changed = True
    return frozenset(closure)


def _lr1_goto(items, symbol, grammar, all_nts, first_cache, terminals_set):
    """Compute GOTO(items, symbol) for LR(1) items."""
    moved = set()
    for (nt, prod_idx, dot_pos, la) in items:
        prods = grammar.get(nt, [])
        if prod_idx >= len(prods):
            continue
        prod = prods[prod_idx]
        if dot_pos < len(prod) and prod[dot_pos] == symbol:
            moved.add((nt, prod_idx, dot_pos + 1, la))
    if not moved:
        return frozenset()
    return _lr1_closure(moved, grammar, all_nts, first_cache, terminals_set)


def _get_core(item_set):
    """Extract the core (LR(0) part) of an LR(1) item set — ignoring lookaheads."""
    return frozenset((nt, prod_idx, dot_pos) for (nt, prod_idx, dot_pos, _) in item_set)


def generate_parsing_table_for_query(query_type='SELECT'):
    """
    Generate a proper LALR(1) parsing table following the standard algorithm:
    1. Build CLR(1) item sets with lookaheads
    2. Merge states with identical cores (LALR reduction)
    3. Build ACTION/GOTO table with standard S#/R#/acc notation

    Args:
        query_type: 'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE'

    Returns:
        list of dicts — each dict is one row of the parsing table
    """
    start_map = {
        'SELECT': 'select_stmt',
        'INSERT': 'insert_stmt',
        'UPDATE': 'update_stmt',
        'DELETE': 'delete_stmt',
        'CREATE': 'create_stmt',
    }
    start_nt = start_map.get(query_type, 'select_stmt')

    # Build augmented grammar
    aug_grammar = _augment_grammar(start_nt)
    all_nts = set(aug_grammar.keys())

    # Collect all symbols
    all_symbols = set()
    for nt, prods in aug_grammar.items():
        for prod in prods:
            for sym in prod:
                all_symbols.add(sym)

    terminals_used = sorted(all_symbols & TERMINALS)
    nonterminals_used = sorted(all_nts - {"S'"})

    # Build numbered production list (for R# references)
    # Production 0 = S' -> start_nt, then all others
    prod_list = []
    prod_list.append(("S'", aug_grammar["S'"][0]))
    for nt in sorted(aug_grammar.keys()):
        if nt == "S'":
            continue
        for prod in aug_grammar[nt]:
            prod_list.append((nt, prod))

    # Build a lookup: (nt, tuple(prod)) -> production number
    prod_num = {}
    for i, (nt, prod) in enumerate(prod_list):
        prod_num[(nt, tuple(prod))] = i

    # Pre-compute FIRST sets
    first_cache = {}
    terminals_set = TERMINALS | {'$'}

    # ---- STEP 1: Build CLR(1) item sets ----
    start_items = _lr1_closure(
        {("S'", 0, 0, '$')}, aug_grammar, all_nts, first_cache, terminals_set
    )
    clr_states = [start_items]
    clr_state_map = {start_items: 0}
    clr_transitions = {}

    queue = [start_items]
    while queue:
        current = queue.pop(0)
        current_idx = clr_state_map[current]

        for sym in terminals_used + nonterminals_used:
            next_state = _lr1_goto(current, sym, aug_grammar, all_nts, first_cache, terminals_set)
            if not next_state:
                continue
            if next_state not in clr_state_map:
                clr_state_map[next_state] = len(clr_states)
                clr_states.append(next_state)
                queue.append(next_state)
            clr_transitions[(current_idx, sym)] = clr_state_map[next_state]

    # ---- STEP 2: Merge CLR states with identical cores (LALR) ----
    core_to_states = {}
    for idx, item_set in enumerate(clr_states):
        core = _get_core(item_set)
        if core not in core_to_states:
            core_to_states[core] = []
        core_to_states[core].append(idx)

    # Map old CLR state index -> new LALR state index
    clr_to_lalr = {}
    lalr_states = []  # list of merged item sets
    lalr_labels = []  # display labels for merged states

    for core, old_indices in core_to_states.items():
        new_idx = len(lalr_states)
        for oi in old_indices:
            clr_to_lalr[oi] = new_idx
        # Merge all items from all states with this core
        merged = set()
        for oi in old_indices:
            merged |= set(clr_states[oi])
        lalr_states.append(frozenset(merged))
        # Label: if single state, use its number; if merged, show combined
        if len(old_indices) == 1:
            lalr_labels.append(str(old_indices[0]))
        else:
            lalr_labels.append('/'.join(str(x) for x in sorted(old_indices)))

    # Re-map transitions to LALR state indices
    lalr_transitions = {}
    for (old_src, sym), old_tgt in clr_transitions.items():
        new_src = clr_to_lalr[old_src]
        new_tgt = clr_to_lalr[old_tgt]
        lalr_transitions[(new_src, sym)] = new_tgt

    # ---- STEP 3: Build ACTION and GOTO table ----
    # Column order: State | ACTION terminals... | $ | GOTO non-terminals...
    action_cols = terminals_used + ['$']
    goto_cols = nonterminals_used

    table = []
    for lalr_idx, item_set in enumerate(lalr_states):
        row = {'State': lalr_idx}

        # Initialize all columns empty
        for t in action_cols:
            row[t] = ''
        for nt in goto_cols:
            row[nt] = ''

        for (nt, prod_idx, dot_pos, la) in item_set:
            prods = aug_grammar.get(nt, [])
            if prod_idx >= len(prods):
                continue
            prod = prods[prod_idx]

            if dot_pos >= len(prod):
                # Reduce item
                if nt == "S'":
                    # Accept
                    if not row['$']:
                        row['$'] = 'acc'
                else:
                    # Reduce by this production — only on the lookahead terminal
                    pn = prod_num.get((nt, tuple(prod)), '?')
                    reduce_str = f"R{pn}"
                    if la in row and not row[la]:
                        row[la] = reduce_str
                    elif la in row and row[la] and row[la] != reduce_str:
                        # Conflict — append both
                        row[la] = f"{row[la]}/{reduce_str}"
            else:
                # Shift item
                next_sym = prod[dot_pos]
                key = (lalr_idx, next_sym)
                if key in lalr_transitions:
                    target = lalr_transitions[key]
                    if next_sym in TERMINALS:
                        shift_str = f"S{target}"
                        if next_sym in row and not row[next_sym]:
                            row[next_sym] = shift_str
                    elif next_sym in all_nts and next_sym != "S'":
                        if next_sym in row and not row[next_sym]:
                            row[next_sym] = str(target)

        table.append(row)

    # Build production reference list for display
    prod_ref = []
    for i, (nt, prod) in enumerate(prod_list):
        prod_ref.append({
            'number': i,
            'production': f"{nt} → {' '.join(prod)}"
        })

    # Limit table size for display (max 50 states)
    if len(table) > 50:
        table = table[:50]
        table.append({'State': '...', '$': f'({len(lalr_states) - 50} more states)'})

    # Attach production reference as metadata in the first row
    if table:
        table[0]['_productions'] = prod_ref
        table[0]['_action_cols'] = action_cols
        table[0]['_goto_cols'] = goto_cols

    return table


# ============================================================
#  Legacy static table (kept for backward compatibility)
# ============================================================

def generate_parsing_table():
    """Generate parsing table for default SELECT grammar."""
    return generate_parsing_table_for_query('SELECT')


# ============================================================
#  Relevant Non-Terminals — filter by query type
# ============================================================

def get_relevant_nonterminals(query_type):
    """
    Get the set of non-terminals relevant to a specific query type.
    This filters FIRST/FOLLOW display to only show relevant entries.
    """
    start_map = {
        'SELECT': 'select_stmt',
        'INSERT': 'insert_stmt',
        'UPDATE': 'update_stmt',
        'DELETE': 'delete_stmt',
        'CREATE': 'create_stmt',
    }
    start_nt = start_map.get(query_type, 'select_stmt')
    reachable = set()
    _find_reachable(start_nt, reachable)
    reachable.add('query')  # Always include top-level
    return reachable


# ============================================================
#  Formatted Display Functions
# ============================================================

def format_first_sets(first_sets=None, query_type=None):
    """Format FIRST sets as a list of dicts for UI display."""
    if first_sets is None:
        first_sets = compute_first_sets()

    # Filter to relevant non-terminals if query_type given
    relevant = None
    if query_type:
        relevant = get_relevant_nonterminals(query_type)

    result = []
    for nt in sorted(first_sets.keys()):
        if relevant and nt not in relevant:
            continue
        terminals = sorted(first_sets[nt])
        if not terminals:
            continue
        result.append({
            'non_terminal': nt,
            'first_set': '{ ' + ', '.join(terminals) + ' }'
        })
    return result


def format_follow_sets(follow_sets=None, query_type=None):
    """Format FOLLOW sets as a list of dicts for UI display."""
    if follow_sets is None:
        follow_sets = compute_follow_sets()

    # Filter to relevant non-terminals if query_type given
    relevant = None
    if query_type:
        relevant = get_relevant_nonterminals(query_type)

    result = []
    for nt in sorted(follow_sets.keys()):
        if relevant and nt not in relevant:
            continue
        terminals = sorted(follow_sets[nt])
        if not terminals:
            continue
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
                lines.append(f"{nt:<15} -> {' '.join(prod)}")
            else:
                lines.append(f"{'':<15} |  {' '.join(prod)}")
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
    print("DYNAMIC PARSING TABLE (SELECT)")
    print("=" * 60)
    table = generate_parsing_table_for_query('SELECT')
    for row in table:
        state = row.get('state', '')
        action = row.get('action', '')
        entries = {k: v for k, v in row.items() if k not in ('state', 'action')}
        print(f"  State {state}: {entries}  ({action})")

    print("\n" + "=" * 60)
    print("DYNAMIC PARSING TABLE (INSERT)")
    print("=" * 60)
    table = generate_parsing_table_for_query('INSERT')
    for row in table:
        state = row.get('state', '')
        action = row.get('action', '')
        entries = {k: v for k, v in row.items() if k not in ('state', 'action')}
        print(f"  State {state}: {entries}  ({action})")
