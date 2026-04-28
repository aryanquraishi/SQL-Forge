"""
app.py — Flask Backend for Terra SQL Studio
Serves the exact Google Stitch design and handles compilation API.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import sys, os, json, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compiler import MiniSQLCompiler
from ai_assistant import get_ai_response
from tree_visualizer import generate_tree_svg

# Serve React build if available, fallback to templates/static
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'dist')
if os.path.exists(FRONTEND_DIST):
    app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path='')
else:
    app = Flask(__name__, template_folder='templates', static_folder='static')
compiler = MiniSQLCompiler()
DEFAULT_GROQ_KEY = os.environ.get('GROQ_API_KEY', '')


@app.route('/')
def index():
    if os.path.exists(os.path.join(FRONTEND_DIST, 'index.html')):
        return send_from_directory(FRONTEND_DIST, 'index.html')
    return render_template('index.html')

@app.errorhandler(404)
def not_found(e):
    # SPA fallback: serve index.html for client-side routing
    if os.path.exists(os.path.join(FRONTEND_DIST, 'index.html')):
        return send_from_directory(FRONTEND_DIST, 'index.html')
    return 'Not found', 404


import re

@app.route('/api/format', methods=['POST'])
def format_query():
    data = request.get_json()
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'formatted': ''})
    
    # Simple regex-based SQL formatter
    # Collapse multiple spaces
    formatted = re.sub(r'\s+', ' ', query)
    
    # Uppercase keywords and add newlines before major clauses
    keywords = ['SELECT', 'FROM', 'WHERE', 'INSERT INTO', 'VALUES', 'AND', 'OR', 'ORDER BY', 'GROUP BY']
    for kw in keywords:
        # Case insensitive replacement, adding newline
        formatted = re.sub(rf'(?i)\b{kw}\b', f'\n{kw}', formatted)
    
    formatted = formatted.strip()
    return jsonify({'formatted': formatted})

@app.route('/api/compile', methods=['POST'])
def compile_query():
    data = request.get_json()
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'error': 'Empty query'}), 400

    result = compiler.compile(query)

    # Build response
    resp = {
        'is_valid': result.is_valid,
        'tokens': result.tokens,
        'token_stats': result.token_stats,
        'symbol_table': result.symbol_table_data,
        'errors': result.errors,
        'error_count': result.error_count,
        'grammar_rules': result.grammar_rules,
        'grammar_trace': result.grammar_trace,
        'first_sets': result.first_sets,
        'follow_sets': result.follow_sets,
        'parsing_table': result.parsing_table,
        'parse_tree_str': result.parse_tree_str,
        'parse_tree_svg': generate_tree_svg(result.parse_tree_node) if result.parse_tree_node else None,
        'tree_depth': result.tree_depth,
        'tree_node_count': result.tree_node_count,
        'postfix': result.postfix,
        'postfix_steps': result.postfix_steps,
        'tac_string': result.tac_string,
        'quadruples': result.quadruples,
        'triples': result.triples,
        'compile_time_ms': result.compile_time_ms,
    }
    return jsonify(resp)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', [])
    api_key = data.get('api_key', '') or DEFAULT_GROQ_KEY
    response = get_ai_response(messages, api_key)
    return jsonify({'response': response})


@app.route('/api/format', methods=['POST'])
def format_sql():
    from utils import format_query
    data = request.get_json()
    query = data.get('query', '')
    return jsonify({'formatted': format_query(query)})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
