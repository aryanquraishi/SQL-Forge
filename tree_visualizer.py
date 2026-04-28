"""
tree_visualizer.py — Graphical Parse Tree Renderer
Generates beautiful SVG-based parse tree with colored nodes and connecting lines.
Renders inside Streamlit via st.components.v1.html()
"""


# ============================================================
#  Color Scheme for Node Types
# ============================================================
NODE_COLORS = {
    'QUERY':     {'fill': '#D4691E', 'stroke': '#A84D12', 'text': '#FFFFFF'},  # Amber - root
    'SELECT':    {'fill': '#B45309', 'stroke': '#92400E', 'text': '#FFFFFF'},  # Deep amber - clause
    'FROM':      {'fill': '#B45309', 'stroke': '#92400E', 'text': '#FFFFFF'},  # Deep amber - clause
    'WHERE':     {'fill': '#B45309', 'stroke': '#92400E', 'text': '#FFFFFF'},  # Deep amber - clause
    'INSERT INTO': {'fill': '#B45309', 'stroke': '#92400E', 'text': '#FFFFFF'},
    'VALUES':    {'fill': '#B45309', 'stroke': '#92400E', 'text': '#FFFFFF'},
    'COLUMNS':   {'fill': '#78716C', 'stroke': '#57534E', 'text': '#FFFFFF'},  # Neutral - group
    'CONDITION': {'fill': '#78716C', 'stroke': '#57534E', 'text': '#FFFFFF'},  # Neutral - condition
    'AND':       {'fill': '#78716C', 'stroke': '#57534E', 'text': '#FFFFFF'},  # Neutral - logic
    'OR':        {'fill': '#78716C', 'stroke': '#57534E', 'text': '#FFFFFF'},  # Neutral - logic
    '_LEAF':     {'fill': '#44403C', 'stroke': '#292524', 'text': '#FFFFFF'},  # Dark stone - leaf
    '_OPERATOR': {'fill': '#E8894A', 'stroke': '#D4691E', 'text': '#1F2937'},  # Light amber - operators
    '_DEFAULT':  {'fill': '#57534E', 'stroke': '#44403C', 'text': '#FFFFFF'},  # Stone - default
}

OPERATORS = {'>', '<', '=', '>=', '<=', '!=', '+', '-', '*', '/'}


def _get_node_color(node):
    """Get color scheme for a node based on its type."""
    name = node.name
    if name in NODE_COLORS:
        return NODE_COLORS[name]
    if name in OPERATORS:
        return NODE_COLORS['_OPERATOR']
    if node.is_leaf():
        return NODE_COLORS['_LEAF']
    return NODE_COLORS['_DEFAULT']


# ============================================================
#  Tree Layout Algorithm — Assign (x, y) to each node
# ============================================================

class LayoutNode:
    """A node with position info for rendering."""
    def __init__(self, name, x=0, y=0, children=None, is_leaf=False, colors=None):
        self.name = name
        self.x = x
        self.y = y
        self.children = children or []
        self.is_leaf = is_leaf
        self.colors = colors or NODE_COLORS['_DEFAULT']


def _compute_subtree_width(node):
    """Recursively compute the width (number of leaf-level slots) needed."""
    if node.is_leaf() or len(node.children) == 0:
        return 1
    total = 0
    for child in node.children:
        total += _compute_subtree_width(child)
    return total


def _layout_tree(node, depth=0, left_offset=0, h_spacing=100, v_spacing=90):
    """
    Recursively assign positions to each node.
    Returns a LayoutNode with (x, y) and children.
    """
    colors = _get_node_color(node)
    
    if node.is_leaf() or len(node.children) == 0:
        lnode = LayoutNode(
            name=node.name,
            x=left_offset * h_spacing,
            y=depth * v_spacing,
            is_leaf=True,
            colors=colors
        )
        return lnode, 1  # width = 1
    
    layout_children = []
    current_offset = left_offset
    total_width = 0
    
    for child in node.children:
        lchild, w = _layout_tree(child, depth + 1, current_offset, h_spacing, v_spacing)
        layout_children.append(lchild)
        current_offset += w
        total_width += w
    
    # Center the parent above its children
    if layout_children:
        first_x = layout_children[0].x
        last_x = layout_children[-1].x
        center_x = (first_x + last_x) / 2
    else:
        center_x = left_offset * h_spacing
    
    lnode = LayoutNode(
        name=node.name,
        x=center_x,
        y=depth * v_spacing,
        children=layout_children,
        is_leaf=False,
        colors=colors
    )
    
    return lnode, total_width


# ============================================================
#  SVG Renderer — Generate SVG string
# ============================================================

def _collect_all_nodes(lnode, nodes=None, edges=None):
    """Collect all nodes and edges for rendering."""
    if nodes is None:
        nodes = []
    if edges is None:
        edges = []
    
    nodes.append(lnode)
    
    for child in lnode.children:
        edges.append((lnode, child))
        _collect_all_nodes(child, nodes, edges)
    
    return nodes, edges


def generate_tree_svg(tree_node):
    """
    Generate an SVG string for the parse tree.
    
    Args:
        tree_node: TreeNode from syntax_tree.py
    
    Returns:
        str: SVG markup string
    """
    if tree_node is None:
        return "<p>No tree to display</p>"
    
    # Layout the tree
    layout_root, total_width = _layout_tree(tree_node, depth=0, left_offset=0, h_spacing=110, v_spacing=100)
    
    # Collect all nodes and edges
    all_nodes, all_edges = _collect_all_nodes(layout_root)
    
    # Calculate SVG dimensions
    if not all_nodes:
        return "<p>Empty tree</p>"
    
    padding = 70
    node_radius = 32
    
    min_x = min(n.x for n in all_nodes)
    max_x = max(n.x for n in all_nodes)
    max_y = max(n.y for n in all_nodes)
    
    # Shift all nodes so min_x starts at padding
    x_shift = padding - min_x
    for n in all_nodes:
        n.x += x_shift
    
    svg_width = max(max_x - min_x + 2 * padding + 60, 400)
    svg_height = max_y + 2 * padding + 20
    
    # Start building SVG
    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" style="font-family: 'Inter', 'Segoe UI', sans-serif;">''')
    
    # Defs — drop shadow, glow, arrow markers
    svg_parts.append('''
    <defs>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="rgba(0,0,0,0.3)"/>
        </filter>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 8 3, 0 6" fill="#78716C"/>
        </marker>
    </defs>
    ''')
    
    # Background
    svg_parts.append(f'''<rect width="{svg_width}" height="{svg_height}" rx="12" fill="transparent"/>''')
    
    # Draw edges (lines from parent to child)
    for parent, child in all_edges:
        px, py = parent.x, parent.y + padding
        cx, cy = child.x, child.y + padding
        
        # Curved line using quadratic bezier
        mid_y = (py + cy) / 2
        svg_parts.append(
            f'<path d="M {px} {py + node_radius} Q {px} {mid_y}, {cx} {cy - node_radius}" '
            f'fill="none" stroke="#A8A29E" stroke-width="1.5" stroke-dasharray="none" '
            f'marker-end="url(#arrowhead)"/>'
        )
    
    # Draw nodes (circles with labels)
    for node in all_nodes:
        nx, ny = node.x, node.y + padding
        colors = node.colors
        fill = colors['fill']
        stroke = colors['stroke']
        text_color = colors['text']
        
        # Determine radius based on text length
        label = node.name
        if len(label) > 8:
            r = 38
        elif len(label) > 5:
            r = 35
        else:
            r = node_radius
        
        # Outer glow
        svg_parts.append(
            f'<circle cx="{nx}" cy="{ny}" r="{r + 4}" fill="none" '
            f'stroke="{fill}" stroke-width="1" opacity="0.3"/>'
        )
        
        # Main circle
        svg_parts.append(
            f'<circle cx="{nx}" cy="{ny}" r="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="2.5" filter="url(#shadow)" '
            f'style="cursor:pointer;"/>'
        )
        
        # Inner highlight
        svg_parts.append(
            f'<circle cx="{nx}" cy="{ny - r*0.3}" r="{r * 0.6}" '
            f'fill="url(#)" opacity="0.1" fill="white"/>'
        )
        
        # Label text
        font_size = 11 if len(label) > 6 else 13
        if len(label) > 10:
            font_size = 9
        
        svg_parts.append(
            f'<text x="{nx}" y="{ny + 1}" text-anchor="middle" dominant-baseline="middle" '
            f'fill="{text_color}" font-size="{font_size}" font-weight="600" '
            f'style="pointer-events:none;">{label}</text>'
        )
        
        # Type label below leaf nodes
        if node.is_leaf:
            type_label = "leaf"
            if label in OPERATORS:
                type_label = "operator"
            elif label == '*':
                type_label = "wildcard"
            elif label.startswith("'"):
                type_label = "string"
            elif label.replace('.', '').isdigit():
                type_label = "number"
            else:
                type_label = "identifier"
            
            svg_parts.append(
                f'<text x="{nx}" y="{ny + r + 16}" text-anchor="middle" '
                f'fill="#A8A29E" font-size="9" font-style="italic">{type_label}</text>'
            )
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)


def generate_tree_html(tree_node):
    """
    Generate complete HTML with the SVG tree for Streamlit embedding.
    
    Args:
        tree_node: TreeNode from syntax_tree.py
    
    Returns:
        str: Complete HTML string
    """
    svg = generate_tree_svg(tree_node)
    
    html = f'''
    <div style="
        background: #0F172A;
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 12px;
        padding: 16px;
        overflow-x: auto;
        margin: 8px 0;
    ">
        <div style="text-align: center; min-width: 400px;">
            {svg}
        </div>
    </div>
    '''
    return html


# ============================================================
#  Legend Component
# ============================================================

def generate_legend_html():
    """Generate an HTML legend showing node color meanings."""
    items = [
        ('Root (QUERY)', '#7C3AED'),
        ('SELECT', '#2563EB'),
        ('FROM', '#0891B2'),
        ('WHERE', '#DC2626'),
        ('Group Node', '#059669'),
        ('Condition', '#D97706'),
        ('Leaf Value', '#10B981'),
        ('Operator', '#F59E0B'),
    ]
    
    legend_items = []
    for label, color in items:
        legend_items.append(
            f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;">'
            f'<span style="width:12px;height:12px;border-radius:50%;background:{color};display:inline-block;"></span>'
            f'<span style="color:#94A3B8;font-size:0.75rem;">{label}</span>'
            f'</span>'
        )
    
    return f'<div style="display:flex;flex-wrap:wrap;gap:4px;padding:8px 0;">{"".join(legend_items)}</div>'
