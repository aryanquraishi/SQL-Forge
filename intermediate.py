"""
intermediate.py — Intermediate Code Generation for Mini SQL Compiler
Generates Postfix Notation, Three Address Code (TAC), and Quadruples.

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
            e.g., {'type': 'COMPARISON', 'left': 'age', 'operator': '>', 'right': 18}
    
    Returns:
        str: Postfix notation string
    
    Example:
        Input:  age > 18 AND department = 'CS'
        Output: age 18 > department 'CS' = AND
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
    
    Returns:
        list: List of step dicts showing the conversion process
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
    
    Three Address Code format:
        t1 = age > 18
        t2 = SELECT name FROM students
        t3 = t2 WHERE t1
        result = t3
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
    
    def _generate_select(self, ast_node):
        """Generate TAC for SELECT statement."""
        columns = ast_node.get('columns', [])
        table = ast_node.get('table', '')
        condition = ast_node.get('condition', None)
        
        # Generate condition TAC first (if exists)
        cond_temp = None
        if condition:
            cond_temp = self._generate_condition(condition)
        
        # Column list
        col_str = ", ".join(str(c) for c in columns)
        
        # SELECT instruction
        select_temp = self.new_temp()
        self.instructions.append({
            'result': select_temp,
            'op': 'SELECT',
            'arg1': col_str,
            'arg2': table,
            'code': f"{select_temp} = SELECT {col_str} FROM {table}"
        })
        
        # Apply WHERE filter if exists
        if cond_temp:
            filter_temp = self.new_temp()
            self.instructions.append({
                'result': filter_temp,
                'op': 'FILTER',
                'arg1': select_temp,
                'arg2': cond_temp,
                'code': f"{filter_temp} = {select_temp} WHERE {cond_temp}"
            })
            # Final result
            self.instructions.append({
                'result': 'result',
                'op': '=',
                'arg1': filter_temp,
                'arg2': '',
                'code': f"result = {filter_temp}"
            })
        else:
            # No WHERE, result is the SELECT directly
            self.instructions.append({
                'result': 'result',
                'op': '=',
                'arg1': select_temp,
                'arg2': '',
                'code': f"result = {select_temp}"
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
    
    Args:
        tac_instructions (list): TAC instruction dicts from TACGenerator
    
    Returns:
        list: List of quadruple dicts
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
    
    Args:
        tac_instructions (list): TAC instruction dicts from TACGenerator
    
    Returns:
        list: List of triple dicts
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
    # Test with a sample AST
    sample_ast = {
        'type': 'SELECT',
        'columns': ['name', 'age'],
        'table': 'students',
        'condition': {
            'type': 'AND',
            'left': {
                'type': 'COMPARISON',
                'left': 'age',
                'operator': '>',
                'right': 18
            },
            'right': {
                'type': 'COMPARISON',
                'left': 'dept',
                'operator': '=',
                'right': "'CS'"
            }
        }
    }
    
    # Postfix
    print("=" * 60)
    print("POSTFIX NOTATION")
    print("=" * 60)
    postfix = generate_postfix(sample_ast['condition'])
    print(f"  {postfix}")
    
    print("\nPostfix Steps:")
    for step in get_postfix_steps(sample_ast['condition']):
        print(f"  Step {step['step']}: {step['description']}")
        print(f"         {step['expression']}")
    
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
    print(f"  {'#':<4} {'Operator':<10} {'Arg1':<15} {'Arg2':<15} {'Result':<10}")
    print("  " + "─" * 54)
    for q in quads:
        print(f"  {q['index']:<4} {q['operator']:<10} {q['arg1']:<15} {q['arg2']:<15} {q['result']:<10}")
    
    # Triples
    print("\n" + "=" * 60)
    print("TRIPLES")
    print("=" * 60)
    trips = generate_triples(tac)
    print(f"  {'#':<4} {'Operator':<10} {'Arg1':<15} {'Arg2':<15}")
    print("  " + "─" * 44)
    for t in trips:
        print(f"  {t['index']:<4} {t['operator']:<10} {t['arg1']:<15} {t['arg2']:<15}")
