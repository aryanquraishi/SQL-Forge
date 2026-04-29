import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import ThemeSwitch from '@/components/ui/theme-switch'
import GradientButton from '@/components/ui/button-1'
import { SQLForgeLogo } from '@/components/ui/sqlforge-logo'
import { PromptInput } from '@/components/ui/ai-chat-input'
import ConfettiBackground from '@/components/ui/confetti-background'
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
  const [openSection, setOpenSection] = useState<string | null>(null)
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
    setResult(null) // Reset pipeline state
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
      {/* Sidebar — Desktop: always visible, Mobile: framer-motion slide */}
      {/* Desktop sidebar — only on md+ screens */}
      <nav className="desktop-sidebar h-screen w-64 border-r border-border bg-card backdrop-blur-xl flex-col py-6 shadow-lg shrink-0 hidden md:flex">
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
                const el = document.getElementById(item.target)
                if (el) {
                  el.scrollIntoView({ behavior: 'smooth', block: 'start' })
                  el.classList.add('section-highlight')
                  setTimeout(() => el.classList.remove('section-highlight'), 1500)
                } else {
                  window.scrollTo({ top: 0, behavior: 'smooth' })
                }
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${activeNav === item.id
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

      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sideOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black/60 z-40 md:hidden"
              onClick={() => setSideOpen(false)}
            />
            <motion.nav
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="fixed top-0 left-0 h-screen w-[280px] bg-card border-r border-border flex flex-col py-5 shadow-2xl z-50 md:hidden"
            >
              <div className="px-5 mb-6 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <SQLForgeLogo size={32} />
                  <div>
                    <span className="font-mono font-bold text-lg text-primary">SQL</span>
                    <span className="font-[Literata] font-light text-lg">Forge</span>
                  </div>
                </div>
                <button onClick={() => setSideOpen(false)} className="p-1.5 rounded-lg hover:bg-accent/50 text-muted-foreground">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="px-4 mb-4">
                <GradientButton onClick={() => { setQuery('SELECT name, age FROM students WHERE age > 18'); setSideOpen(false); handleCompile() }}
                  width="100%" height="40px">
                  <Play className="w-4 h-4" /> Run Sample
                </GradientButton>
              </div>
              <div className="flex-1 overflow-y-auto space-y-1 px-3">
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
                      } else {
                        window.scrollTo({ top: 0, behavior: 'smooth' })
                      }
                    }}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all text-sm ${activeNav === item.id
                      ? 'text-primary font-bold bg-primary/10 border border-primary/20'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent/50 border border-transparent'
                      }`}>
                    <item.icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </button>
                ))}
              </div>
            </motion.nav>
          </>
        )}
      </AnimatePresence>

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
          <div className="flex items-center gap-2">
            <ThemeSwitch />
            <button onClick={handleFormat} className="px-2.5 py-1.5 text-primary border border-primary/30 rounded-lg hover:bg-primary/10 text-xs sm:text-sm transition-colors">Format</button>
            <GradientButton onClick={handleCompile} width="90px" height="34px">
              <Play className="w-4 h-4" /> Run
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

              {/* Collapsible Sections — Accordion (only one open at a time) */}
              <div id="intermediate" className="space-y-2">
                {result.grammar_trace?.length > 0 && (
                  <Details title="CFG Rules Trace" icon={Gauge} sectionKey="cfg" openSection={openSection} setOpenSection={setOpenSection}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="bg-muted/50 rounded p-2 overflow-auto max-h-[250px]">
                        <table className="w-full font-mono text-xs border-collapse border border-border/40">
                          <thead className="bg-muted/30"><tr><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">Non-Terminal</th><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">Production</th></tr></thead>
                          <tbody>{result.grammar_rules?.map((r: string, i: number) => {
                            const parts = r.split('→')
                            return <tr key={i} className="hover:bg-muted/20"><td className="px-2 py-1 text-primary font-semibold whitespace-nowrap border border-border/40">{parts[0]?.trim()}</td><td className="px-2 py-1 border border-border/40">{parts[1]?.trim() || r}</td></tr>
                          })}</tbody>
                        </table>
                      </div>
                      <div className="bg-muted/50 rounded p-2 overflow-auto max-h-[250px]">
                        <table className="w-full font-mono text-xs border-collapse border border-border/40">
                          <thead className="bg-muted/30"><tr><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40 w-8">#</th><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">Derivation Step</th></tr></thead>
                          <tbody>{result.grammar_trace?.map((t: any, i: number) => <tr key={i} className="hover:bg-muted/20"><td className="px-2 py-1 text-primary font-bold border border-border/40">{i + 1}</td><td className="px-2 py-1 border border-border/40">{t.production}</td></tr>)}</tbody>
                        </table>
                      </div>
                    </div>
                  </Details>
                )}
                {result.first_sets?.length > 0 && (
                  <Details title="First & Follow Sets" icon={ArrowRightLeft} sectionKey="firstfollow" openSection={openSection} setOpenSection={setOpenSection}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="bg-muted/30 rounded p-2 overflow-auto max-h-[250px]">
                        <table className="w-full font-mono text-xs border-collapse border border-border/40">
                          <thead className="bg-muted/30"><tr><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">Non-Terminal</th><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">FIRST Set</th></tr></thead>
                          <tbody>{result.first_sets.map((item: any, i: number) => <tr key={i} className="hover:bg-muted/20"><td className="px-2 py-1 text-primary font-semibold border border-border/40">{item.non_terminal}</td><td className="px-2 py-1 border border-border/40">{item.first_set}</td></tr>)}</tbody>
                        </table>
                      </div>
                      <div className="bg-muted/30 rounded p-2 overflow-auto max-h-[250px]">
                        <table className="w-full font-mono text-xs border-collapse border border-border/40">
                          <thead className="bg-muted/30"><tr><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">Non-Terminal</th><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">FOLLOW Set</th></tr></thead>
                          <tbody>{result.follow_sets?.map((item: any, i: number) => <tr key={i} className="hover:bg-muted/20"><td className="px-2 py-1 text-primary font-semibold border border-border/40">{item.non_terminal}</td><td className="px-2 py-1 border border-border/40">{item.follow_set}</td></tr>)}</tbody>
                        </table>
                      </div>
                    </div>
                  </Details>
                )}
                {result.parsing_table?.length > 0 && (
                  <Details title="LALR Parsing Table" icon={Grid3X3} sectionKey="lalr" openSection={openSection} setOpenSection={setOpenSection}>
                    <div className="overflow-x-auto">
                      <table className="w-full font-mono text-xs border-collapse border border-border/40 min-w-[500px]">
                        <thead className="bg-muted/30"><tr>{Object.keys(result.parsing_table[0]).map(k => <th key={k} className="text-left px-3 py-2 text-muted-foreground border border-border/40 font-bold uppercase text-[10px] tracking-wider">{k}</th>)}</tr></thead>
                        <tbody>{result.parsing_table.map((row: any, i: number) => <tr key={i} className="hover:bg-muted/10">{Object.entries(row).map(([k, v], j) => {
                          const val = String(v || '')
                          const cls = val.includes('Shift') ? 'text-emerald-500 font-semibold' : val.includes('Reduce') ? 'text-red-400 font-semibold' : k === 'state' ? 'text-primary font-bold' : ''
                          return <td key={j} className={`px-3 py-1.5 border border-border/40 ${cls}`}>{val || '·'}</td>
                        })}</tr>)}</tbody>
                      </table>
                    </div>
                  </Details>
                )}
                {result.parse_tree_svg && (
                  <Details title="Graphical Parse Tree" icon={TreePine} sectionKey="graphtree" openSection={openSection} setOpenSection={setOpenSection}>
                    <div className="overflow-auto parse-tree-container" dangerouslySetInnerHTML={{ __html: result.parse_tree_svg }} />
                  </Details>
                )}
                {result.postfix && (
                  <Details title="Postfix Notation" icon={ArrowRightLeft} sectionKey="postfix" openSection={openSection} setOpenSection={setOpenSection}>
                    <div className="bg-muted/50 rounded p-3 font-mono text-sm">{result.postfix}</div>
                  </Details>
                )}
                {result.tac_string && (
                  <Details title="Three Address Code" icon={FileText} sectionKey="tac" openSection={openSection} setOpenSection={setOpenSection}>
                    <pre className="bg-muted/50 rounded p-3 font-mono text-xs whitespace-pre overflow-auto">{result.tac_string}</pre>
                  </Details>
                )}
                {result.quadruples?.length > 0 && (
                  <Details title="Quadruples & Triples" icon={Grid3X3} sectionKey="quads" openSection={openSection} setOpenSection={setOpenSection}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="bg-muted/30 rounded p-2 overflow-auto max-h-[250px]">
                        <table className="w-full font-mono text-xs border-collapse border border-border/40">
                          <thead className="bg-muted/30"><tr><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">#</th><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">Op</th><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">Arg1</th><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">Arg2</th><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">Result</th></tr></thead>
                          <tbody>{result.quadruples.map((q: any, i: number) => <tr key={i} className="hover:bg-muted/20"><td className="px-2 py-1 border border-border/40">{q.index}</td><td className="px-2 py-1 text-primary border border-border/40">{q.operator}</td><td className="px-2 py-1 border border-border/40">{q.arg1}</td><td className="px-2 py-1 border border-border/40">{q.arg2}</td><td className="px-2 py-1 font-semibold border border-border/40">{q.result}</td></tr>)}</tbody>
                        </table>
                      </div>
                      {result.triples?.length > 0 && (
                        <div className="bg-muted/30 rounded p-2 overflow-auto max-h-[250px]">
                          <table className="w-full font-mono text-xs border-collapse border border-border/40">
                            <thead className="bg-muted/30"><tr><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">#</th><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">Op</th><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">Arg1</th><th className="text-left px-2 py-1.5 text-muted-foreground border border-border/40">Arg2</th></tr></thead>
                            <tbody>{result.triples.map((t: any, i: number) => <tr key={i} className="hover:bg-muted/20"><td className="px-2 py-1 border border-border/40">{t.index}</td><td className="px-2 py-1 text-primary border border-border/40">{t.operator}</td><td className="px-2 py-1 border border-border/40">{t.arg1}</td><td className="px-2 py-1 border border-border/40">{t.arg2}</td></tr>)}</tbody>
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
          className="fixed bottom-20 md:bottom-6 right-3 md:right-6 z-50 w-10 h-10 md:w-14 md:h-14 bg-primary text-primary-foreground rounded-full shadow-lg flex items-center justify-center hover:scale-105 active:scale-95 transition-transform">
          <MessageCircle className="w-5 h-5 md:w-6 md:h-6" />
        </button>
      )}
      {aiOpen && (
        <div className="fixed inset-4 md:inset-auto md:bottom-6 md:right-6 z-50 md:w-[340px] md:h-[480px] bg-card rounded-2xl border border-border shadow-2xl flex flex-col overflow-hidden">
          {/* Fun Confetti Background */}
          <div className="absolute inset-0 pointer-events-none opacity-50"><ConfettiBackground /></div>

          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary/50 to-transparent z-10" />
          <div className="relative z-10 p-3 border-b border-border flex items-center justify-between bg-card/90 backdrop-blur-sm">
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
          <div ref={chatRef} className="relative z-10 flex-1 p-3 overflow-y-auto space-y-3 flex flex-col bg-card/40 backdrop-blur-sm">
            {chatMessages.map((msg, i) => (
              <div key={i} className={`flex gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                {msg.role === 'assistant' && (
                  <div className="w-6 h-6 rounded-md bg-primary/20 border border-primary/30 flex items-center justify-center shrink-0 mt-1">
                    <Sparkles className="w-3 h-3 text-primary" />
                  </div>
                )}
                <div className={`rounded-2xl p-2.5 text-sm max-w-[85%] border overflow-hidden ${msg.role === 'user' ? 'bg-accent/60 rounded-tr-sm border-border' : 'bg-primary/10 rounded-tl-sm border-primary/20'}`}>
                  <div className="markdown-body text-sm space-y-2 break-words leading-relaxed">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        code({ node, inline, className, children, ...props }: any) {
                          const match = /language-(\w+)/.exec(className || '')
                          return !inline ? (
                            <div className="relative mt-2 mb-2 rounded-md overflow-hidden border border-primary/20">
                              <div className="flex items-center px-3 py-1 bg-muted/80 border-b border-primary/10 text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
                                {match?.[1] || 'Code'}
                              </div>
                              <pre className="p-3 bg-background/60 overflow-x-auto text-xs font-mono text-primary/90 scrollbar-thin">
                                <code className={className} {...props}>{children}</code>
                              </pre>
                            </div>
                          ) : (
                            <code className="bg-primary/10 text-primary rounded px-1 py-0.5 text-xs font-mono mx-0.5" {...props}>{children}</code>
                          )
                        },
                        table: ({ node, ...props }) => <div className="overflow-x-auto my-2"><table className="w-full border-collapse border border-border/40 text-xs" {...props} /></div>,
                        th: ({ node, ...props }) => <th className="border border-border/40 px-2 py-1.5 bg-muted/30 text-left font-semibold text-muted-foreground" {...props} />,
                        td: ({ node, ...props }) => <td className="border border-border/40 px-2 py-1" {...props} />,
                        ul: ({ node, ...props }) => <ul className="list-disc list-outside ml-4 space-y-1" {...props} />,
                        ol: ({ node, ...props }) => <ol className="list-decimal list-outside ml-4 space-y-1" {...props} />,
                        a: ({ node, ...props }) => <a className="text-primary underline decoration-primary/30 underline-offset-2 hover:decoration-primary transition-colors" {...props} />,
                        p: ({ node, ...props }) => <p className="last:mb-0" {...props} />,
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
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
          <div className="relative z-10 p-3 bg-card/90 backdrop-blur-sm border-t border-border">
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
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 px-4 pb-2 pt-1 bg-gradient-to-t from-background via-background/95 to-transparent">
        <LimelightNav
          className="bg-card/95 dark:bg-card/90 backdrop-blur-xl border border-border shadow-2xl rounded-2xl"
          items={[
            { id: 'editor', icon: <Code />, label: 'Editor', onClick: () => { setActiveNav('editor'); window.scrollTo({ top: 0, behavior: 'smooth' }) } },
            { id: 'pipeline', icon: <ListTree />, label: 'Results', onClick: () => { if (result) setActiveNav('tokens') } },
            { id: 'menu', icon: <Menu />, label: 'Menu', onClick: () => setSideOpen(true) },
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

function Details({ title, icon: Icon, sectionKey, openSection, setOpenSection, children }: { title: string; icon: any; sectionKey: string; openSection: string | null; setOpenSection: (k: string | null) => void; children: React.ReactNode }) {
  const isOpen = openSection === sectionKey
  return (
    <div className="bg-card/50 backdrop-blur-xl border border-border rounded-xl hover:border-primary/50 transition-colors">
      <button onClick={() => setOpenSection(isOpen ? null : sectionKey)} className="w-full p-3 flex items-center gap-2 cursor-pointer">
        <Icon className="w-4 h-4 text-primary" />
        <span className="font-[Literata] text-sm font-bold text-foreground">{title}</span>
        <ChevronDown className={`w-4 h-4 ml-auto text-muted-foreground transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && <div className="px-3 pb-3 animate-[fadeIn_0.2s_ease-out]">{children}</div>}
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
