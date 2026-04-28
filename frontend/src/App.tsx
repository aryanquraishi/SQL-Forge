import { useState, useRef, useEffect } from 'react'
import ThemeSwitch from '@/components/ui/theme-switch'
import GradientButton from '@/components/ui/button-1'
import { SQLForgeLogo } from '@/components/ui/sqlforge-logo'
import { PromptInput } from '@/components/ui/ai-chat-input'
import { compileQuery, chatWithAI, formatSQL, type CompileResult } from '@/lib/api'
import {
  Play, Terminal, AlignJustify as Segment, TreePine, KeyRound, Code,
  Sparkles, Send, Menu, ChevronDown, ListTree, BrainCircuit,
  ArrowRightLeft, FileText, Grid3X3, CheckCircle, XCircle, Gauge,
  MessageCircle, X
} from 'lucide-react'
import { LimelightNav } from '@/components/ui/limelight-nav'

export default function App() {
  const [query, setQuery] = useState('SELECT name, age FROM students WHERE age > 18')
  const [result, setResult] = useState<CompileResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [sideOpen, setSideOpen] = useState(false)
  const [aiOpen, setAiOpen] = useState(false)
  const [activeNav, setActiveNav] = useState('editor')
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([
    { role: 'assistant', content: "Hi! I'm SQLForge AI. Ask me about Compiler Design concepts or this project." }
  ])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const chatRef = useRef<HTMLDivElement>(null)

  useEffect(() => { chatRef.current?.scrollTo(0, chatRef.current.scrollHeight) }, [chatMessages])

  const handleCompile = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const data = await compileQuery(query)
      setResult(data)
      setActiveNav('tokens')
    } catch { alert('Compilation error') }
    setLoading(false)
  }

  const handleFormat = async () => {
    setActiveNav('editor')
    try {
      const formatted = await formatSQL(query)
      if (formatted) setQuery(formatted)
    } catch { /* ignore */ }
  }

  const handleChat = async () => {
    if (!chatInput.trim()) return
    const msg = chatInput.trim()
    setChatInput('')
    const newMsgs = [...chatMessages, { role: 'user', content: msg }]
    setChatMessages(newMsgs)
    setChatLoading(true)
    try {
      const resp = await chatWithAI([{ role: 'user', content: msg }], '')
      setChatMessages([...newMsgs, { role: 'assistant', content: resp }])
    } catch {
      setChatMessages([...newMsgs, { role: 'assistant', content: '⚠️ Error connecting to AI.' }])
    }
    setChatLoading(false)
  }

  return (
    <div className="h-screen flex overflow-hidden font-[Nunito_Sans]">
      {/* Sidebar */}
      {/* Mobile overlay backdrop */}
      {sideOpen && <div className="fixed inset-0 bg-black/50 z-20 md:hidden" onClick={() => setSideOpen(false)} />}
      <nav className={`fixed md:relative h-screen w-64 border-r border-border bg-card backdrop-blur-xl flex-col py-6 shadow-lg z-30 shrink-0 transition-transform duration-300 ${sideOpen ? 'flex translate-x-0' : 'flex -translate-x-full md:translate-x-0'}`}>
        <div className="px-6 mb-8 flex items-center gap-3">
          <SQLForgeLogo size={40} />
          <div>
            <div className="leading-tight">
              <span className="font-mono font-bold text-xl text-primary tracking-tight">SQL</span>
              <span className="font-[Literata] font-light text-xl tracking-wide">Forge</span>
            </div>
            <p className="text-[9px] text-muted-foreground font-mono tracking-[0.2em]">QUERY · CRAFT · COMPILE</p>
          </div>
        </div>
        <div className="px-4 mb-6">
          <GradientButton onClick={() => { setQuery('SELECT name, age FROM students WHERE age > 18'); handleCompile() }}
            width="100%" height="44px">
            <Play className="w-4 h-4" /> Run Sample
          </GradientButton>
        </div>
        <div className="flex-1 overflow-y-auto space-y-1 px-2">
          {[
            { id: 'editor', icon: Terminal, label: 'Query Editor', target: 'editor-section' },
            { id: 'tokens', icon: Segment, label: 'Token Stream', target: 'tokens' },
            { id: 'tree', icon: TreePine, label: 'Parse Tree', target: 'tree' },
            { id: 'symbols', icon: KeyRound, label: 'Symbol Table', target: 'symbols' },
            { id: 'intermediate', icon: Code, label: 'Intermediate Code', target: 'intermediate' },
          ].map((item) => (
            <button key={item.id}
              onClick={() => {
                setActiveNav(item.id)
                setSideOpen(false)
                const el = document.getElementById(item.target)
                if (el) {
                  el.scrollIntoView({ behavior: 'smooth', block: 'start' })
                  el.classList.add('section-highlight')
                  setTimeout(() => el.classList.remove('section-highlight'), 1500)
                } else {
                  window.scrollTo({ top: 0, behavior: 'smooth' })
                }
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                activeNav === item.id
                  ? 'text-primary font-bold bg-primary/10 shadow-sm border border-primary/20'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent/50 border border-transparent'
              }`}>
              <item.icon className={`w-5 h-5 transition-transform duration-200 ${activeNav === item.id ? 'scale-110' : ''}`} />
              <span>{item.label}</span>
              {activeNav === item.id && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />}
            </button>
          ))}
        </div>
      </nav>

      {/* Main */}
      <div className="flex-1 flex flex-col h-screen relative">
        {/* TopBar */}
        <header className="sticky top-0 z-40 border-b border-border bg-card/60 backdrop-blur-xl flex justify-between items-center h-14 px-4 md:px-8">
          <div className="flex items-center gap-4">
            <button className="md:hidden p-2 text-muted-foreground" onClick={() => setSideOpen(!sideOpen)}>
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <SQLForgeLogo size={28} />
              <span className="font-mono font-bold text-lg text-primary">SQL</span>
              <span className="font-[Literata] font-light text-lg">Forge</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <ThemeSwitch />
            <button onClick={handleFormat} className="hidden sm:block px-3 py-1.5 text-primary border border-primary/30 rounded-lg hover:bg-primary/10 text-sm transition-colors">Format</button>
            <GradientButton onClick={handleCompile} width="100px" height="34px">
              <Play className="w-4 h-4" /> <span className="hidden sm:inline">Execute</span><span className="sm:hidden">Run</span>
            </GradientButton>
          </div>
        </header>

        {/* Canvas */}
        <main className="flex-1 p-4 md:p-6 flex flex-col gap-6 overflow-y-auto pb-24 md:pb-6">
          {/* Editor — only when Query Editor is selected */}
          {activeNav === 'editor' && (
           <div id="editor-section" className="bg-[#0D1117] rounded-xl border border-border shadow-lg overflow-hidden flex flex-col">
            <div className="h-10 bg-card border-b border-border flex items-center justify-between px-4">
              <div className="flex items-center gap-3">
                <Code className="w-4 h-4 text-muted-foreground" />
                <span className="font-mono text-xs text-muted-foreground">query.sql</span>
              </div>
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50" />
                <div className="w-3 h-3 rounded-full bg-amber-500/20 border border-amber-500/50" />
                <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50" />
              </div>
            </div>
            <textarea value={query} onChange={e => setQuery(e.target.value)}
              onKeyDown={e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') handleCompile() }}
              className="flex-1 bg-[#0D1117] text-[#F2F2F0] p-4 font-mono text-sm leading-relaxed focus:outline-none resize-none min-h-[180px] placeholder:text-gray-600"
              placeholder="Enter your SQL query here..." spellCheck={false} />
           </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="text-center py-8 text-primary fade-in">
              <div className="flex items-center justify-center gap-2">
                {[0, 0.1, 0.2].map((d, i) => <div key={i} className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: `${d}s` }} />)}
              </div>
              <p className="text-muted-foreground text-sm mt-2">Compiling...</p>
            </div>
          )}

          {/* Results */}
          {result && !loading && activeNav !== 'editor' && (
            <div className="space-y-4 fade-in">
              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { label: 'Tokens', value: result.tokens?.length || 0 },
                  { label: 'Status', value: result.is_valid ? '✓ Valid' : '✗ Error', color: result.is_valid ? 'text-emerald-500' : 'text-red-500' },
                  { label: 'Tree Nodes', value: result.tree_node_count || 0 },
                  { label: 'Compile Time', value: `${(result.compile_time_ms || 0).toFixed(1)}ms` },
                ].map((s, i) => (
                  <div key={i} className="bg-card border border-border rounded-xl p-3 text-center">
                    <div className={`text-xl font-bold font-[Literata] ${s.color || 'text-primary'}`}>{s.value}</div>
                    <div className="text-muted-foreground text-[10px] uppercase tracking-widest">{s.label}</div>
                  </div>
                ))}
              </div>

              {/* Bento Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <BentoCard title="TOKEN STREAM" icon={Segment} id="tokens">
                  <div className="space-y-1 font-mono text-xs max-h-[200px] overflow-auto">
                    {result.tokens?.map((t, i) => (
                      <div key={i} className="flex justify-between">
                        <span className="text-muted-foreground">[{t.category?.substring(0, 3)}]</span>
                        <span>{t.value}</span>
                      </div>
                    ))}
                  </div>
                </BentoCard>
                <BentoCard title="PARSE TREE" icon={ListTree} id="tree">
                  <pre className="font-mono text-xs whitespace-pre overflow-auto max-h-[200px] text-foreground">{result.parse_tree_str || '(no tree)'}</pre>
                </BentoCard>
                <BentoCard title="SYMBOL TABLE" icon={KeyRound} id="symbols" badge="Live">
                  <table className="w-full text-left font-mono text-[11px]">
                    <thead className="text-muted-foreground border-b border-border"><tr><th>Symbol</th><th>Type</th><th>Scope</th></tr></thead>
                    <tbody>{result.symbol_table?.map((s, i) => (
                      <tr key={i}><td>{s.name}</td><td className="text-primary">{s.category}</td><td>{s.contexts?.join(', ')}</td></tr>
                    ))}</tbody>
                  </table>
                </BentoCard>
              </div>

              {/* Syntax Status */}
              {result.is_valid ? (
                <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-3 text-emerald-600 dark:text-emerald-400 font-bold flex items-center gap-2">
                  <CheckCircle className="w-5 h-5" /> Query is syntactically VALID
                </div>
              ) : (
                <div>
                  <div className="bg-destructive/10 border border-destructive/40 rounded-xl p-3 text-red-500 font-bold flex items-center gap-2 mb-2">
                    <XCircle className="w-5 h-5" /> {result.error_count} Syntax Error(s)
                  </div>
                  {result.errors?.map((e, i) => (
                    <div key={i} className="bg-destructive/5 border-l-2 border-destructive pl-3 py-2 text-sm mb-1 rounded-r-lg">
                      <strong>{e.message}</strong>{e.token_value && ` near '${e.token_value}'`}
                      {e.hint && <div className="text-primary text-xs mt-1">💡 {e.hint}</div>}
                    </div>
                  ))}
                </div>
              )}

              {/* Collapsible Sections — Professional monochrome */}
              <div id="intermediate" className="space-y-2">
                {result.grammar_trace?.length > 0 && (
                  <Details title="CFG Rules Trace" icon={Gauge}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <pre className="bg-muted/50 rounded p-2 font-mono text-xs overflow-auto max-h-[200px]">{result.grammar_rules?.join('\n')}</pre>
                      <pre className="bg-muted/50 rounded p-2 font-mono text-xs overflow-auto max-h-[200px]">{result.grammar_trace?.map((t, i) => `${i + 1}. ${t.production}`).join('\n')}</pre>
                    </div>
                  </Details>
                )}
                {result.first_sets?.length > 0 && (
                  <Details title="First & Follow Sets" icon={ArrowRightLeft}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="bg-muted/30 rounded p-2 font-mono text-xs overflow-auto max-h-[200px]">
                        <table className="w-full"><thead className="text-muted-foreground"><tr><th className="text-left">Non-Terminal</th><th className="text-left">FIRST</th></tr></thead>
                          <tbody>{result.first_sets.map((item: any, i: number) => <tr key={i}><td>{item.non_terminal}</td><td>{item.first_set}</td></tr>)}</tbody>
                        </table>
                      </div>
                      <div className="bg-muted/30 rounded p-2 font-mono text-xs overflow-auto max-h-[200px]">
                        <table className="w-full"><thead className="text-muted-foreground"><tr><th className="text-left">Non-Terminal</th><th className="text-left">FOLLOW</th></tr></thead>
                          <tbody>{result.follow_sets?.map((item: any, i: number) => <tr key={i}><td>{item.non_terminal}</td><td>{item.follow_set}</td></tr>)}</tbody>
                        </table>
                      </div>
                    </div>
                  </Details>
                )}
                {result.parsing_table?.length > 0 && (
                  <Details title="LALR Parsing Table" icon={Grid3X3}>
                    <div className="overflow-auto">
                      <table className="w-full font-mono text-xs">
                        <thead className="text-muted-foreground"><tr>{Object.keys(result.parsing_table[0]).map(k => <th key={k} className="text-left px-2 py-1">{k}</th>)}</tr></thead>
                        <tbody>{result.parsing_table.map((row, i) => <tr key={i} className="border-t border-border">{Object.values(row).map((v, j) => <td key={j} className="px-2 py-1">{v}</td>)}</tr>)}</tbody>
                      </table>
                    </div>
                  </Details>
                )}
                {result.parse_tree_svg && (
                  <Details title="Graphical Parse Tree" icon={TreePine}>
                    <div className="overflow-auto parse-tree-container" dangerouslySetInnerHTML={{ __html: result.parse_tree_svg }} />
                  </Details>
                )}
                {result.postfix && (
                  <Details title="Postfix Notation" icon={ArrowRightLeft}>
                    <div className="bg-muted/50 rounded p-3 font-mono text-sm">{result.postfix}</div>
                  </Details>
                )}
                {result.tac_string && (
                  <Details title="Three Address Code" icon={FileText}>
                    <pre className="bg-muted/50 rounded p-3 font-mono text-xs whitespace-pre overflow-auto">{result.tac_string}</pre>
                  </Details>
                )}
                {result.quadruples?.length > 0 && (
                  <Details title="Quadruples & Triples" icon={Grid3X3}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="bg-muted/30 rounded p-2 font-mono text-xs overflow-auto max-h-[200px]">
                        <table className="w-full"><thead className="text-muted-foreground"><tr><th className="text-left">#</th><th className="text-left">Op</th><th className="text-left">Arg1</th><th className="text-left">Arg2</th><th className="text-left">Result</th></tr></thead>
                          <tbody>{result.quadruples.map((q: any, i: number) => <tr key={i}><td>{q.index}</td><td>{q.operator}</td><td>{q.arg1}</td><td>{q.arg2}</td><td>{q.result}</td></tr>)}</tbody>
                        </table>
                      </div>
                      {result.triples?.length > 0 && (
                        <div className="bg-muted/30 rounded p-2 font-mono text-xs overflow-auto max-h-[200px]">
                          <table className="w-full"><thead className="text-muted-foreground"><tr><th className="text-left">#</th><th className="text-left">Op</th><th className="text-left">Arg1</th><th className="text-left">Arg2</th></tr></thead>
                            <tbody>{result.triples.map((t: any, i: number) => <tr key={i}><td>{t.index}</td><td>{t.operator}</td><td>{t.arg1}</td><td>{t.arg2}</td></tr>)}</tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  </Details>
                )}
              </div>
            </div>
          )}

          {/* Empty State */}
          {!result && !loading && (
            <div className="text-center py-12 text-muted-foreground">
              <SQLForgeLogo size={48} />
              <p className="font-[Literata] text-lg text-primary/60 mt-4">Enter a query and click Execute</p>
              <p className="text-sm mt-1">Try: SELECT name, age FROM students WHERE age &gt; 18</p>
            </div>
          )}
        </main>
      </div>

      {/* AI Chat — Floating Icon + Panel */}
      {!aiOpen && (
        <button onClick={() => setAiOpen(true)}
          className="fixed bottom-4 right-4 z-50 w-12 h-12 md:w-14 md:h-14 bg-primary text-primary-foreground rounded-full shadow-lg flex items-center justify-center hover:scale-105 transition-transform">
          <MessageCircle className="w-6 h-6" />
        </button>
      )}
      {aiOpen && (
        <div className="fixed inset-4 md:inset-auto md:bottom-6 md:right-6 z-50 md:w-[340px] md:h-[480px] bg-card/95 backdrop-blur-2xl rounded-2xl border border-border shadow-2xl flex flex-col overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
          <div className="p-3 border-b border-border flex items-center justify-between bg-card/80">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-primary" />
              </div>
              <div>
                <h3 className="font-[Literata] font-bold text-sm leading-tight">SQLForge AI</h3>
                <p className="text-[9px] text-primary/80 font-mono flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse inline-block" /> Online
                </p>
              </div>
            </div>
            <button onClick={() => setAiOpen(false)} className="p-1 text-muted-foreground hover:text-foreground transition-colors">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div ref={chatRef} className="flex-1 p-3 overflow-y-auto space-y-3 flex flex-col">
            {chatMessages.map((msg, i) => (
              <div key={i} className={`flex gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                {msg.role === 'assistant' && (
                  <div className="w-6 h-6 rounded-md bg-primary/20 border border-primary/30 flex items-center justify-center shrink-0 mt-1">
                    <Sparkles className="w-3 h-3 text-primary" />
                  </div>
                )}
                <div className={`rounded-2xl p-2.5 text-sm max-w-[85%] border ${msg.role === 'user' ? 'bg-accent/60 rounded-tr-sm border-border' : 'bg-primary/10 rounded-tl-sm border-primary/20'}`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex gap-2">
                <div className="w-6 h-6 rounded-md bg-primary/20 border border-primary/30 flex items-center justify-center shrink-0">
                  <Sparkles className="w-3 h-3 text-primary" />
                </div>
                <div className="bg-primary/10 rounded-2xl rounded-tl-sm p-2.5 border border-primary/20 flex items-center gap-1">
                  {[0, 0.1, 0.2].map((d, i) => <div key={i} className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: `${d}s` }} />)}
                </div>
              </div>
            )}
          </div>
          <div className="p-3 bg-card/80 border-t border-border">
            <PromptInput
              placeholder="Ask about compiler design..."
              onSubmit={(value) => {
                const msg = value.trim()
                if (!msg) return
                const newMsgs = [...chatMessages, { role: 'user', content: msg }]
                setChatMessages(newMsgs)
                setChatLoading(true)
                chatWithAI([{ role: 'user', content: msg }], '').then(resp => {
                  setChatMessages([...newMsgs, { role: 'assistant', content: resp }])
                }).catch(() => {
                  setChatMessages([...newMsgs, { role: 'assistant', content: '⚠️ Error connecting to AI.' }])
                }).finally(() => setChatLoading(false))
              }}
              disabled={chatLoading}
              className="border-border"
            />
          </div>
        </div>
      )}

      {/* Mobile Bottom Nav — LimelightNav */}
      <div className="md:hidden fixed bottom-4 left-1/2 -translate-x-1/2 z-40">
        <LimelightNav
          className="bg-card/90 dark:bg-card/80 backdrop-blur-xl border-border shadow-2xl rounded-2xl"
          items={[
            { id: 'editor', icon: <Code />, label: 'Editor', onClick: () => window.scrollTo({ top: 0, behavior: 'smooth' }) },
            { id: 'pipeline', icon: <ListTree />, label: 'Pipeline', onClick: () => document.getElementById('tokens')?.scrollIntoView({ behavior: 'smooth' }) },
            { id: 'symbols', icon: <KeyRound />, label: 'Symbols', onClick: () => document.getElementById('symbols')?.scrollIntoView({ behavior: 'smooth' }) },
            { id: 'ai', icon: <BrainCircuit />, label: 'AI', onClick: () => setAiOpen(true) },
          ]}
        />
      </div>
    </div>
  )
}

/* Helper Components */
function BentoCard({ title, icon: Icon, badge, id, children }: { title: string; icon: any; badge?: string; id?: string; children: React.ReactNode }) {
  return (
    <div id={id} className="bg-card/50 backdrop-blur-xl border border-border rounded-xl p-4 flex flex-col hover:border-primary/50 transition-colors shadow-lg">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 text-foreground">
          <Icon className="w-4 h-4 text-primary" />
          <h3 className="font-[Literata] text-sm font-bold tracking-wide">{title}</h3>
        </div>
        {badge && <span className="text-[10px] bg-primary/15 text-primary px-2 py-0.5 rounded-full border border-primary/30">{badge}</span>}
      </div>
      <div className="flex-1 bg-muted/30 rounded p-2 overflow-auto">{children}</div>
    </div>
  )
}

function Details({ title, icon: Icon, children }: { title: string; icon: any; children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="bg-card/50 backdrop-blur-xl border border-border rounded-xl hover:border-primary/50 transition-colors">
      <button onClick={() => setOpen(!open)} className="w-full p-3 flex items-center gap-2 cursor-pointer">
        <Icon className="w-4 h-4 text-primary" />
        <span className="font-[Literata] text-sm font-bold text-foreground">{title}</span>
        <ChevronDown className={`w-4 h-4 ml-auto text-muted-foreground transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && <div className="px-3 pb-3">{children}</div>}
    </div>
  )
}

function MiniTable({ headers, rows }: { headers: string[]; rows: string[][] }) {
  return (
    <div className="bg-muted/30 rounded p-2 font-mono text-xs overflow-auto max-h-[200px]">
      <table className="w-full"><thead className="text-muted-foreground"><tr>{headers.map(h => <th key={h} className="text-left">{h}</th>)}</tr></thead>
        <tbody>{rows?.map((r, i) => <tr key={i}>{r.map((c, j) => <td key={j}>{c}</td>)}</tr>)}</tbody>
      </table>
    </div>
  )
}
