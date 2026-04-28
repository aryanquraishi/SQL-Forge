"""
terra_styles.py — Terra SQL Studio Design System CSS
Extracted from Google Stitch designs (light/dark/mobile)
"""

TERRA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,400;7..72,700;7..72,900&family=Nunito+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

/* ═══════ CSS Variables ═══════ */
:root {
    --primary: #4a7c59;
    --primary-container: #78a886;
    --on-primary: #ffffff;
    --bg-dark: #121416;
    --bg-card: #1c1e21;
    --bg-editor: #0a0a0a;
    --text-primary: #d8f0de;
    --text-secondary: #a8a8a0;
    --text-muted: #64748b;
    --border: rgba(255,255,255,0.04);
    --green-glow: rgba(74,124,89,0.2);
    --tertiary: #705c30;
    --tertiary-container: #c4a66a;
    --error: #b83230;
    --syntax-kw: #5eead4;
    --syntax-str: #fcd34d;
    --syntax-num: #f472b6;
    --syntax-fn: #38bdf8;
    --syntax-op: #cbd5e1;
}

/* ═══════ Global ═══════ */
.stApp { font-family: 'Nunito Sans', sans-serif !important; }
h1,h2,h3 { font-family: 'Literata', serif !important; }

/* ═══════ Terra Header ═══════ */
.terra-header {
    background: var(--bg-dark);
    border-bottom: 1px solid var(--border);
    padding: 1rem 1.5rem;
    display: flex; align-items: center; gap: 12px;
    border-radius: 0 0 16px 16px;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(12px);
}
.terra-header .logo {
    width: 40px; height: 40px; border-radius: 50%;
    background: rgba(74,124,89,0.2);
    border: 1px solid rgba(74,124,89,0.3);
    display: flex; align-items: center; justify-content: center;
    color: var(--primary); font-size: 20px;
}
.terra-header h1 {
    color: var(--primary) !important; font-size: 1.4rem !important;
    font-weight: 900 !important; margin: 0 !important; letter-spacing: -0.5px;
}
.terra-header .subtitle {
    color: var(--text-muted); font-size: 0.75rem;
    font-family: 'Nunito Sans', sans-serif;
}

/* ═══════ Editor Card ═══════ */
.editor-card {
    background: var(--bg-editor);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
}
.editor-toolbar {
    height: 40px; background: var(--bg-dark);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 16px;
}
.editor-dots { display: flex; gap: 6px; }
.editor-dots span {
    width: 10px; height: 10px; border-radius: 50%;
}
.dot-red { background: rgba(239,68,68,0.2); border: 1px solid rgba(239,68,68,0.5); }
.dot-yellow { background: rgba(245,158,11,0.2); border: 1px solid rgba(245,158,11,0.5); }
.dot-green { background: rgba(34,197,94,0.2); border: 1px solid rgba(34,197,94,0.5); }
.file-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem; color: var(--text-secondary);
}

/* ═══════ Step Cards ═══════ */
.terra-card {
    background: rgba(18,20,22,0.5);
    backdrop-filter: blur(40px);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.3s;
}
.terra-card:hover { border-color: rgba(74,124,89,0.5); }

.terra-card-title {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 0.75rem;
    font-family: 'Literata', serif;
    font-weight: 700; font-size: 0.85rem;
    text-transform: uppercase; letter-spacing: 1.2px;
}
.terra-card-title .icon {
    color: var(--primary); font-size: 18px;
}
.terra-card-title .label { color: #5eead4; }

/* ═══════ Bento Grid ═══════ */
.bento-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 1rem;
}
@media (max-width: 768px) {
    .bento-grid { grid-template-columns: 1fr; }
}
.bento-item {
    background: rgba(18,20,22,0.5);
    backdrop-filter: blur(40px);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    transition: border-color 0.3s;
}
.bento-item:hover { border-color: rgba(74,124,89,0.5); }
.bento-item h3 {
    font-family: 'Literata', serif !important;
    font-size: 0.8rem !important; font-weight: 700 !important;
    letter-spacing: 1px; text-transform: uppercase;
    margin-bottom: 0.5rem !important;
}
.bento-item .content {
    background: rgba(0,0,0,0.4);
    border-radius: 8px; padding: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem; color: var(--text-secondary);
    overflow: auto; max-height: 180px;
}

/* ═══════ Success/Error ═══════ */
.terra-success {
    background: rgba(74,124,89,0.1);
    border: 1px solid rgba(74,124,89,0.4);
    border-radius: 12px; padding: 1rem 1.25rem;
    color: #8ecf9e; font-weight: 600;
}
.terra-error {
    background: rgba(184,50,48,0.1);
    border: 1px solid rgba(184,50,48,0.4);
    border-radius: 12px; padding: 1rem 1.25rem;
    color: #fca5a5; font-weight: 600;
}
.terra-error-detail {
    background: rgba(184,50,48,0.08);
    border-left: 3px solid var(--error);
    padding: 0.6rem 0.8rem; margin: 0.4rem 0;
    border-radius: 0 8px 8px 0;
    color: #fda4af; font-size: 0.85rem;
}
.terra-hint { color: var(--syntax-fn); font-size: 0.8rem; margin-top: 0.2rem; }

/* ═══════ Stats Bar ═══════ */
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem;
    text-align: center;
}
.stat-value { color: var(--primary); font-size: 1.6rem; font-weight: 700; font-family: 'Literata', serif; }
.stat-label { color: var(--text-muted); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; }

/* ═══════ Code Block ═══════ */
.terra-code {
    background: rgba(0,0,0,0.4);
    border: 1px solid var(--border);
    border-radius: 10px; padding: 0.8rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem; color: var(--text-primary);
    overflow-x: auto; white-space: pre;
}

/* ═══════ Tree Display ═══════ */
.terra-tree {
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(74,124,89,0.25);
    border-radius: 10px; padding: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem; line-height: 1.6;
    color: var(--text-primary); white-space: pre; overflow-x: auto;
}

/* ═══════ AI Panel ═══════ */
.ai-panel {
    background: rgba(18,20,22,0.6);
    backdrop-filter: blur(40px);
    border: 1px solid var(--border);
    border-radius: 16px; overflow: hidden;
    position: relative;
}
.ai-panel::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(74,124,89,0.5), transparent);
}
.ai-header {
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 12px;
}
.ai-logo {
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(135deg, #1c2e21, var(--bg-dark));
    border: 1px solid rgba(74,124,89,0.3);
    display: flex; align-items: center; justify-content: center;
    color: var(--primary);
}
.ai-name { font-family: 'Literata', serif; font-weight: 700; color: white; font-size: 1.1rem; }
.ai-status { color: rgba(74,124,89,0.8); font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; }

/* ═══════ Syntax Highlighting ═══════ */
.syn-kw { color: var(--syntax-kw); font-weight: 700; }
.syn-str { color: var(--syntax-str); }
.syn-num { color: var(--syntax-num); }
.syn-fn { color: var(--syntax-fn); }
.syn-id { color: var(--text-primary); }
.syn-op { color: var(--syntax-op); }
.syn-sym { color: var(--text-muted); }

/* ═══════ Sidebar ═══════ */
[data-testid="stSidebar"] {
    background: var(--bg-dark) !important;
    border-right: 1px solid var(--border) !important;
}

/* ═══════ Buttons ═══════ */
div.stButton > button:first-child {
    background: var(--primary) !important;
    color: white !important; border: none !important;
    padding: 0.5rem 2rem !important; font-size: 0.95rem !important;
    font-weight: 700 !important; border-radius: 12px !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 12px var(--green-glow) !important;
    font-family: 'Nunito Sans', sans-serif !important;
}
div.stButton > button:first-child:hover {
    background: #5a8c69 !important;
    box-shadow: 0 6px 20px var(--green-glow) !important;
}

/* ═══════ Expander ═══════ */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    font-family: 'Literata', serif !important;
    color: var(--text-primary) !important;
}

/* ═══════ Tables ═══════ */
div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* ═══════ Scrollbar ═══════ */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(74,124,89,0.3); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(74,124,89,0.5); }

/* ═══════ Mobile ═══════ */
@media (max-width: 768px) {
    .terra-header h1 { font-size: 1.1rem !important; }
    .terra-card { padding: 0.8rem; }
    .terra-code { font-size: 0.75rem; }
    .terra-tree { font-size: 0.7rem; }
    .bento-grid { grid-template-columns: 1fr; }
}

/* ═══════ Divider ═══════ */
hr { border-color: var(--border) !important; }
</style>
"""
