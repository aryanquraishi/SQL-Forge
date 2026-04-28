const BASE = '';

export interface CompileResult {
  is_valid: boolean;
  tokens: Array<{ value: string; type: string; category: string; position: number; regex_pattern: string }>;
  token_stats: Record<string, number>;
  symbol_table: Array<{ name: string; category: string; data_type: string; frequency: number; contexts: string[]; first_position: number }>;
  errors: Array<{ message: string; token_value?: string; position?: number; hint?: string }>;
  error_count: number;
  grammar_rules: string[];
  grammar_trace: Array<{ production: string }>;
  first_sets: string[][];
  follow_sets: string[][];
  parsing_table: Record<string, string>[];
  parse_tree_str: string;
  parse_tree_svg: string | null;
  tree_depth: number;
  tree_node_count: number;
  postfix: string;
  postfix_steps: Array<{ step: number; description: string; expression: string }>;
  tac_string: string;
  quadruples: string[][];
  triples: string[][];
  compile_time_ms: number;
}

export async function compileQuery(query: string): Promise<CompileResult> {
  const res = await fetch(`${BASE}/api/compile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  return res.json();
}

export async function chatWithAI(messages: Array<{ role: string; content: string }>, apiKey: string): Promise<string> {
  const res = await fetch(`${BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages, api_key: apiKey }),
  });
  const data = await res.json();
  return data.response;
}

export async function formatSQL(query: string): Promise<string> {
  const res = await fetch(`${BASE}/api/format`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  const data = await res.json();
  return data.formatted;
}
