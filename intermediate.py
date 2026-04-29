"""
intermediate.py — Intermediate Code Generation for Mini SQL Compiler
Generates Postfix Notation, Three Address Code (TAC), Quadruples, and Triples.

Supports ADVANCED AST: JOINs, aliases, dot notation, ORDER BY, GROUP BY, HAVING, DISTINCT, aggregates.

Syllabus Mapping:
  - Unit 3: Postfix Notation
  - Unit 3: Three Address Codes
  - Unit 3: Quadruples, Triples and Indirect Triples
  - Unit 3: Translation of Assignment Statements
  - Unit 3: Boolean Expression
"""


# ============================================================
#  Postfix Notation Generator
#  Converts infix WHERE conditions to postfix (Reverse Polish Notation)
# ============================================================

def generate_postfix(condition):
    """
    Convert a WHERE condition from infix to postfix notation.
    
    Args:
        condition (dict): Condition AST from parser
    
    Returns:
        str: Postfix notation string
    
    Example:
        Input:  s.age > 18 AND c.course_name = 'Compiler Design'
        Output: s.age 18 > c.course_name 'Compiler Design' = AND
    """
    if condition is None:
        return ""
    
    tokens = []
    _condition_to_postfix(condition, tokens)
    return " ".join(str(t) for t in tokens)


def _condition_to_postfix(condition, tokens):
    """Recursively convert condition to postfix tokens."""
    if condition is None:
        return
    
    cond_type = condition.get('type', '')
    
    if cond_type in ('AND', 'OR'):
        # Process left operand
        _condition_to_postfix(condition.get('left'), tokens)
        # Process right operand
        _condition_to_postfix(condition.get('right'), tokens)
        # Add operator (postfix = operands first, then operator)
        tokens.append(cond_type)
    
    elif cond_type == 'COMPARISON':
        # Simple comparison: left op right → left right op
        tokens.append(str(condition.get('left', '')))
        tokens.append(str(condition.get('right', '')))
        tokens.append(str(condition.get('operator', '')))


def get_postfix_steps(condition):
    """
    Get step-by-step postfix conversion for display.
    """
    if condition is None:
        return []
    
    steps = []
    infix = _condition_to_infix(condition)
    postfix = generate_postfix(condition)
    
    steps.append({
        'step': 1,
        'description': 'Original infix expression',
        'expression': infix
    })
    
    # Show intermediate steps based on condition complexity
    if condition.get('type') in ('AND', 'OR'):
        left_postfix = generate_postfix(condition.get('left'))
        right_postfix = generate_postfix(condition.get('right'))
        
        steps.append({
            'step': 2,
            'description': f"Convert left sub-expression to postfix",
            'expression': left_postfix
        })
        steps.append({
            'step': 3,
            'description': f"Convert right sub-expression to postfix",
            'expression': right_postfix
        })
        steps.append({
            'step': 4,
            'description': f"Combine with {condition.get('type')} operator",
            'expression': postfix
        })
    else:
        steps.append({
            'step': 2,
            'description': 'Move operator after operands (postfix)',
            'expression': postfix
        })
    
    return steps


def _condition_to_infix(condition):
    """Convert condition AST back to infix string."""
    if condition is None:
        return ""
    
    cond_type = condition.get('type', '')
    
    if cond_type in ('AND', 'OR'):
        left = _condition_to_infix(condition.get('left'))
        right = _condition_to_infix(condition.get('right'))
        return f"{left} {cond_type} {right}"
    elif cond_type == 'COMPARISON':
        return f"{condition.get('left')} {condition.get('operator')} {condition.get('right')}"
    return str(condition)


# ============================================================
#  Three Address Code (TAC) Generator
#  Generates three-address code representation
# ============================================================

class TACGenerator:
    """
    Generates Three Address Code from the parsed AST.
    
    Supports advanced SELECT with JOIN, ORDER BY, GROUP BY, HAVING, DISTINCT.
    """
    
    def __init__(self):
        self.temp_counter = 0
        self.instructions = []
    
    def reset(self):
        """Reset for new generation."""
        self.temp_counter = 0
        self.instructions = []
    
    def new_temp(self):
        """Generate a new temporary variable name."""
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def generate(self, ast_node):
        """
        Generate TAC from AST.
        
        Args:
            ast_node (dict): AST from parser
        
        Returns:
            list: List of TAC instruction dicts
        """
        self.reset()
        
        if ast_node is None:
            return []
        
        query_type = ast_node.get('type', '')
        
        if query_type == 'SELECT':
            self._generate_select(ast_node)
        elif query_type == 'INSERT':
            self._generate_insert(ast_node)
        
        return self.instructions
    
    def _get_col_str(self, columns):
        """Get column string from column list (handles dicts and strings)."""
        parts = []
        for col in columns:
            if isinstance(col, dict):
                expr = col.get('expr', str(col))
                alias = col.get('alias')
                if alias:
                    parts.append(f"{expr} AS {alias}")
                else:
                    parts.append(str(expr))
            else:
                parts.append(str(col))
        return ", ".join(parts)
    
    def _get_table_str(self, table):
        """Get table string from table ref (handles dicts and strings)."""
        if isinstance(table, dict):
            name = table.get('name', '')
            alias = table.get('alias', '')
            if alias:
                return f"{name} {alias}"
            return name
        return str(table)
    
    def _generate_select(self, ast_node):
        """Generate TAC for SELECT statement (advanced)."""
        columns = ast_node.get('columns', [])
        table = ast_node.get('table', '')
        condition = ast_node.get('condition', None)
        group_by = ast_node.get('group_by', None)
        having = ast_node.get('having', None)
        order_by = ast_node.get('order_by', None)
        distinct = ast_node.get('distinct', False)
        
        # Generate condition TAC first (if exists)
        cond_temp = None
        if condition:
            cond_temp = self._generate_condition(condition)
        
        # Column list
        col_str = self._get_col_str(columns)
        table_str = self._get_table_str(table)
        
        # DISTINCT prefix
        select_kw = "SELECT DISTINCT" if distinct else "SELECT"
        
        # SELECT instruction
        select_temp = self.new_temp()
        self.instructions.append({
            'result': select_temp,
            'op': select_kw,
            'arg1': col_str,
            'arg2': table_str,
            'code': f"{select_temp} = {select_kw} {col_str} FROM {table_str}"
        })
        
        current_temp = select_temp
        
        # JOIN instructions
        joins = []
        if isinstance(table, dict):
            joins = table.get('joins', [])
        
        for join in joins:
            jtable_str = self._get_table_str(join.get('table', {}))
            on_cond = join.get('on', {})
            on_left = on_cond.get('left', '')
            on_right = on_cond.get('right', '')
            
            join_temp = self.new_temp()
            self.instructions.append({
                'result': join_temp,
                'op': 'JOIN',
                'arg1': current_temp,
                'arg2': jtable_str,
                'code': f"{join_temp} = {current_temp} JOIN {jtable_str} ON {on_left} = {on_right}"
            })
            current_temp = join_temp
        
        # Apply WHERE filter if exists
        if cond_temp:
            filter_temp = self.new_temp()
            self.instructions.append({
                'result': filter_temp,
                'op': 'FILTER',
                'arg1': current_temp,
                'arg2': cond_temp,
                'code': f"{filter_temp} = {current_temp} WHERE {cond_temp}"
            })
            current_temp = filter_temp
        
        # GROUP BY
        if group_by:
            group_str = ", ".join(str(g) for g in group_by)
            group_temp = self.new_temp()
            self.instructions.append({
                'result': group_temp,
                'op': 'GROUP',
                'arg1': current_temp,
                'arg2': group_str,
                'code': f"{group_temp} = {current_temp} GROUP BY {group_str}"
            })
            current_temp = group_temp
        
        # HAVING
        if having:
            having_temp = self._generate_condition(having)
            having_filter = self.new_temp()
            self.instructions.append({
                'result': having_filter,
                'op': 'HAVING',
                'arg1': current_temp,
                'arg2': having_temp,
                'code': f"{having_filter} = {current_temp} HAVING {having_temp}"
            })
            current_temp = having_filter
        
        # ORDER BY
        if order_by:
            order_parts = []
            for item in order_by:
                if isinstance(item, dict):
                    order_parts.append(f"{item.get('column', '')} {item.get('direction', 'ASC')}")
                else:
                    order_parts.append(str(item))
            order_str = ", ".join(order_parts)
            order_temp = self.new_temp()
            self.instructions.append({
                'result': order_temp,
                'op': 'ORDER',
                'arg1': current_temp,
                'arg2': order_str,
                'code': f"{order_temp} = {current_temp} ORDER BY {order_str}"
            })
            current_temp = order_temp
        
        # Final result
        self.instructions.append({
            'result': 'result',
            'op': '=',
            'arg1': current_temp,
            'arg2': '',
            'code': f"result = {current_temp}"
        })
    
    def _generate_insert(self, ast_node):
        """Generate TAC for INSERT statement."""
        table = ast_node.get('table', '')
        values = ast_node.get('values', [])
        
        val_str = ", ".join(str(v) for v in values)
        
        # Create tuple
        tuple_temp = self.new_temp()
        self.instructions.append({
            'result': tuple_temp,
            'op': 'TUPLE',
            'arg1': val_str,
            'arg2': '',
            'code': f"{tuple_temp} = ({val_str})"
        })
        
        # INSERT instruction
        insert_temp = self.new_temp()
        self.instructions.append({
            'result': insert_temp,
            'op': 'INSERT',
            'arg1': table,
            'arg2': tuple_temp,
            'code': f"{insert_temp} = INSERT INTO {table} VALUES {tuple_temp}"
        })
        
        # Final result
        self.instructions.append({
            'result': 'result',
            'op': '=',
            'arg1': insert_temp,
            'arg2': '',
            'code': f"result = {insert_temp}"
        })
    
    def _generate_condition(self, condition):
        """Generate TAC for a condition expression. Returns temp variable name."""
        if condition is None:
            return None
        
        cond_type = condition.get('type', '')
        
        if cond_type in ('AND', 'OR'):
            left_temp = self._generate_condition(condition.get('left'))
            right_temp = self._generate_condition(condition.get('right'))
            
            result_temp = self.new_temp()
            self.instructions.append({
                'result': result_temp,
                'op': cond_type,
                'arg1': left_temp,
                'arg2': right_temp,
                'code': f"{result_temp} = {left_temp} {cond_type} {right_temp}"
            })
            return result_temp
        
        elif cond_type == 'COMPARISON':
            left = str(condition.get('left', ''))
            op = str(condition.get('operator', ''))
            right = str(condition.get('right', ''))
            
            result_temp = self.new_temp()
            self.instructions.append({
                'result': result_temp,
                'op': op,
                'arg1': left,
                'arg2': right,
                'code': f"{result_temp} = {left} {op} {right}"
            })
            return result_temp
        
        return None
    
    def get_tac_string(self):
        """Get TAC as formatted string."""
        return "\n".join(f"  {inst['code']}" for inst in self.instructions)


# ============================================================
#  Quadruples Generator
#  Converts TAC to (Operator, Arg1, Arg2, Result) format
# ============================================================

def generate_quadruples(tac_instructions):
    """
    Convert TAC instructions to Quadruples format.
    Format: (Operator, Arg1, Arg2, Result)
    """
    quadruples = []
    
    for i, inst in enumerate(tac_instructions):
        quad = {
            'index': i + 1,
            'operator': inst.get('op', ''),
            'arg1': inst.get('arg1', ''),
            'arg2': inst.get('arg2', ''),
            'result': inst.get('result', ''),
        }
        quadruples.append(quad)
    
    return quadruples


def generate_triples(tac_instructions):
    """
    Convert TAC instructions to Triples format.
    Format: (Index, Operator, Arg1, Arg2)
    Unlike quadruples, triples use the index as the implicit result reference.
    """
    triples = []
    
    # Map temp variables to triple indices
    temp_to_index = {}
    
    for i, inst in enumerate(tac_instructions):
        result = inst.get('result', '')
        arg1 = inst.get('arg1', '')
        arg2 = inst.get('arg2', '')
        
        # Replace temp references with triple indices
        if arg1 in temp_to_index:
            arg1 = f"({temp_to_index[arg1]})"
        if arg2 in temp_to_index:
            arg2 = f"({temp_to_index[arg2]})"
        
        triple = {
            'index': i + 1,
            'operator': inst.get('op', ''),
            'arg1': arg1,
            'arg2': arg2,
        }
        triples.append(triple)
        
        # Track temp variable → index mapping
        if result.startswith('t'):
            temp_to_index[result] = i + 1
    
    return triples


# ============================================================
#  Module test
# ============================================================
if __name__ == '__main__':
    # Test with an advanced AST
    sample_ast = {
        'type': 'SELECT',
        'distinct': False,
        'columns': [
            {'expr': 's.name', 'alias': None},
            {'expr': 'AVG(s.marks)', 'alias': 'avg_marks', 'is_agg': True},
        ],
        'table': {
            'name': 'students',
            'alias': 's',
            'joins': [
                {
                    'type': 'JOIN',
                    'table': {'name': 'courses', 'alias': 'c', 'joins': []},
                    'on': {'type': 'JOIN_COND', 'left': 's.course_id', 'right': 'c.course_id'},
                }
            ],
        },
        'condition': {
            'type': 'AND',
            'left': {
                'type': 'COMPARISON',
                'left': 's.age',
                'operator': '>',
                'right': 18
            },
            'right': {
                'type': 'COMPARISON',
                'left': 'c.name',
                'operator': '=',
                'right': "'CS'"
            }
        },
        'group_by': ['c.name'],
        'having': {
            'type': 'COMPARISON',
            'left': 'AVG(s.marks)',
            'operator': '>',
            'right': 60,
        },
        'order_by': [
            {'column': 's.name', 'direction': 'ASC'},
        ],
    }
    
    # Postfix
    print("=" * 60)
    print("POSTFIX NOTATION")
    print("=" * 60)
    postfix = generate_postfix(sample_ast['condition'])
    print(f"  {postfix}")
    
    # Three Address Code
    print("\n" + "=" * 60)
    print("THREE ADDRESS CODE")
    print("=" * 60)
    tac_gen = TACGenerator()
    tac = tac_gen.generate(sample_ast)
    print(tac_gen.get_tac_string())
    
    # Quadruples
    print("\n" + "=" * 60)
    print("QUADRUPLES")
    print("=" * 60)
    quads = generate_quadruples(tac)
    print(f"  {'#':<4} {'Operator':<12} {'Arg1':<25} {'Arg2':<20} {'Result':<10}")
    print("  " + "─" * 71)
    for q in quads:
        print(f"  {q['index']:<4} {q['operator']:<12} {str(q['arg1']):<25} {str(q['arg2']):<20} {q['result']:<10}")
    
    # Triples
    print("\n" + "=" * 60)
    print("TRIPLES")
    print("=" * 60)
    trips = generate_triples(tac)
    print(f"  {'#':<4} {'Operator':<12} {'Arg1':<25} {'Arg2':<20}")
    print("  " + "─" * 61)
    for t in trips:
        print(f"  {t['index']:<4} {t['operator']:<12} {str(t['arg1']):<25} {str(t['arg2']):<20}")
