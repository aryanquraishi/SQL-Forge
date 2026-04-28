"""
symbol_table.py — Symbol Table Manager for Mini SQL Compiler
Tracks all identifiers: name, category (column/table/value), position, frequency, context.
Maps to Unit 1 (Lexical Analysis) and Unit 4 (Runtime Environment — Symbol Table).
"""


class SymbolEntry:
    """A single entry in the symbol table."""
    
    def __init__(self, name, category, position, context):
        self.name = name
        self.category = category        # 'COLUMN', 'TABLE', 'VALUE', 'CONDITION_FIELD'
        self.positions = [position]      # List of positions where this symbol appears
        self.frequency = 1
        self.contexts = [context]        # e.g., ['SELECT'], ['SELECT', 'WHERE']
        self.data_type = 'unknown'       # Inferred type: 'identifier', 'number', 'string'
    
    def add_occurrence(self, position, context):
        """Record another occurrence of this symbol."""
        self.positions.append(position)
        self.frequency += 1
        if context not in self.contexts:
            self.contexts.append(context)
    
    def to_dict(self):
        return {
            'name': self.name,
            'category': self.category,
            'first_position': self.positions[0],
            'all_positions': self.positions,
            'frequency': self.frequency,
            'contexts': self.contexts,
            'data_type': self.data_type
        }


class SymbolTable:
    """
    Symbol Table for the Mini SQL Compiler.
    Collects and categorizes all identifiers found during compilation.
    """
    
    def __init__(self):
        self.entries = {}   # name -> SymbolEntry
        self._order = []    # Preserve insertion order for display
    
    def add_symbol(self, name, category, position, context):
        """Add or update a symbol in the table."""
        key = name.lower()  # Case-insensitive matching
        
        if key in self.entries:
            self.entries[key].add_occurrence(position, context)
            # Update category if more specific info available
            if category in ('TABLE', 'CONDITION_FIELD') and self.entries[key].category == 'unknown':
                self.entries[key].category = category
        else:
            entry = SymbolEntry(name, category, position, context)
            self.entries[key] = entry
            self._order.append(key)
    
    def set_data_type(self, name, data_type):
        """Set the inferred data type for a symbol."""
        key = name.lower()
        if key in self.entries:
            self.entries[key].data_type = data_type
    
    def get_symbol(self, name):
        """Get a symbol entry by name."""
        return self.entries.get(name.lower())
    
    def get_all_entries(self):
        """Get all entries in insertion order."""
        return [self.entries[key] for key in self._order if key in self.entries]
    
    def get_columns(self):
        """Get all column identifiers."""
        return [e for e in self.get_all_entries() if e.category == 'COLUMN']
    
    def get_tables(self):
        """Get all table identifiers."""
        return [e for e in self.get_all_entries() if e.category == 'TABLE']
    
    def get_as_list(self):
        """Get symbol table as list of dicts for UI display."""
        result = []
        for entry in self.get_all_entries():
            result.append(entry.to_dict())
        return result
    
    def clear(self):
        """Clear the symbol table."""
        self.entries.clear()
        self._order.clear()
    
    def __len__(self):
        return len(self.entries)
    
    def __str__(self):
        lines = []
        lines.append(f"{'Name':<15} {'Category':<18} {'Type':<12} {'Freq':<6} {'Positions':<15} {'Contexts'}")
        lines.append("─" * 85)
        for entry in self.get_all_entries():
            positions_str = ", ".join(str(p) for p in entry.positions)
            contexts_str = ", ".join(entry.contexts)
            lines.append(
                f"{entry.name:<15} {entry.category:<18} {entry.data_type:<12} "
                f"{entry.frequency:<6} {positions_str:<15} {contexts_str}"
            )
        return "\n".join(lines)


def build_symbol_table_from_ast(ast_node, tokens=None):
    """
    Build a symbol table from the parsed AST.
    
    Args:
        ast_node: The AST dictionary from the parser
        tokens: Optional list of token dicts for position info
    
    Returns:
        SymbolTable instance
    """
    st = SymbolTable()
    
    if ast_node is None:
        return st
    
    query_type = ast_node.get('type', '')
    
    if query_type == 'SELECT':
        # Add column symbols
        columns = ast_node.get('columns', [])
        if isinstance(columns, list):
            for col in columns:
                if col != '*':
                    pos = _find_token_position(tokens, col) if tokens else 0
                    st.add_symbol(col, 'COLUMN', pos, 'SELECT')
                    st.set_data_type(col, 'identifier')
        
        # Add table symbol
        table = ast_node.get('table', '')
        if table:
            pos = _find_token_position(tokens, table) if tokens else 0
            st.add_symbol(table, 'TABLE', pos, 'FROM')
            st.set_data_type(table, 'identifier')
        
        # Add condition symbols
        condition = ast_node.get('condition', None)
        if condition:
            _extract_condition_symbols(st, condition, tokens)
    
    elif query_type == 'INSERT':
        # Add table symbol
        table = ast_node.get('table', '')
        if table:
            pos = _find_token_position(tokens, table) if tokens else 0
            st.add_symbol(table, 'TABLE', pos, 'INSERT')
            st.set_data_type(table, 'identifier')
        
        # Add value symbols
        values = ast_node.get('values', [])
        for val in values:
            if isinstance(val, str) and not val.startswith("'"):
                pos = _find_token_position(tokens, val) if tokens else 0
                st.add_symbol(val, 'VALUE', pos, 'VALUES')
    
    return st


def _extract_condition_symbols(symbol_table, condition, tokens):
    """Extract symbols from a WHERE condition."""
    if condition is None:
        return
    
    cond_type = condition.get('type', '')
    
    if cond_type in ('AND', 'OR'):
        _extract_condition_symbols(symbol_table, condition.get('left'), tokens)
        _extract_condition_symbols(symbol_table, condition.get('right'), tokens)
    elif cond_type == 'COMPARISON':
        left = condition.get('left', '')
        right = condition.get('right', '')
        
        if isinstance(left, str) and not left.replace('.', '').isdigit() and not left.startswith("'"):
            pos = _find_token_position(tokens, left) if tokens else 0
            symbol_table.add_symbol(left, 'CONDITION_FIELD', pos, 'WHERE')
            symbol_table.set_data_type(left, 'identifier')
        
        if isinstance(right, str) and not right.replace('.', '').isdigit() and not right.startswith("'"):
            pos = _find_token_position(tokens, right) if tokens else 0
            symbol_table.add_symbol(right, 'VALUE', pos, 'WHERE')
            symbol_table.set_data_type(right, 'identifier')


def _find_token_position(tokens, value):
    """Find the position of a token value in the token list."""
    if tokens is None:
        return 0
    for tok in tokens:
        if not isinstance(tok, dict):
            continue
        if str(tok.get('value', '')).lower() == str(value).lower():
            return tok.get('position', 0)
    return 0
