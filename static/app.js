/* app.js — Terra SQL Studio Frontend Logic */

async function compileQuery() {
    const query = document.getElementById('editor').value.trim();
    if (!query) return;

    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('loading').style.display = 'block';
    document.getElementById('statsBar').classList.add('hidden');
    document.getElementById('bentoGrid').classList.add('hidden');
    document.getElementById('detailedResults').classList.add('hidden');

    try {
        const resp = await fetch('/api/compile', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query})
        });
        const data = await resp.json();
        document.getElementById('loading').style.display = 'none';
        renderResults(data);
    } catch (e) {
        document.getElementById('loading').style.display = 'none';
        alert('Compilation error: ' + e.message);
    }
}

function renderResults(d) {
    // Stats
    document.getElementById('statTokens').textContent = d.tokens ? d.tokens.length : 0;
    document.getElementById('statStatus').innerHTML = d.is_valid ? '<span class="text-emerald-400">✓ Valid</span>' : '<span class="text-red-400">✗ Error</span>';
    document.getElementById('statNodes').textContent = d.tree_node_count || 0;
    document.getElementById('statTime').textContent = (d.compile_time_ms || 0).toFixed(1) + 'ms';
    document.getElementById('statsBar').classList.remove('hidden');

    // Token Stream
    const tl = document.getElementById('tokenList');
    tl.innerHTML = '';
    if (d.tokens) {
        d.tokens.forEach(t => {
            const catColor = {KEYWORD:'text-teal-400',IDENTIFIER:'text-stone-300',NUMBER:'text-pink-400',STRING:'text-amber-300',OPERATOR:'text-slate-300',SYMBOL:'text-stone-400'}[t.category] || 'text-stone-300';
            tl.innerHTML += `<div class="flex justify-between"><span class="text-stone-500">[${t.category.substring(0,3)}]</span><span class="${catColor}">${t.value}</span></div>`;
        });
    }

    // Parse Tree (text)
    const tc = document.getElementById('treeContent');
    tc.textContent = d.parse_tree_str || '(no tree)';

    // Symbol Table
    const sc = document.getElementById('symbolContent');
    sc.innerHTML = '';
    if (d.symbol_table && d.symbol_table.length > 0) {
        let html = '<table class="w-full text-left"><thead class="text-stone-500 border-b border-[#ffffff0a]"><tr><th>Symbol</th><th>Type</th><th>Scope</th></tr></thead><tbody class="text-stone-300">';
        d.symbol_table.forEach(s => {
            const typeColor = s.category === 'COLUMN' ? 'text-teal-300' : s.category === 'TABLE' ? 'text-amber-300' : 'text-sky-300';
            html += `<tr><td>${s.name}</td><td class="${typeColor}">${s.category}</td><td>${s.contexts ? s.contexts.join(', ') : ''}</td></tr>`;
        });
        html += '</tbody></table>';
        sc.innerHTML = html;
    }

    document.getElementById('bentoGrid').classList.remove('hidden');

    // Syntax Status
    const ss = document.getElementById('syntaxStatus');
    if (d.is_valid) {
        ss.innerHTML = '<div class="bg-[#4a7c59]/10 border border-[#4a7c59]/40 rounded-lg p-3 text-[#8ecf9e] font-bold flex items-center gap-2"><span class="material-symbols-outlined">check_circle</span>Query is syntactically VALID</div>';
    } else {
        let errHtml = `<div class="bg-red-500/10 border border-red-500/40 rounded-lg p-3 text-red-300 font-bold mb-2"><span class="material-symbols-outlined align-middle">error</span> ${d.error_count} Syntax Error(s)</div>`;
        if (d.errors) {
            d.errors.forEach(e => {
                errHtml += `<div class="bg-red-500/5 border-l-3 border-red-500 pl-3 py-2 text-sm text-red-200 mb-1"><strong>${e.message}</strong>${e.token_value ? ` near '${e.token_value}'` : ''}${e.hint ? `<div class="text-sky-400 text-xs mt-1">💡 ${e.hint}</div>` : ''}</div>`;
            });
        }
        ss.innerHTML = errHtml;
    }

    // CFG Rules
    const cfgSec = document.getElementById('cfgSection');
    if (d.grammar_trace && d.grammar_trace.length > 0) {
        cfgSec.classList.remove('hidden');
        let rulesHtml = '<div class="bg-black/40 rounded p-2 font-mono text-xs text-stone-300 whitespace-pre overflow-auto max-h-[200px]">' + (d.grammar_rules || []).join('\n') + '</div>';
        let traceHtml = '<div class="bg-black/40 rounded p-2 font-mono text-xs text-stone-300 whitespace-pre overflow-auto max-h-[200px]">';
        d.grammar_trace.forEach((t, i) => { traceHtml += `${i+1}. ${t.production}\n`; });
        traceHtml += '</div>';
        document.getElementById('cfgContent').innerHTML = rulesHtml + traceHtml;
    } else { cfgSec.classList.add('hidden'); }

    // FIRST/FOLLOW
    const ffSec = document.getElementById('ffSection');
    if (d.first_sets && d.first_sets.length > 0) {
        ffSec.classList.remove('hidden');
        let fHtml = '<div class="bg-black/40 rounded p-2 font-mono text-xs overflow-auto max-h-[200px]"><table class="w-full"><thead class="text-stone-500"><tr><th class="text-left">Non-Terminal</th><th class="text-left">FIRST</th></tr></thead><tbody class="text-stone-300">';
        d.first_sets.forEach(r => { fHtml += `<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`; });
        fHtml += '</tbody></table></div>';
        let foHtml = '<div class="bg-black/40 rounded p-2 font-mono text-xs overflow-auto max-h-[200px]"><table class="w-full"><thead class="text-stone-500"><tr><th class="text-left">Non-Terminal</th><th class="text-left">FOLLOW</th></tr></thead><tbody class="text-stone-300">';
        d.follow_sets.forEach(r => { foHtml += `<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`; });
        foHtml += '</tbody></table></div>';
        document.getElementById('ffContent').innerHTML = fHtml + foHtml;
    } else { ffSec.classList.add('hidden'); }

    // Parsing Table
    const ptSec = document.getElementById('ptSection');
    if (d.parsing_table && d.parsing_table.length > 0) {
        ptSec.classList.remove('hidden');
        let ptHtml = '<table class="w-full font-mono text-xs text-stone-300"><thead class="text-stone-500"><tr>';
        Object.keys(d.parsing_table[0]).forEach(k => { ptHtml += `<th class="text-left px-2 py-1">${k}</th>`; });
        ptHtml += '</tr></thead><tbody>';
        d.parsing_table.forEach(row => {
            ptHtml += '<tr class="border-t border-[#ffffff0a]">';
            Object.values(row).forEach(v => { ptHtml += `<td class="px-2 py-1">${v}</td>`; });
            ptHtml += '</tr>';
        });
        ptHtml += '</tbody></table>';
        document.getElementById('ptContent').innerHTML = ptHtml;
    } else { ptSec.classList.add('hidden'); }

    // SVG Tree
    const svgSec = document.getElementById('svgTreeSection');
    if (d.parse_tree_svg) {
        svgSec.classList.remove('hidden');
        document.getElementById('svgTreeContent').innerHTML = d.parse_tree_svg;
    } else { svgSec.classList.add('hidden'); }

    // Intermediate Code
    const ic = document.getElementById('intermediateSection');
    let icHtml = '';
    if (d.is_valid && d.postfix) {
        icHtml += '<details class="step-card"><summary class="cursor-pointer flex items-center gap-2 text-pink-400 font-headline text-sm font-bold"><span class="material-symbols-outlined text-sm">swap_horiz</span>POSTFIX NOTATION</summary>';
        icHtml += `<div class="mt-3 bg-black/40 rounded p-3 font-mono text-sm text-stone-200">${d.postfix}</div></details>`;
    }
    if (d.is_valid && d.tac_string) {
        icHtml += '<details class="step-card"><summary class="cursor-pointer flex items-center gap-2 text-cyan-400 font-headline text-sm font-bold"><span class="material-symbols-outlined text-sm">description</span>THREE ADDRESS CODE</summary>';
        icHtml += `<div class="mt-3 bg-black/40 rounded p-3 font-mono text-xs text-stone-200 whitespace-pre">${d.tac_string}</div></details>`;
    }
    if (d.is_valid && d.quadruples && d.quadruples.length > 0) {
        icHtml += '<details class="step-card"><summary class="cursor-pointer flex items-center gap-2 text-yellow-400 font-headline text-sm font-bold"><span class="material-symbols-outlined text-sm">grid_view</span>QUADRUPLES & TRIPLES</summary>';
        icHtml += '<div class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">';
        icHtml += '<div class="bg-black/40 rounded p-2 font-mono text-xs overflow-auto"><table class="w-full"><thead class="text-stone-500"><tr><th>#</th><th>Op</th><th>Arg1</th><th>Arg2</th><th>Result</th></tr></thead><tbody class="text-stone-300">';
        d.quadruples.forEach(q => { icHtml += `<tr><td>${q[0]}</td><td>${q[1]}</td><td>${q[2]}</td><td>${q[3]}</td><td>${q[4]}</td></tr>`; });
        icHtml += '</tbody></table></div>';
        if (d.triples && d.triples.length > 0) {
            icHtml += '<div class="bg-black/40 rounded p-2 font-mono text-xs overflow-auto"><table class="w-full"><thead class="text-stone-500"><tr><th>#</th><th>Op</th><th>Arg1</th><th>Arg2</th></tr></thead><tbody class="text-stone-300">';
            d.triples.forEach(t => { icHtml += `<tr><td>${t[0]}</td><td>${t[1]}</td><td>${t[2]}</td><td>${t[3]}</td></tr>`; });
            icHtml += '</tbody></table></div>';
        }
        icHtml += '</div></details>';
    }
    ic.innerHTML = icHtml;

    document.getElementById('detailedResults').classList.remove('hidden');
}

async function formatQuery() {
    const editor = document.getElementById('editor');
    try {
        const resp = await fetch('/api/format', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: editor.value})
        });
        const data = await resp.json();
        editor.value = data.formatted;
    } catch (e) {}
}

async function sendChat() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';

    const container = document.getElementById('chatMessages');
    // User message
    container.innerHTML += `<div class="flex gap-2 flex-row-reverse"><div class="bg-[#24272a]/60 rounded-2xl rounded-tr-sm p-2.5 text-sm text-stone-200 border border-[#ffffff0a] max-w-[85%]">${msg}</div></div>`;
    container.scrollTop = container.scrollHeight;

    // Loading dots
    container.innerHTML += `<div id="chatLoading" class="flex gap-2"><div class="w-6 h-6 rounded-md bg-[#1c2e21] border border-[#4a7c59]/30 flex items-center justify-center shrink-0"><span class="material-symbols-outlined text-[12px] text-[#4a7c59]">auto_awesome</span></div><div class="bg-[#1c2e21]/50 rounded-2xl rounded-tl-sm p-2.5 border border-[#4a7c59]/20 flex items-center gap-1"><div class="w-1.5 h-1.5 bg-[#4a7c59] rounded-full animate-bounce"></div><div class="w-1.5 h-1.5 bg-[#4a7c59] rounded-full animate-bounce" style="animation-delay:.1s"></div><div class="w-1.5 h-1.5 bg-[#4a7c59] rounded-full animate-bounce" style="animation-delay:.2s"></div></div></div>`;

    const apiKey = document.getElementById('apiKey').value;
    const messages = [{role: 'user', content: msg}];

    try {
        const resp = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({messages, api_key: apiKey})
        });
        const data = await resp.json();
        const el = document.getElementById('chatLoading');
        if (el) el.remove();

        container.innerHTML += `<div class="flex gap-2"><div class="w-6 h-6 rounded-md bg-[#1c2e21] border border-[#4a7c59]/30 flex items-center justify-center shrink-0 mt-1"><span class="material-symbols-outlined text-[12px] text-[#4a7c59]">auto_awesome</span></div><div class="bg-[#1c2e21]/50 rounded-2xl rounded-tl-sm p-2.5 text-sm text-stone-200 border border-[#4a7c59]/20 max-w-[85%]">${data.response.replace(/\n/g,'<br>')}</div></div>`;
        container.scrollTop = container.scrollHeight;
    } catch (e) {
        const el = document.getElementById('chatLoading');
        if (el) el.remove();
        container.innerHTML += `<div class="text-red-400 text-xs p-2">Error: ${e.message}</div>`;
    }
}

// Ctrl+Enter to compile
document.getElementById('editor').addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { compileQuery(); }
});
