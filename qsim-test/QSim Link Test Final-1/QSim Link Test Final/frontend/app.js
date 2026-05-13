// --- Configuration & Constants ---
const API_BASE = '/api';
const EXAMPLES = {
    bell: `OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[2] q;\nbit[2] c;\n\nh q[0];\ncx q[0], q[1];\nc = measure q;`,
    ghz: `OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[3] q;\nbit[3] c;\n\nh q[0];\ncx q[0], q[1];\ncx q[1], q[2];\nc = measure q;`,
    qft: `OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[4] q;\nbit[4] c;\n\nh q[0];\ncp(pi/2) q[1], q[0];\nh q[1];\ncp(pi/4) q[2], q[0];\ncp(pi/2) q[2], q[1];\nh q[2];\ncp(pi/8) q[3], q[0];\ncp(pi/4) q[3], q[1];\ncp(pi/2) q[3], q[2];\nh q[3];\nc = measure q;`,
    bv: `OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[4] q;\nbit[3] c;\n\n// Secret string s = 101\nx q[3];\nh q;\ncx q[0], q[3];\ncx q[2], q[3];\nh q;\nc = measure q[0:2];`
};

const DEFAULT_PYTHON = `import time
import cirq
import qcanvas
import fastqsim

client = fastqsim.init()

q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit(cirq.H(q0), cirq.CNOT(q0, q1))
qasm = qcanvas.compile(circuit, framework='cirq')
job = client.run(qasm, shots=2048, asynchronous=False)
result = job.result()

print(job.job_id, job.status.value)
print(result.counts)
`;

let editor;
let pythonEditor;
let currentJobId = null;
let timerInterval = null;
let startTime = null;

// --- Initialization ---

require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' } });
require(['vs/editor/editor.main'], function () {
    const common = {
        theme: 'vs-dark',
        automaticLayout: true,
        fontSize: 14,
        fontFamily: 'JetBrains Mono',
        minimap: { enabled: false },
        padding: { top: 16 }
    };
    editor = monaco.editor.create(document.getElementById('editor-container'), {
        ...common,
        value: EXAMPLES.bell,
        language: 'cpp',
    });
    pythonEditor = monaco.editor.create(document.getElementById('python-editor-container'), {
        ...common,
        value: DEFAULT_PYTHON,
        language: 'python',
    });
    syncEditorPanels();
    checkHealth();
});

// --- UI Logic ---

// Run mode: OpenQASM (HTTP) vs Python on session pod (kernel WebSocket via server)
document.querySelectorAll('input[name="run-mode"]').forEach((r) => {
    r.addEventListener('change', syncEditorPanels);
});

function isPodMode() {
    const r = document.querySelector('input[name="run-mode"]:checked');
    return r && r.value === 'pod';
}

function syncEditorPanels() {
    const pod = isPodMode();
    document.getElementById('editor-wrap-qasm').style.display = pod ? 'none' : 'flex';
    document.getElementById('editor-wrap-python').style.display = pod ? 'flex' : 'none';
    document.getElementById('editor-panel-title').textContent = pod ? 'Python (user pod)' : 'OpenQASM 3.0';
    document.getElementById('example-select').disabled = pod;
    ['backend-select', 'sim-type-select', 'shots-range', 'job-name', 'seed', 'device-select'].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.disabled = pod;
    });
    requestAnimationFrame(() => {
        if (editor) editor.layout();
        if (pythonEditor) pythonEditor.layout();
    });
}

// Tabs
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');
        
        if (tab.dataset.tab === 'history') fetchHistory();
    });
});

// Shots Range
const shotsRange = document.getElementById('shots-range');
const shotsVal = document.getElementById('shots-val');
shotsRange.addEventListener('input', (e) => {
    shotsVal.textContent = e.target.value;
});

// Examples
document.getElementById('example-select').addEventListener('change', (e) => {
    if (isPodMode()) return;
    editor.setValue(EXAMPLES[e.target.value]);
});

// Run Button
document.getElementById('run-btn').addEventListener('click', runSimulation);

// Cancel Button
document.getElementById('cancel-btn').addEventListener('click', cancelJob);

// --- API Functions ---

async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        const data = await res.json();
        const dot = document.getElementById('connection-dot');
        const text = document.getElementById('connection-text');
        
        if (data.status === 'ok') {
            dot.classList.add('connected');
            text.textContent = data.sdk_initialized ? `Connected: ${data.user_id}` : "SDK Init Failed";
        }
    } catch (e) {
        showToast("Backend unreachable. Start the Flask server.", "error");
    }
}

async function runSimulation() {
    if (isPodMode()) {
        await runPodPython();
        return;
    }

    const runBtn = document.getElementById('run-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const dot = document.getElementById('connection-dot');
    
    const payload = {
        circuit: editor.getValue(),
        backend: document.getElementById('backend-select').value,
        simulation_type: document.getElementById('sim-type-select').value,
        shots: parseInt(shotsRange.value),
        job_name: document.getElementById('job-name').value || "Unnamed Job",
        seed: document.getElementById('seed').value ? parseInt(document.getElementById('seed').value) : null,
        device: document.getElementById('device-select').value,
        asynchronous: false
    };

    try {
        setRunningState(true);
        const res = await fetch(`${API_BASE}/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const job = await res.json();
        if (job.error) throw new Error(job.error);

        // Synchronous run (asynchronous: false) — backend returns counts immediately, same as job.result() in Python.
        if (job.counts != null) {
            renderResults(job);
            setRunningState(false);
            showToast("Simulation Complete!");
            return;
        }

        currentJobId = job.job_id;
        pollJobStatus(currentJobId);
        
    } catch (e) {
        setRunningState(false);
        showToast(e.message, "error");
    }
}

async function runPodPython() {
    const code = pythonEditor.getValue();
    try {
        setRunningState(true);
        const res = await fetch(`${API_BASE}/kernel/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, timeout: 300 }),
        });
        const text = await res.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch {
            data = { error: text || 'Non-JSON response', ok: false };
        }
        if (!res.ok) {
            const msg = [data.error, data.traceback].filter(Boolean).join('\n\n');
            throw new Error(msg || res.statusText);
        }
        renderPodOutput(data);
        document.querySelector('[data-tab="pod"]').click();
        setRunningState(false);
        showToast(data.ok ? 'Pod execution finished' : 'Pod execution finished with errors', data.ok ? 'success' : 'error');
    } catch (e) {
        setRunningState(false);
        showToast(e.message, 'error');
        document.getElementById('pod-output').textContent = e.message;
        document.querySelector('[data-tab="pod"]')?.click();
    }
}

async function pollJobStatus(jobId) {
    try {
        const res = await fetch(`${API_BASE}/wait/${jobId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ timeout: 300 })
        });
        
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        
        renderResults(data);
        setRunningState(false);
        showToast("Simulation Complete!");
        
    } catch (e) {
        setRunningState(false);
        showToast(e.message, "error");
    }
}

async function cancelJob() {
    if (!currentJobId) return;
    try {
        await fetch(`${API_BASE}/cancel/${currentJobId}`, { method: 'DELETE' });
        showToast("Job Cancellation Requested");
        setRunningState(false);
    } catch (e) {
        showToast(e.message, "error");
    }
}

async function fetchHistory() {
    const list = document.getElementById('history-list');
    list.innerHTML = '<div style="color: var(--text-muted)">Loading history...</div>';
    
    try {
        const res = await fetch(`${API_BASE}/search?limit=10`);
        const jobs = await res.json();
        
        list.innerHTML = '';
        if (jobs.length === 0) {
            list.innerHTML = '<div style="color: var(--text-muted)">No past jobs found.</div>';
            return;
        }

        jobs.forEach(job => {
            const item = document.createElement('div');
            item.className = 'panel-header'; // Reusing header style for rows
            item.style.borderRadius = '4px';
            item.style.cursor = 'pointer';
            item.style.marginBottom = '4px';
            item.innerHTML = `
                <div style="display: flex; flex-direction: column;">
                    <span style="font-weight: 600; font-size: 0.85rem;">${job.job_name}</span>
                    <span style="font-size: 0.7rem; color: var(--text-muted);">${job.job_id.substring(0,8)}... | ${job.backend}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 0.75rem; color: ${job.status === 'completed' ? 'var(--success)' : 'var(--error)'}">${job.status}</span>
                </div>
            `;
            item.onclick = async () => {
                const res = await fetch(`${API_BASE}/job/${job.job_id}`);
                const detail = await res.json();
                renderResults(detail);
                document.querySelector('[data-tab="histogram"]').click();
            };
            list.appendChild(item);
        });
    } catch (e) {
        list.innerHTML = '<div style="color: var(--error)">Failed to load history</div>';
    }
}

// --- Rendering ---

function renderPodOutput(data) {
    const lines = [];
    if (data.stdout) lines.push('--- stdout ---\n' + data.stdout);
    if (data.stderr) lines.push('--- stderr ---\n' + data.stderr);
    if (data.errors && data.errors.length) lines.push('--- kernel errors ---\n' + JSON.stringify(data.errors, null, 2));
    if (data.execute_reply) lines.push('--- execute_reply ---\n' + JSON.stringify(data.execute_reply, null, 2));
    if (data.error) lines.push('--- transport ---\n' + data.error);
    document.getElementById('pod-output').textContent = lines.join('\n\n') || JSON.stringify(data, null, 2);
}

function renderResults(data) {
    // 1. Raw JSON
    document.getElementById('json-output').textContent = JSON.stringify(data, null, 2);
    
    // 2. Histogram
    const histogramDiv = document.getElementById('histogram');
    if (data.counts) {
        const total = Object.values(data.counts).reduce((a, b) => a + b, 0);
        const sorted = Object.entries(data.counts).sort((a, b) => b[1] - a[1]);
        
        histogramDiv.innerHTML = '<div class="histogram"></div>';
        const hist = histogramDiv.querySelector('.histogram');
        
        sorted.forEach(([state, count]) => {
            const percent = ((count / total) * 100).toFixed(1);
            const row = document.createElement('div');
            row.className = 'bar-row';
            row.innerHTML = `
                <div class="bar-label">|${state}⟩</div>
                <div class="bar-container"><div class="bar" style="width: ${percent}%"></div></div>
                <div class="bar-value">${percent}%</div>
            `;
            hist.appendChild(row);
        });
    } else {
        histogramDiv.innerHTML = '<div style="color: var(--error)">No counts available for this result.</div>';
    }

    // 3. Statevector
    const svBody = document.getElementById('sv-body');
    svBody.innerHTML = '';
    if (data.statevector) {
        data.statevector.forEach((amp, i) => {
            // Binary label for state
            const bin = i.toString(2).padStart(Math.log2(data.statevector.length), '0');
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
            tr.innerHTML = `
                <td style="padding: 8px; color: var(--accent);">|${bin}⟩</td>
                <td style="padding: 8px;">${amp}</td>
            `;
            svBody.appendChild(tr);
        });
    } else {
        svBody.innerHTML = '<tr><td colspan="2" style="padding: 20px; color: var(--text-muted); text-align: center;">No statevector data available</td></tr>';
    }
}

// --- Utilities ---

function setRunningState(running) {
    const runBtn = document.getElementById('run-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const timer = document.getElementById('timer');
    const dot = document.getElementById('connection-dot');
    const pod = isPodMode();

    if (running) {
        runBtn.disabled = true;
        runBtn.innerHTML = '<span class="dot running"></span> Running...';
        cancelBtn.style.display = pod ? 'none' : 'block';
        dot.className = 'dot running';
        
        timer.style.display = 'block';
        startTime = Date.now();
        timerInterval = setInterval(updateTimer, 100);
    } else {
        runBtn.disabled = false;
        runBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg> Run Simulation';
        cancelBtn.style.display = 'none';
        dot.className = 'dot connected';
        
        clearInterval(timerInterval);
        currentJobId = null;
    }
}

function updateTimer() {
    const elapsed = Date.now() - startTime;
    const mins = Math.floor(elapsed / 60000).toString().padStart(2, '0');
    const secs = Math.floor((elapsed % 60000) / 1000).toString().padStart(2, '0');
    const ms = Math.floor((elapsed % 1000) / 100).toString();
    document.getElementById('timer').textContent = `${mins}:${secs}.${ms}`;
}

function showToast(msg, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}
