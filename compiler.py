"""
compiler.py — Main Compiler Pipeline for Mini SQL Compiler
Orchestrates: Lexer → Parser → Symbol Table → Syntax Tree → Intermediate Code
"""

from dataclasses import dataclass, field
from typing import Optional
import time

from lexer import tokenize, get_token_patterns
from parser import parse_query, get_grammar_rules
from syntax_tree import build_tree_from_ast, tree_to_string, get_tree_depth, get_tree_node_count
from symbol_table import build_symbol_table_from_ast, SymbolTable
from intermediate import generate_postfix, get_postfix_steps, TACGenerator, generate_quadruples, generate_triples
from grammar_analysis import compute_first_sets, compute_follow_sets, format_first_sets, format_follow_sets, generate_parsing_table, generate_parsing_table_for_query
from errors import ErrorCollector


@dataclass
class CompileResult:
    """Complete compilation result."""
    query: str = ""
    tokens: list = field(default_factory=list)
    token_patterns: dict = field(default_factory=dict)
    symbol_table: Optional[SymbolTable] = None
    symbol_table_data: list = field(default_factory=list)
    token_stats: dict = field(default_factory=dict)
    is_valid: bool = False
    syntax_message: str = ""
    ast: dict = field(default_factory=dict)
    grammar_trace: list = field(default_factory=list)
    grammar_rules: list = field(default_factory=list)
    first_sets: list = field(default_factory=list)
    follow_sets: list = field(default_factory=list)
    parsing_table: list = field(default_factory=list)
    parse_tree_str: str = ""
    parse_tree_node: object = None
    tree_depth: int = 0
    tree_node_count: int = 0
    postfix: str = ""
    postfix_steps: list = field(default_factory=list)
    tac: list = field(default_factory=list)
    tac_string: str = ""
    quadruples: list = field(default_factory=list)
    triples: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    error_count: int = 0
    warning_count: int = 0
    compile_time_ms: float = 0.0
    step_times: dict = field(default_factory=dict)


class MiniSQLCompiler:
    """Main compiler class — orchestrates the full pipeline."""
    
    def __init__(self):
        self.tac_generator = TACGenerator()
    
    def compile(self, query):
        result = CompileResult(query=query.strip().rstrip(';').strip())
        start_time = time.time()
        all_errors = ErrorCollector()
        
        # STEP 1: Lexical Analysis
        s = time.time()
        tokens_list, lexer_errors = tokenize(result.query)
        result.tokens = tokens_list
        result.token_patterns = get_token_patterns()
        result.step_times['lexical_analysis'] = (time.time() - s) * 1000
        if lexer_errors.has_errors():
            for err in lexer_errors.errors:
                all_errors.add_error(err)
        
        # STEP 2: Token Statistics
        s = time.time()
        result.token_stats = self._compute_token_stats(tokens_list)
        result.step_times['token_statistics'] = (time.time() - s) * 1000
        
        # STEP 3: Syntax Analysis
        s = time.time()
        ast, grammar_trace, parse_errors = parse_query(result.query)
        result.step_times['syntax_analysis'] = (time.time() - s) * 1000
        if parse_errors.has_errors():
            for err in parse_errors.errors:
                all_errors.add_error(err)
            result.is_valid = False
            result.syntax_message = "❌ Query has syntax errors"
            result.ast = None
        elif lexer_errors.has_errors():
            result.is_valid = False
            result.syntax_message = "❌ Query has illegal characters"
            result.ast = ast
        else:
            result.is_valid = True
            result.syntax_message = "✅ Query is syntactically VALID"
            result.ast = ast
        result.grammar_trace = grammar_trace
        result.grammar_rules = get_grammar_rules()
        
        # STEP 4: Symbol Table
        s = time.time()
        if ast:
            st = build_symbol_table_from_ast(ast, tokens_list)
            result.symbol_table = st
            result.symbol_table_data = st.get_as_list()
        result.step_times['symbol_table'] = (time.time() - s) * 1000
        
        # Steps 5-10 only if valid — grammar analysis is query-specific
        if result.is_valid and ast:
            query_type = ast.get('type', 'SELECT')
            
            # STEP 5: FIRST & FOLLOW Sets (filtered by query type)
            s = time.time()
            first = compute_first_sets()
            follow = compute_follow_sets(first)
            result.first_sets = format_first_sets(first, query_type=query_type)
            result.follow_sets = format_follow_sets(follow, query_type=query_type)
            result.step_times['first_follow'] = (time.time() - s) * 1000
            
            # STEP 6: Dynamic Parsing Table (query-type-specific)
            s = time.time()
            result.parsing_table = generate_parsing_table_for_query(query_type)
            result.step_times['parsing_table'] = (time.time() - s) * 1000
            
            # STEP 7: Parse Tree
            s = time.time()
            tree_node = build_tree_from_ast(ast)
            result.parse_tree_node = tree_node
            result.parse_tree_str = tree_to_string(tree_node)
            result.tree_depth = get_tree_depth(tree_node)
            result.tree_node_count = get_tree_node_count(tree_node)
            result.step_times['parse_tree'] = (time.time() - s) * 1000
            
            # STEP 8: Postfix
            s = time.time()
            cond = ast.get('condition', None)
            if cond:
                result.postfix = generate_postfix(cond)
                result.postfix_steps = get_postfix_steps(cond)
            result.step_times['postfix'] = (time.time() - s) * 1000
            
            # STEP 9: TAC
            s = time.time()
            self.tac_generator.reset()
            tac_inst = self.tac_generator.generate(ast)
            result.tac = tac_inst
            result.tac_string = self.tac_generator.get_tac_string()
            result.step_times['tac'] = (time.time() - s) * 1000
            
            # STEP 10: Quadruples & Triples
            s = time.time()
            result.quadruples = generate_quadruples(tac_inst)
            result.triples = generate_triples(tac_inst)
            result.step_times['quadruples'] = (time.time() - s) * 1000
        
        # Finalize
        result.errors = [e.to_dict() for e in all_errors.errors]
        result.warnings = [w.to_dict() for w in all_errors.warnings]
        result.error_count = all_errors.get_error_count()
        result.warning_count = all_errors.get_warning_count()
        result.compile_time_ms = (time.time() - start_time) * 1000
        return result
    
    def _compute_token_stats(self, tokens_list):
        stats = {'KEYWORD': 0, 'IDENTIFIER': 0, 'NUMBER': 0, 'STRING': 0, 'OPERATOR': 0, 'SYMBOL': 0, 'ARITHMETIC': 0}
        for tok in tokens_list:
            cat = tok.get('category', 'SYMBOL')
            stats[cat] = stats.get(cat, 0) + 1
        return {k: v for k, v in stats.items() if v > 0}


def compile_query(query):
    """Convenience function to compile a query."""
    return MiniSQLCompiler().compile(query)


if __name__ == '__main__':
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    for q in ["SELECT name, age FROM students WHERE age > 18", "SELECT * FROM courses", "SELECT FROM students"]:
        r = compile_query(q)
        print(f"\n{'='*60}\nQuery: {q}\nStatus: {'VALID' if r.is_valid else 'INVALID'} | Tokens: {len(r.tokens)} | Time: {r.compile_time_ms:.2f}ms")
        if r.is_valid:
            print(f"Tree:\n{r.parse_tree_str}")
        else:
            for e in r.errors:
                print(f"  Error: {e['message']}")
