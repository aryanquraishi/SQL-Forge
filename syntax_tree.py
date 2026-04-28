"""
syntax_tree.py — Parse Tree Node Class and Tree Builder
Builds visual parse tree from AST output of the parser.

Syllabus Mapping:
  - Unit 3: Construction of Syntax Trees
  - Unit 3: Synthesized and Inherited Attributes
  - Unit 3: Dependency Graph
"""


class TreeNode:
    """
    A node in the parse tree.
    
    Attributes:
        name (str): Node label (e.g., "QUERY", "SELECT", "CONDITION")
        children (list): List of child TreeNode objects
        value (str): Leaf value (e.g., "name", "18") — None for internal nodes
    """
    
    def __init__(self, name, children=None, value=None):
        self.name = name
        self.children = children or []
        self.value = value
    
    def add_child(self, child):
        """Add a child node."""
        if isinstance(child, TreeNode):
            self.children.append(child)
        else:
            # Auto-wrap string values as leaf nodes
            self.children.append(TreeNode(str(child), value=str(child)))
    
    def is_leaf(self):
        """Check if this is a leaf node (no children)."""
        return len(self.children) == 0
    
    def __repr__(self):
        if self.value:
            return f"TreeNode({self.name}={self.value})"
        return f"TreeNode({self.name}, children={len(self.children)})"


def build_tree_from_ast(ast_node):
    """
    Build a TreeNode tree from the parser's AST dictionary.
    
    Args:
        ast_node (dict): AST dictionary from parser
    
    Returns:
        TreeNode: Root of the parse tree
    """
    if ast_node is None:
        return TreeNode("EMPTY")
    
    query_type = ast_node.get('type', 'UNKNOWN')
    
    if query_type == 'SELECT':
        return _build_select_tree(ast_node)
    elif query_type == 'INSERT':
        return _build_insert_tree(ast_node)
    else:
        return TreeNode("QUERY", value=str(ast_node))


def _build_select_tree(ast_node):
    """Build parse tree for SELECT statement."""
    root = TreeNode("QUERY")
    
    # SELECT clause
    select_node = TreeNode("SELECT")
    columns = ast_node.get('columns', [])
    
    if columns == ['*']:
        select_node.add_child(TreeNode("*", value="*"))
    else:
        columns_node = TreeNode("COLUMNS")
        for col in columns:
            columns_node.add_child(TreeNode(str(col), value=str(col)))
        select_node.add_child(columns_node)
    
    root.add_child(select_node)
    
    # FROM clause
    from_node = TreeNode("FROM")
    table = ast_node.get('table', '')
    from_node.add_child(TreeNode(str(table), value=str(table)))
    root.add_child(from_node)
    
    # WHERE clause (optional)
    condition = ast_node.get('condition', None)
    if condition:
        where_node = TreeNode("WHERE")
        condition_tree = _build_condition_tree(condition)
        where_node.add_child(condition_tree)
        root.add_child(where_node)
    
    return root


def _build_insert_tree(ast_node):
    """Build parse tree for INSERT statement."""
    root = TreeNode("QUERY")
    
    # INSERT INTO clause
    insert_node = TreeNode("INSERT INTO")
    table = ast_node.get('table', '')
    insert_node.add_child(TreeNode(str(table), value=str(table)))
    root.add_child(insert_node)
    
    # VALUES clause
    values_node = TreeNode("VALUES")
    values = ast_node.get('values', [])
    for val in values:
        values_node.add_child(TreeNode(str(val), value=str(val)))
    root.add_child(values_node)
    
    return root


def _build_condition_tree(condition):
    """Build parse tree for a WHERE condition (recursive for AND/OR)."""
    if condition is None:
        return TreeNode("EMPTY")
    
    cond_type = condition.get('type', '')
    
    if cond_type in ('AND', 'OR'):
        # Logical operator — two sub-conditions
        logic_node = TreeNode(cond_type)
        left_tree = _build_condition_tree(condition.get('left'))
        right_tree = _build_condition_tree(condition.get('right'))
        logic_node.add_child(left_tree)
        logic_node.add_child(right_tree)
        return logic_node
    
    elif cond_type == 'COMPARISON':
        # Simple comparison: left OP right
        comp_node = TreeNode("CONDITION")
        comp_node.add_child(TreeNode(str(condition.get('left', '')), value=str(condition.get('left', ''))))
        comp_node.add_child(TreeNode(str(condition.get('operator', '')), value=str(condition.get('operator', ''))))
        comp_node.add_child(TreeNode(str(condition.get('right', '')), value=str(condition.get('right', ''))))
        return comp_node
    
    else:
        return TreeNode("CONDITION", value=str(condition))


# ============================================================
#  Tree Display — Formatted text output with connectors
# ============================================================

def tree_to_string(node, prefix="", is_last=True, is_root=True):
    """
    Convert a TreeNode to a formatted string with tree connectors.
    
    Args:
        node (TreeNode): The node to display
        prefix (str): Current line prefix for indentation
        is_last (bool): Whether this is the last child
        is_root (bool): Whether this is the root node
    
    Returns:
        str: Formatted tree string
    
    Example Output:
        QUERY
        ├── SELECT
        │   ├── name
        │   └── age
        ├── FROM
        │   └── students
        └── WHERE
            └── CONDITION
                ├── age
                ├── >
                └── 18
    """
    lines = []
    
    # Current node display
    if is_root:
        connector = ""
        new_prefix = ""
    else:
        connector = "└── " if is_last else "├── "
        new_prefix = prefix + ("    " if is_last else "│   ")
    
    # Node label
    if node.value and node.name == node.value:
        label = node.name
    elif node.value:
        label = f"{node.name}: {node.value}"
    else:
        label = node.name
    
    lines.append(f"{prefix}{connector}{label}")
    
    # Children
    for i, child in enumerate(node.children):
        is_child_last = (i == len(node.children) - 1)
        child_str = tree_to_string(child, new_prefix, is_child_last, is_root=False)
        lines.append(child_str)
    
    return "\n".join(lines)


def tree_to_dict(node):
    """
    Convert a TreeNode to a nested dictionary for JSON/display.
    
    Args:
        node (TreeNode): The node to convert
    
    Returns:
        dict: Nested dictionary representation
    """
    result = {
        'name': node.name,
        'value': node.value,
        'children': []
    }
    
    for child in node.children:
        result['children'].append(tree_to_dict(child))
    
    return result


def get_tree_depth(node):
    """Get the depth of the tree."""
    if node.is_leaf():
        return 1
    return 1 + max(get_tree_depth(child) for child in node.children)


def get_tree_node_count(node):
    """Get total number of nodes in the tree."""
    count = 1
    for child in node.children:
        count += get_tree_node_count(child)
    return count


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
            'type': 'COMPARISON',
            'left': 'age',
            'operator': '>',
            'right': 18
        }
    }
    
    tree = build_tree_from_ast(sample_ast)
    print(tree_to_string(tree))
    print(f"\nTree depth: {get_tree_depth(tree)}")
    print(f"Total nodes: {get_tree_node_count(tree)}")
