(() => {
  function toDevProxyWsUrl(rawWsUrl) {
    if (!rawWsUrl) return '';
    try {
      const parsed = new URL(rawWsUrl);
      const isDevServer = window.location.port === '5173';
      if (!isDevServer) return rawWsUrl;

      const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const local = new URL(`${proto}//${window.location.host}${parsed.pathname}${parsed.search || ''}`);
      return local.toString();
    } catch {
      return rawWsUrl;
    }
  }

  // The API base can point directly at FastQubit or at a local dev proxy.
  // No BFF-specific behavior is assumed in this frontend.
  const injectedApiBase = typeof window !== 'undefined'
    ? String(window.__QOS_API_BASE || window.FASTQUBIT_API_BASE || '').trim()
    : '';
  const persistedApiBase = String(localStorage.getItem('qos_api_base') || '').trim();
  const isDevServer = typeof window !== 'undefined' && window.location.port === '5173';
  const rawApiBase = (isDevServer
    ? (injectedApiBase || '/api')
    : (injectedApiBase || persistedApiBase || '/api')).replace(/\/+$/, '');
  const API_BASE = rawApiBase;
  try {
    localStorage.setItem('qos_api_base', API_BASE);
  } catch { }
  const SESSION_TERMINAL = new Set(['terminated', 'failed', 'cancelled']);
  const JOB_TERMINAL = new Set(['completed', 'failed', 'cancelled']);
  const THEME_KEY = 'qos_theme';
  const AUTH_KEY = 'qos_direct_auth';
  const PY_MONACO_MARKER_OWNER = 'qos-python-console';

  const appState = typeof state !== 'undefined' ? state : {
    userId: null,
    integratorApiKey: null,
    endUserId: null,
    sessionToken: null,
    activeSession: null,
    jobs: [],
    sessions: [],
    currentJobId: null,
    monitorInterval: null,
    countdownInterval: null,
    historyFilter: 'all',
    pyWs: null,
    pyCurrentMsgId: null,
    pyWsToken: null,
    pyEditor: null,
    pyMonaco: null,
    pyCompletionRegistered: false,
    pyLintMarkers: [],
    pyRuntimeMarkers: [],
    pyLintTimer: null,
    pySawExecutionError: false
  };

  // Identity is managed explicitly by the frontend in direct-auth mode.
  appState.userId = appState.userId || null;
  appState.integratorApiKey = appState.integratorApiKey || null;
  appState.endUserId = appState.endUserId || null;
  appState.sessionToken = appState.sessionToken || null;
  appState.jobs = Array.isArray(appState.jobs) ? appState.jobs : [];
  appState.sessions = Array.isArray(appState.sessions) ? appState.sessions : [];
  appState.historyFilter = appState.historyFilter || 'all';

  const templates = {
    bell: `OPENQASM 3.0;\ninclude "stdgates.inc";\n\nqubit[2] q;\nbit[2] c;\n\nh q[0];\ncx q[0], q[1];\nc = measure q;`,
    ghz: `OPENQASM 3.0;\ninclude "stdgates.inc";\n\nqubit[3] q;\nbit[3] c;\n\nh q[0];\ncx q[0], q[1];\ncx q[0], q[2];\nc = measure q;`,
    qft: `OPENQASM 3.0;\ninclude "stdgates.inc";\n\nqubit[4] q;\nbit[4] c;\n\nh q[0];\ncp(pi/2) q[1], q[0];\ncp(pi/4) q[2], q[0];\ncp(pi/8) q[3], q[0];\nh q[1];\ncp(pi/2) q[2], q[1];\ncp(pi/4) q[3], q[1];\nh q[2];\ncp(pi/2) q[3], q[2];\nh q[3];\nc = measure q;`,
    grover: `OPENQASM 3.0;\ninclude "stdgates.inc";\n\nqubit[2] q;\nbit[2] c;\n\nh q[0];\nh q[1];\ncz q[0], q[1];\nh q[0];\nh q[1];\ncz q[0], q[1];\nh q[0];\nh q[1];\nc = measure q;`
  };

  function $(id) {
    return document.getElementById(id);
  }

  function readStoredAuth() {
    try {
      const raw = localStorage.getItem(AUTH_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== 'object') return null;
      return {
        apiKey: String(parsed.apiKey || parsed.api_key || '').trim(),
        endUserId: String(parsed.endUserId || parsed.end_user_id || '').trim()
      };
    } catch {
      return null;
    }
  }

  function persistStoredAuth() {
    try {
      const payload = {
        apiKey: appState.integratorApiKey || '',
        endUserId: appState.endUserId || ''
      };
      localStorage.setItem(AUTH_KEY, JSON.stringify(payload));
    } catch { }
  }

  function clearStoredAuth() {
    try {
      localStorage.removeItem(AUTH_KEY);
    } catch { }
  }

  function setDirectAuth({ apiKey, endUserId }) {
    appState.integratorApiKey = String(apiKey || '').trim();
    appState.endUserId = String(endUserId || '').trim();
    appState.userId = appState.endUserId;
    appState.sessionToken = null;
    appState.activeSession = null;
    appState.jobs = [];
    appState.sessions = [];
    appState.currentJobId = null;
    persistStoredAuth();
    setSidebarUser();
  }

  function clearDirectAuth() {
    appState.integratorApiKey = null;
    appState.endUserId = null;
    appState.userId = null;
    appState.sessionToken = null;
    appState.activeSession = null;
    appState.currentJobId = null;
    appState.pyWsToken = null;
    appState.pyCurrentMsgId = null;
    appState.pySawExecutionError = false;
    appState.jobs = [];
    appState.sessions = [];
    clearStoredAuth();
  }

  function syncSessionState(sessionLike) {
    if (!sessionLike) return null;
    const sess = normalizeSession(sessionLike);
    if (sess.session_token) {
      appState.sessionToken = sess.session_token;
    }
    if (sess.ws_token) {
      appState.pyWsToken = sess.ws_token;
    }
    if (sess.id) {
      const idx = appState.sessions.findIndex((s) => s.id === sess.id);
      if (idx >= 0) appState.sessions[idx] = { ...appState.sessions[idx], ...sess };
      else appState.sessions.unshift(sess);
    }
    appState.activeSession = getActiveSession();
    if (!appState.activeSession && sess.id) {
      appState.activeSession = sess;
    }
    return sess;
  }

  async function ensureActiveSessionToken(session = null) {
    const target = session || appState.activeSession;
    if (!target || !target.id) return '';
    if (appState.sessionToken && (!appState.activeSession || appState.activeSession.id === target.id)) {
      return appState.sessionToken;
    }
    if (target.session_token) {
      appState.sessionToken = target.session_token;
      return target.session_token;
    }
    if (!appState.integratorApiKey || !appState.endUserId) return '';
    const resp = await apiRequest(`/sessions/${encodeURIComponent(target.id)}/reconnect-token`, 'POST', {}, 'integrator');
    const sess = syncSessionState({ ...target, ...resp });
    return (sess && sess.session_token) || appState.sessionToken || '';
  }

  function getActiveSession() {
    return appState.sessions.find((s) => !SESSION_TERMINAL.has((s.state || '').toLowerCase())) || null;
  }

  function normalizeSession(s) {
    return {
      ...s,
      id: s.session_id,
      user_id: s.end_user_id || s.user_id || null,
      end_user_id: s.end_user_id || s.user_id || null,
      started_at: s.created_at || s.started_at || null,
      ws_url: s && s.ws_url ? String(s.ws_url) : s.ws_url,
      ws_token: s && s.ws_token ? String(s.ws_token) : '',
      session_token: s && s.session_token ? String(s.session_token) : ''
    };
  }

  function getDurationMs(job) {
    if (job.execution_started_at && job.execution_finished_at) {
      const start = new Date(job.execution_started_at).getTime();
      const end = new Date(job.execution_finished_at).getTime();
      if (!Number.isNaN(start) && !Number.isNaN(end) && end >= start) return end - start;
    }
    if (typeof job.execution_time_seconds === 'number' && Number.isFinite(job.execution_time_seconds) && job.execution_time_seconds >= 0) {
      return job.execution_time_seconds * 1000;
    }
    return null;
  }

  function normalizeJob(j) {
    const profile = j && j.profile ? j.profile : {};
    const tags = j && j.tags && typeof j.tags === 'object' && !Array.isArray(j.tags) ? j.tags : {};
    return {
      ...j,
      id: j.job_id,
      user_id: j.end_user_id || j.user_id || null,
      end_user_id: j.end_user_id || j.user_id || null,
      submitted_at: j.created_at,
      duration_ms: getDurationMs(j),
      tags,
      tag_list: Object.keys(tags),
      qubits: profile.qubit_count !== undefined ? profile.qubit_count : null,
      depth: profile.depth !== undefined ? profile.depth : null,
      gate_count: profile.gate_count !== undefined ? profile.gate_count : null,
      two_qubit_gate_count: profile.two_qubit_gate_count !== undefined ? profile.two_qubit_gate_count : null
    };
  }

  async function apiRequest(path, method = 'GET', body = null, auth = 'none') {
    const headers = { Accept: 'application/json' };
    if (body !== null) headers['Content-Type'] = 'application/json';

    if (auth === 'integrator') {
      const apiKey = appState.integratorApiKey || readStoredAuth()?.apiKey || '';
      const endUserId = appState.endUserId || readStoredAuth()?.endUserId || '';
      if (!apiKey || !endUserId) throw new Error('Missing direct auth credentials');
      headers.Authorization = `Bearer ${apiKey}`;
      headers['X-End-User-Id'] = endUserId;
    } else if (auth === 'pod') {
      const token = await ensureActiveSessionToken();
      if (!token) throw new Error('Missing session token. Start a session first.');
      headers.Authorization = `Bearer ${token}`;
    }

    const resp = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body !== null ? JSON.stringify(body) : undefined
    });

    const isJson = (resp.headers.get('content-type') || '').includes('application/json');
    const data = isJson ? await resp.json() : null;

    if (!resp.ok) {
      const message = (data && (data.detail || data.message)) || `${resp.status} ${resp.statusText}`;
      const err = new Error(message);
      err.status = resp.status;
      err.data = data;
      throw err;
    }

    return data;
  }

  async function updateHealth() {
    try {
      await apiRequest('/health', 'GET', null, 'none');
      $('sidebarHealthDot').className = 'dot dot-green';
      $('sidebarHealthText').textContent = 'API Online';
    } catch {
      $('sidebarHealthDot').className = 'dot dot-red';
      $('sidebarHealthText').textContent = 'API Offline';
    }
  }

  function setSidebarUser() {
    const uid = appState.userId || '—';
    $('sidebarUserId').textContent = uid;
    const avatarEl = $('sidebarAvatarChar');
    if (uid === '—') {
      avatarEl.innerHTML = '<i class="bi bi-person-fill"></i>';
    } else {
      avatarEl.textContent = uid.charAt(0).toUpperCase();
    }
  }

  function badgeHtmlSafe(status) {
    return typeof badgeHtml === 'function'
      ? badgeHtml((status || '').toLowerCase())
      : `<span class="badge badge-gray">${String(status || 'unknown').toUpperCase()}</span>`;
  }

  function toEpochMs(iso) {
    if (!iso) return null;
    const ms = new Date(iso).getTime();
    return Number.isNaN(ms) ? null : ms;
  }

  function formatDurationMs(durationMs) {
    if (durationMs === null || durationMs === undefined || Number.isNaN(durationMs)) return '—';
    const totalMs = Math.max(0, Math.round(durationMs));
    const ms = totalMs % 1000;
    const totalSec = Math.floor(totalMs / 1000);
    const sec = totalSec % 60;
    const min = Math.floor(totalSec / 60);
    return `${min}m ${sec}s ${ms}ms`;
  }

  function formatElapsedSince(iso) {
    const ts = toEpochMs(iso);
    if (ts === null) return '—';
    return formatDurationMs(Date.now() - ts);
  }

  function formatRemainingUntil(iso) {
    const ts = toEpochMs(iso);
    if (ts === null) return '—';
    return formatDurationMs(ts - Date.now());
  }

  function formatOffsetFrom(startIso, endIso) {
    const start = toEpochMs(startIso);
    const end = toEpochMs(endIso);
    if (start === null || end === null) return '—';
    return formatDurationMs(end - start);
  }

  function formatDateTime(iso) {
    return formatRemainingUntil(iso);
  }

  function formatTimeOnly(iso) {
    return formatElapsedSince(iso);
  }

  function timeAgoSafe(iso) {
    return formatElapsedSince(iso);
  }

  function parseTagInput(raw) {
    const text = String(raw || '').trim();
    if (!text) return {};
    const parts = text.split(',').map((part) => part.trim()).filter(Boolean);
    const tags = {};
    parts.forEach((tag) => { tags[tag] = true; });
    return tags;
  }

  function formatSecondsAsDuration(seconds) {
    if (typeof seconds !== 'number' || !Number.isFinite(seconds)) return '—';
    return formatDurationMs(seconds * 1000);
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function compactIsoTimestamp() {
    return new Date().toISOString().replace(/[:.]/g, '-');
  }

  function downloadJsonFile(filename, payload) {
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function buildJobTimingBreakdown(job) {
    const queuedAt = job.queue_enqueued_at || job.queued_at || null;
    const dequeuedAt = job.queue_dequeued_at || job.started_at || null;
    const timingBase = job.created_at || queuedAt || dequeuedAt || job.execution_started_at || null;
    const points = [
      { field: 'created_at', label: 'Created', ts: job.created_at },
      { field: 'queue_enqueued_at', label: 'Queued', ts: queuedAt },
      { field: 'queue_dequeued_at', label: 'Dequeued', ts: dequeuedAt },
      { field: 'execution_started_at', label: 'Exec Start', ts: job.execution_started_at },
      { field: 'execution_finished_at', label: 'Exec End', ts: job.execution_finished_at },
      { field: 'completed_at', label: 'Completed', ts: job.completed_at },
      { field: 'updated_at', label: 'Updated', ts: job.updated_at }
    ];

    let prevTs = null;
    const rows = points.map((point) => {
      const ts = point.ts;
      const fromStartMs = ts && timingBase ? (toEpochMs(ts) - toEpochMs(timingBase)) : null;
      const deltaMs = ts && prevTs ? (toEpochMs(ts) - toEpochMs(prevTs)) : null;
      if (ts) prevTs = ts;
      return {
        field: point.field,
        label: point.label,
        timestamp: ts,
        from_start_ms: Number.isFinite(fromStartMs) ? fromStartMs : null,
        since_previous_ms: Number.isFinite(deltaMs) ? deltaMs : null
      };
    });

    return {
      job_id: job.id || job.job_id,
      status: job.status || null,
      base_timestamp: timingBase,
      duration_ms: getDurationMs(job),
      rows
    };
  }

  function formatNumeric(value, suffix = '') {
    if (value === null || value === undefined || Number.isNaN(value)) return '—';
    if (typeof value !== 'number' || !Number.isFinite(value)) return '—';
    const rounded = Number.isInteger(value) ? String(value) : value.toFixed(3);
    return `${rounded}${suffix}`;
  }

  function formatJsonValue(value) {
    if (value === null || value === undefined) return '—';
    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value);
    }
  }

  function formatSchemaFieldValue(field, value) {
    const dateFields = new Set([
      'created_at',
      'updated_at',
      'queue_enqueued_at',
      'queue_dequeued_at',
      'queued_at',
      'started_at',
      'execution_started_at',
      'execution_finished_at',
      'completed_at',
      'result_url_expires_at'
    ]);
    if (dateFields.has(field)) {
      if (field === 'result_url_expires_at') return formatRemainingUntil(value);
      return formatElapsedSince(value);
    }
    if (field === 'execution_time_seconds' || field === 'cpu_seconds_total') {
      return formatSecondsAsDuration(value);
    }
    if (field === 'peak_memory_mb' || field === 'billing_avg_memory_mb' || field === 'billing_memory_headroom_mb') {
      return formatNumeric(value, ' MB');
    }
    if (field === 'billing_cpu_millicore_seconds') {
      return formatNumeric(value, ' mCPU·s');
    }
    if (field === 'billing_memory_gb_seconds') {
      return formatNumeric(value, ' GB·s');
    }
    if (typeof value === 'boolean') return value ? 'true' : 'false';
    if (typeof value === 'number') return String(value);
    if (value && typeof value === 'object') return formatJsonValue(value);
    if (value === null || value === undefined || value === '') return '—';
    return String(value);
  }

  const JOB_SCHEMA_SECTIONS_BY_VIEW = {
    monitor: [
      {
        title: 'Run Configuration',
        subtitle: 'How this job was executed',
        fields: ['job_name', 'backend', 'simulation_type', 'device', 'shots']
      },
      {
        title: 'Runtime Metrics',
        subtitle: 'Performance and resource use',
        fields: ['execution_time_seconds', 'cpu_seconds_total', 'billing_cpu_millicore_seconds', 'peak_memory_mb', 'billing_avg_memory_mb', 'billing_memory_gb_seconds', 'billing_memory_headroom_mb']
      },
      {
        title: 'Timing Insights',
        subtitle: 'Queue and execution timeline from scheduler/worker telemetry',
        fields: ['created_at', 'queue_enqueued_at', 'queue_dequeued_at', 'execution_started_at', 'execution_finished_at', 'completed_at', 'updated_at']
      },
      {
        title: 'Billing & Infra',
        subtitle: 'Infra telemetry and artifacts',
        fields: ['error_message', 'pod_name', 'billing_psutil_available', 'has_external_artifact', 'result_url_expires_at']
      },
      {
        title: 'Advanced Inputs',
        subtitle: 'Optional payload sent at submit time',
        fields: ['options', 'metadata', 'tags', 'resource_estimate', 'seed']
      }
    ],
    results: [
      {
        title: 'Execution Metrics',
        subtitle: 'Run-level metrics for this result',
        fields: ['execution_time_seconds', 'cpu_seconds_total', 'billing_cpu_millicore_seconds', 'peak_memory_mb', 'billing_avg_memory_mb', 'billing_memory_gb_seconds', 'billing_memory_headroom_mb', 'billing_psutil_available']
      },
      {
        title: 'Result Metadata',
        subtitle: 'Result payload and artifact references',
        fields: ['error_message', 'result_metadata', 'has_external_artifact', 'result_url_expires_at', 'pod_name']
      },
      {
        title: 'Submission Inputs',
        subtitle: 'Advanced options used for this run',
        fields: ['options', 'metadata', 'tags', 'resource_estimate', 'seed']
      }
    ]
  };

  const HIDE_IF_EMPTY_FIELDS = new Set([
    'seed',
    'tags',
    'metadata',
    'options',
    'resource_estimate',
    'result_metadata',
    'result_url_expires_at',
    'error_message',
    'pod_name'
  ]);

  function getJobSchemaFieldMap(job) {
    const profileValue = job.profile || {
      qubit_count: job.qubits !== undefined && job.qubits !== null ? job.qubits : null,
      depth: job.depth !== undefined && job.depth !== null ? job.depth : null,
      gate_count: job.gate_count !== undefined && job.gate_count !== null ? job.gate_count : null,
      two_qubit_gate_count: job.two_qubit_gate_count !== undefined && job.two_qubit_gate_count !== null ? job.two_qubit_gate_count : null
    };
    const resourceEstimateValue = job.resource_estimate || job.estimate || {};
    return {
      job_id: job.job_id || job.id || '—',
      user_id: job.user_id || '—',
      session_id: job.session_id || '—',
      circuit_qasm: job.circuit_qasm || '(not returned by API response)',
      backend: job.backend || '—',
      shots: job.shots,
      device: job.device || '—',
      simulation_type: job.simulation_type || '—',
      seed: job.seed,
      metadata: job.metadata || {},
      job_name: job.job_name || '—',
      options: job.options || {},
      tags: job.tags || {},
      status: job.status || '—',
      profile: profileValue,
      resource_estimate: resourceEstimateValue,
      estimate: resourceEstimateValue,
      result_counts: job.result_counts,
      result_metadata: job.result_metadata || {},
      has_external_artifact: !!job.has_external_artifact,
      result_url_expires_at: job.result_url_expires_at,
      error_message: job.error_message || '—',
      created_at: job.created_at,
      updated_at: job.updated_at,
      queue_enqueued_at: job.queue_enqueued_at || job.queued_at,
      queue_dequeued_at: job.queue_dequeued_at || job.started_at,
      queued_at: job.queue_enqueued_at || job.queued_at,
      started_at: job.queue_dequeued_at || job.started_at,
      execution_started_at: job.execution_started_at,
      execution_finished_at: job.execution_finished_at,
      execution_time_seconds: job.execution_time_seconds,
      cpu_seconds_total: job.cpu_seconds_total,
      peak_memory_mb: job.peak_memory_mb,
      billing_avg_memory_mb: job.billing_avg_memory_mb,
      billing_cpu_millicore_seconds: job.billing_cpu_millicore_seconds,
      billing_memory_gb_seconds: job.billing_memory_gb_seconds,
      billing_psutil_available: job.billing_psutil_available,
      billing_memory_headroom_mb: job.billing_memory_headroom_mb,
      completed_at: job.completed_at,
      pod_name: job.pod_name || '—'
    };
  }

  function hasDisplayValue(value) {
    if (value === null || value === undefined) return false;
    if (typeof value === 'string') return value.trim() !== '' && value !== '—';
    if (Array.isArray(value)) return value.length > 0;
    if (typeof value === 'object') return Object.keys(value).length > 0;
    return true;
  }

  function humanizeFieldName(field) {
    const acronymMap = {
      id: 'ID',
      cpu: 'CPU',
      qasm: 'QASM',
      s3: 'S3',
      url: 'URL',
      mb: 'MB',
      gb: 'GB'
    };
    return String(field)
      .split('_')
      .map((part) => {
        const key = part.toLowerCase();
        if (acronymMap[key]) return acronymMap[key];
        return key.charAt(0).toUpperCase() + key.slice(1);
      })
      .join(' ');
  }

  function getJobSchemaSections(job, view, excludedKeys) {
    const selectedView = view === 'results' ? 'results' : 'monitor';
    const sectionDefs = JOB_SCHEMA_SECTIONS_BY_VIEW[selectedView];
    const hidden = excludedKeys || new Set();
    const schemaFieldMap = getJobSchemaFieldMap(job);
    return sectionDefs.map((section) => {
      const rows = section.fields
        .filter((field) => !hidden.has(field))
        .map((field) => ({ k: field, label: humanizeFieldName(field), v: schemaFieldMap[field] }))
        .filter((row) => !HIDE_IF_EMPTY_FIELDS.has(row.k) || hasDisplayValue(row.v));
      return { title: section.title, subtitle: section.subtitle, rows };
    }).filter((section) => section.rows.length > 0);
  }

  function renderSchemaRows(rows) {
    return rows.map((row) => {
      const label = row.label || humanizeFieldName(row.k);
      const isJsonObject = row.v && typeof row.v === 'object';
      if (isJsonObject) {
        const jsonText = formatJsonValue(row.v);
        const jsonSafe = escapeHtml(jsonText);
        const isLargeJson = jsonText.length > 800;
        if (isLargeJson) {
          const lineCount = String(jsonText).split('\n').length;
          return `
          <div class="session-kv session-kv-stack">
            <span class="session-k">${escapeHtml(label)}</span>
            <details class="schema-collapsible">
              <summary>Expand JSON (${lineCount} lines)</summary>
              <pre class="session-json td-mono">${jsonSafe}</pre>
            </details>
          </div>`;
        }
        return `
        <div class="session-kv session-kv-stack">
          <span class="session-k">${escapeHtml(label)}</span>
          <pre class="session-json td-mono">${jsonSafe}</pre>
        </div>`;
      }
      const rendered = formatSchemaFieldValue(row.k, row.v);
      const safe = escapeHtml(rendered);
      const wrap = safe.length > 50 || safe.includes('{') || safe.includes('[');
      const longText = rendered.length > 180;
      if (longText) {
        const previewText = rendered.slice(0, 140).trim();
        const previewSafe = escapeHtml(`${previewText}${rendered.length > 140 ? '…' : ''}`);
        return `
        <div class="session-kv session-kv-stack">
          <span class="session-k">${escapeHtml(label)}</span>
          <div class="session-preview td-mono">${previewSafe}</div>
          <details class="schema-collapsible">
            <summary>Expand Value</summary>
            <pre class="session-json td-mono">${safe}</pre>
          </details>
        </div>`;
      }
      const wrapClass = wrap ? ' session-v-wrap' : '';
      return `
      <div class="session-kv">
        <span class="session-k">${escapeHtml(label)}</span>
        <span class="session-v td-mono${wrapClass}">${safe}</span>
      </div>`;
    }).join('');
  }

  function renderSchemaSections(sections) {
    return sections.map((section) => `
      <section class="job-schema-section">
        <div class="job-schema-header">
          <div class="job-schema-title">${escapeHtml(section.title)}</div>
          <div class="job-schema-subtitle">${escapeHtml(section.subtitle)}</div>
        </div>
        <div class="job-schema-body">${renderSchemaRows(section.rows)}</div>
      </section>
    `).join('');
  }

  function uid() {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') {
      return window.crypto.randomUUID();
    }
    return `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  function applyTheme(theme) {
    const normalized = theme === 'light' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', normalized);
    localStorage.setItem(THEME_KEY, normalized);
    const btn = $('themeToggleBtn');
    if (btn) btn.textContent = normalized === 'light' ? 'Dark' : 'Light';
    if (appState.pyMonaco && window.monaco && window.monaco.editor) {
      window.monaco.editor.setTheme(normalized === 'light' ? 'qos-light' : 'qos-dark');
    }
  }

  function loadMonacoLoader() {
    return new Promise((resolve, reject) => {
      if (window.require && window.require.config) {
        resolve();
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs/loader.js';
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Monaco loader'));
      document.head.appendChild(script);
    });
  }

  function registerPythonCompletions(monaco) {
    if (appState.pyCompletionRegistered) return;
    appState.pyCompletionRegistered = true;

    const commonModules = [
      ['random', 'Python stdlib random utilities'],
      ['math', 'Python math functions'],
      ['statistics', 'Statistical helpers'],
      ['itertools', 'Iterator building blocks'],
      ['collections', 'Container datatypes'],
      ['datetime', 'Date and time utilities'],
      ['json', 'JSON encode/decode'],
      ['pathlib', 'Filesystem paths'],
      ['typing', 'Type hint helpers'],
      ['numpy', 'Numerical computing'],
      ['scipy', 'Scientific computing'],
      ['pandas', 'Data analysis'],
      ['matplotlib', 'Plotting library'],
      ['seaborn', 'Statistical visualization'],
      ['sympy', 'Symbolic math'],
      ['qiskit', 'Quantum SDK'],
      ['cirq', 'Google quantum SDK'],
      ['pennylane', 'Hybrid quantum ML'],
      ['torch', 'PyTorch'],
      ['tensorflow', 'TensorFlow'],
      ['sklearn', 'Scikit-learn'],
      ['fastqsim', 'FastQSim SDK'],
      ['requests', 'HTTP client'],
      ['fastapi', 'Web API framework']
    ];

    const importSnippets = [
      {
        label: 'import numpy as np',
        insertText: 'import numpy as np',
        documentation: 'Common NumPy import alias'
      },
      {
        label: 'import pandas as pd',
        insertText: 'import pandas as pd',
        documentation: 'Common Pandas import alias'
      },
      {
        label: 'import matplotlib.pyplot as plt',
        insertText: 'import matplotlib.pyplot as plt',
        documentation: 'Common Matplotlib alias'
      },
      {
        label: 'from qiskit import QuantumCircuit',
        insertText: 'from qiskit import QuantumCircuit',
        documentation: 'Qiskit circuit import'
      },
      {
        label: 'import fastqsim',
        insertText: 'import fastqsim',
        documentation: 'Import FastQSim SDK'
      },
      {
        label: 'client = fastqsim.init()',
        insertText: 'client = fastqsim.init()',
        documentation: 'Initialize FastQSim client'
      },
      {
        label: 'from fastqsim import FastQSimClient, RunArgs, JobStatus',
        insertText: 'from fastqsim import FastQSimClient, RunArgs, JobStatus',
        documentation: 'Common FastQSim symbols'
      }
    ];

    const moduleMembers = {
      random: ['random', 'randint', 'randrange', 'choice', 'choices', 'shuffle', 'sample', 'seed'],
      math: ['sqrt', 'sin', 'cos', 'tan', 'pi', 'e', 'log', 'exp', 'floor', 'ceil'],
      statistics: ['mean', 'median', 'mode', 'pstdev', 'stdev', 'variance'],
      json: ['loads', 'dumps', 'load', 'dump'],
      datetime: ['datetime', 'timedelta', 'timezone', 'date', 'time'],
      pathlib: ['Path', 'PurePath'],
      numpy: ['array', 'zeros', 'ones', 'arange', 'linspace', 'mean', 'std', 'dot', 'reshape', 'random'],
      pandas: ['DataFrame', 'Series', 'read_csv', 'concat', 'merge', 'to_datetime'],
      requests: ['get', 'post', 'put', 'delete', 'patch', 'Session'],
      qiskit: ['QuantumCircuit', 'transpile', 'Aer', 'execute'],
      cirq: ['Circuit', 'Simulator', 'LineQubit', 'measure'],
      pennylane: ['device', 'QNode', 'qnode', 'numpy'],
      torch: ['tensor', 'nn', 'optim', 'randn', 'zeros', 'ones'],
      tensorflow: ['keras', 'constant', 'Variable', 'random', 'data'],
      sklearn: ['model_selection', 'metrics', 'preprocessing', 'datasets'],
      fastqsim: [
        'init', 'reset', 'FastQSimClient', 'RunArgs', 'JobStatus', 'SimulationType',
        'FastQSimError', 'FastQSimConnectionError', 'AuthenticationError', 'QuotaExceededError',
        'ValidationError', 'JobFailedError', 'JobTimeoutError', 'JobNotFoundError', 'JobCouldNotCancelError'
      ]
    };

    const objectMembers = {
      FastQSimClient: ['run', 'run_batch', 'get', 'wait', 'cancel', 'search', 'get_session', 'start_session'],
      Job: [
        'result', 'wait_for_completion', 'get_counts', 'get_statevector', 'cancel', 'refresh',
        'status', 'job_id', 'ok', 'error_message', 'backend', 'device', 'simulation_type', 'shots',
        'queue_enqueued_at', 'execution_started_at', 'execution_finished_at', 'completed_at',
        'execution_time_seconds', 'cpu_seconds_total', 'peak_memory_mb',
        'billing_cpu_millicore_seconds', 'billing_memory_gb_seconds', 'tags', 'metadata'
      ],
      Result: ['counts', 'probabilities', 'statevector', 'density_matrix', 'memory', 'execution_time', 'metadata', 'get_counts'],
      Session: ['session_id', 'user_id', 'state', 'execution_mode', 'created_at', 'expires_at', 'ws_token', 'refresh_token', 'close'],
      RunArgs: ['to_dict']
    };

    const memberDocs = {
      QuantumCircuit: 'Qiskit quantum circuit class',
      Aer: 'Qiskit Aer simulator provider',
      DataFrame: 'Pandas 2D labeled data structure',
      Path: 'Filesystem path helper class',
      Simulator: 'Cirq simulator backend'
    };

    const objectMemberDocs = {
      run: 'Submit one circuit or a list of circuits',
      run_batch: 'Submit multiple circuits asynchronously',
      get: 'Fetch latest job metadata',
      wait: 'Wait for one or more jobs to finish',
      cancel: 'Cancel one or more jobs',
      search: 'Search jobs by filters',
      get_session: 'Get active user session',
      start_session: 'Start a new session',
      result: 'Wait and return Result',
      get_counts: 'Return measurement counts',
      wait_for_completion: 'Block until terminal status',
      refresh: 'Refresh object from API',
      refresh_token: 'Refresh reconnect token',
      close: 'Terminate the session',
      to_dict: 'Serialize RunArgs payload'
    };

    function buildImportAliases(code) {
      const aliasMap = {};
      const lines = String(code || '').split('\n');
      for (const rawLine of lines) {
        const line = rawLine.trim();
        if (!line || line.startsWith('#')) continue;

        let m = line.match(/^import\s+([\w\.]+)\s+as\s+(\w+)$/);
        if (m) {
          aliasMap[m[2]] = m[1].split('.')[0];
          continue;
        }

        m = line.match(/^import\s+([\w\.]+)$/);
        if (m) {
          const mod = m[1].split('.')[0];
          aliasMap[mod] = mod;
          continue;
        }

        m = line.match(/^from\s+([\w\.]+)\s+import\s+([\w\s,]+)$/);
        if (m) {
          const mod = m[1].split('.')[0];
          const imports = m[2].split(',').map((p) => p.trim()).filter(Boolean);
          imports.forEach((imp) => {
            const asMatch = imp.match(/^(\w+)\s+as\s+(\w+)$/);
            if (asMatch) aliasMap[asMatch[2]] = mod;
            else aliasMap[imp] = mod;
          });
        }
      }
      return aliasMap;
    }

    function buildObjectAliases(code) {
      const objectMap = {};
      const lines = String(code || '').split('\n');
      for (const rawLine of lines) {
        const line = rawLine.trim();
        if (!line || line.startsWith('#')) continue;

        let m = line.match(/^(\w+)\s*=\s*fastqsim\.init\s*\(/);
        if (m) {
          objectMap[m[1]] = 'FastQSimClient';
          continue;
        }

        m = line.match(/^(\w+)\s*=\s*FastQSimClient\s*\(/);
        if (m) {
          objectMap[m[1]] = 'FastQSimClient';
          continue;
        }

        m = line.match(/^(\w+)\s*=\s*\w+\.run(_batch)?\s*\(/);
        if (m) {
          objectMap[m[1]] = 'Job';
          continue;
        }

        m = line.match(/^(\w+)\s*=\s*\w+\.result\s*\(/);
        if (m) {
          objectMap[m[1]] = 'Result';
          continue;
        }

        m = line.match(/^(\w+)\s*=\s*\w+\.(get_session|start_session)\s*\(/);
        if (m) {
          objectMap[m[1]] = 'Session';
          continue;
        }

        m = line.match(/^(\w+)\s*=\s*RunArgs\s*\(/);
        if (m) {
          objectMap[m[1]] = 'RunArgs';
        }
      }
      return objectMap;
    }

    monaco.languages.registerCompletionItemProvider('python', {
      triggerCharacters: ['.'],
      provideCompletionItems(model, position) {
        const lineText = model.getLineContent(position.lineNumber);
        const beforeCursor = lineText.slice(0, Math.max(0, position.column - 1));
        const importMatch = beforeCursor.match(/^\s*import\s+([\w\.]*)$/);
        const fromMatch = beforeCursor.match(/^\s*from\s+([\w\.]*)$/);
        const fromImportMembersMatch = beforeCursor.match(/^\s*from\s+([\w\.]+)\s+import\s+([\w\.]*)$/);
        const dottedMemberMatch = beforeCursor.match(/([A-Za-z_]\w*)\.([A-Za-z_]\w*)?$/);

        const word = model.getWordUntilPosition(position);
        const range = {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: word.startColumn,
          endColumn: word.endColumn
        };
        const keywords = [
          'import', 'from', 'def', 'class', 'return', 'for', 'while', 'if', 'elif', 'else',
          'try', 'except', 'finally', 'with', 'as', 'lambda', 'yield', 'async', 'await',
          'print', 'len', 'range', 'enumerate', 'zip', 'sum', 'min', 'max', 'map', 'filter'
        ];
        const snippets = [
          {
            label: 'for loop',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'for ${1:item} in ${2:items}:\n    ${3:pass}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Python for loop',
            range
          },
          {
            label: 'if __name__',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: "if __name__ == '__main__':\n    ${1:main()}",
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Entry point snippet',
            range
          }
        ];
        const keywordSuggestions = keywords.map((k) => ({
          label: k,
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: k,
          range
        }));

        const moduleSuggestions = commonModules.map(([name, doc]) => ({
          label: name,
          kind: monaco.languages.CompletionItemKind.Module,
          insertText: name,
          documentation: doc,
          range
        }));

        const importSnippetSuggestions = importSnippets.map((s) => ({
          label: s.label,
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: s.insertText,
          documentation: s.documentation,
          range
        }));

        const codeUntilCursor = model.getValueInRange({
          startLineNumber: 1,
          startColumn: 1,
          endLineNumber: position.lineNumber,
          endColumn: position.column
        });
        const aliasMap = buildImportAliases(codeUntilCursor);
        const objectAliasMap = buildObjectAliases(codeUntilCursor);

        const memberSuggestionsFor = (moduleName, prefix = '') => {
          const base = moduleName ? moduleName.split('.')[0] : '';
          const members = moduleMembers[base] || [];
          return members
            .filter((member) => String(member).startsWith(prefix || ''))
            .map((member) => ({
              label: member,
              kind: /^[A-Z]/.test(member)
                ? monaco.languages.CompletionItemKind.Class
                : monaco.languages.CompletionItemKind.Function,
              insertText: member,
              documentation: memberDocs[member] || `${base} member`,
              range
            }));
        };

        const objectSuggestionsFor = (objectType, prefix = '') => {
          const members = objectMembers[objectType] || [];
          return members
            .filter((member) => String(member).startsWith(prefix || ''))
            .map((member) => ({
              label: member,
              kind: /^[a-z]/.test(member)
                ? monaco.languages.CompletionItemKind.Method
                : monaco.languages.CompletionItemKind.Property,
              insertText: member,
              documentation: objectMemberDocs[member] || `${objectType} member`,
              range
            }));
        };

        if (importMatch || fromMatch) {
          const typedPrefix = (importMatch ? importMatch[1] : fromMatch[1]) || '';
          const filtered = moduleSuggestions.filter((s) => s.label.startsWith(typedPrefix));
          return { suggestions: filtered.concat(importSnippetSuggestions) };
        }

        if (fromImportMembersMatch) {
          const moduleName = fromImportMembersMatch[1];
          const typedPrefix = fromImportMembersMatch[2] || '';
          return { suggestions: memberSuggestionsFor(moduleName, typedPrefix) };
        }

        if (dottedMemberMatch) {
          const alias = dottedMemberMatch[1];
          const typedPrefix = dottedMemberMatch[2] || '';
          const objectType = objectAliasMap[alias];
          if (objectType) {
            const objectRange = {
              startLineNumber: position.lineNumber,
              endLineNumber: position.lineNumber,
              startColumn: position.column - typedPrefix.length,
              endColumn: position.column
            };
            const objectMembersList = objectSuggestionsFor(objectType, typedPrefix).map((s) => ({
              ...s,
              range: objectRange
            }));
            if (objectMembersList.length) return { suggestions: objectMembersList };
          }

          const moduleName = aliasMap[alias] || alias;
          const memberRange = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: position.column - typedPrefix.length,
            endColumn: position.column
          };
          const dottedMembers = memberSuggestionsFor(moduleName, typedPrefix).map((s) => ({
            ...s,
            range: memberRange
          }));
          if (dottedMembers.length) return { suggestions: dottedMembers };
        }

        return { suggestions: keywordSuggestions.concat(moduleSuggestions, importSnippetSuggestions, snippets) };
      }
    });
  }

  async function ensurePythonEditor() {
    if (appState.pyEditor) return appState.pyEditor;
    const host = $('python-editor');
    const fallback = $('python-code');
    if (!host || !fallback) return null;

    try {
      await loadMonacoLoader();
      window.require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs' } });
      const monaco = await new Promise((resolve, reject) => {
        window.require(['vs/editor/editor.main'], resolve, reject);
      });
      appState.pyMonaco = monaco;
      registerPythonCompletions(monaco);
      monaco.editor.defineTheme('qos-dark', {
        base: 'vs-dark',
        inherit: true,
        rules: [],
        colors: {
          'editor.background': '#080c14',
          'editorLineNumber.foreground': '#64748b',
          'editorLineNumber.activeForeground': '#cbd5e1',
          'scrollbarSlider.background': '#33415599',
          'scrollbarSlider.hoverBackground': '#475569aa',
          'scrollbarSlider.activeBackground': '#64748bcc'
        }
      });
      monaco.editor.defineTheme('qos-light', {
        base: 'vs',
        inherit: true,
        rules: [],
        colors: {
          'editor.background': '#f8fafc',
          'editorLineNumber.foreground': '#94a3b8',
          'editorLineNumber.activeForeground': '#334155',
          'scrollbarSlider.background': '#94a3b899',
          'scrollbarSlider.hoverBackground': '#64748baa',
          'scrollbarSlider.activeBackground': '#475569cc'
        }
      });
      fallback.classList.add('hidden');
      host.classList.remove('hidden');
      appState.pyEditor = monaco.editor.create(host, {
        value: fallback.value || "print('Hello from pod kernel!')",
        language: 'python',
        automaticLayout: true,
        minimap: { enabled: false },
        fontFamily: 'DM Mono, monospace',
        fontSize: 13,
        smoothScrolling: true,
        scrollBeyondLastLine: false,
        quickSuggestions: true,
        suggestOnTriggerCharacters: true,
        wordBasedSuggestions: 'currentDocument'
      });

      appState.pyEditor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
        window.runPythonCode();
      });
      appState.pyEditor.addCommand(monaco.KeyMod.Shift | monaco.KeyCode.Enter, () => {
        window.runPythonCode();
      });
      appState.pyEditor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Slash, () => {
        appState.pyEditor.getAction('editor.action.commentLine').run();
      });

      const scheduleLint = () => {
        if (appState.pyLintTimer) clearTimeout(appState.pyLintTimer);
        appState.pyLintTimer = setTimeout(() => {
          const code = appState.pyEditor ? appState.pyEditor.getValue() : '';
          setPythonLintMarkers(runBasicPythonLint(code));
        }, 180);
      };
      appState.pyEditor.onDidChangeModelContent(() => {
        // Runtime markers come from last execution traceback; clear them once user edits.
        clearPythonRuntimeMarkers();
        appState.pySawExecutionError = false;
        scheduleLint();
      });
      scheduleLint();

      monaco.editor.setTheme(document.documentElement.getAttribute('data-theme') === 'light' ? 'qos-light' : 'qos-dark');
      return appState.pyEditor;
    } catch {
      host.classList.add('hidden');
      fallback.classList.remove('hidden');
      return null;
    }
  }

  function getPythonCode() {
    if (appState.pyEditor && typeof appState.pyEditor.getValue === 'function') {
      return appState.pyEditor.getValue();
    }
    const input = $('python-code');
    return input ? input.value : '';
  }

  function stripAnsi(text) {
    return String(text || '').replace(/\u001b\[[0-9;]*m/g, '');
  }

  function pythonErrorSeverity() {
    return (appState.pyMonaco && appState.pyMonaco.MarkerSeverity && appState.pyMonaco.MarkerSeverity.Error) || 8;
  }

  function applyPythonMarkers() {
    if (!appState.pyMonaco || !appState.pyEditor || !appState.pyEditor.getModel) return;
    const model = appState.pyEditor.getModel();
    if (!model) return;
    const merged = (appState.pyLintMarkers || []).concat(appState.pyRuntimeMarkers || []);
    appState.pyMonaco.editor.setModelMarkers(model, PY_MONACO_MARKER_OWNER, merged);
  }

  function setPythonLintMarkers(markers) {
    appState.pyLintMarkers = Array.isArray(markers) ? markers : [];
    applyPythonMarkers();
  }

  function setPythonRuntimeMarkers(markers) {
    appState.pyRuntimeMarkers = Array.isArray(markers) ? markers : [];
    applyPythonMarkers();
  }

  function clearPythonRuntimeMarkers() {
    setPythonRuntimeMarkers([]);
  }

  function runBasicPythonLint(code) {
    const markers = [];
    const lines = String(code || '').replace(/\r\n/g, '\n').split('\n');
    const stack = [];
    const openerToCloser = { '(': ')', '[': ']', '{': '}' };
    const closerToOpener = { ')': '(', ']': '[', '}': '{' };
    const quoteState = { active: false, quote: '' };

    lines.forEach((line, idx) => {
      const lineNo = idx + 1;
      const leading = line.match(/^\s+/);
      if (leading && leading[0].includes('\t') && leading[0].includes(' ')) {
        markers.push({
          startLineNumber: lineNo,
          endLineNumber: lineNo,
          startColumn: 1,
          endColumn: Math.max(2, leading[0].length + 1),
          message: 'Mixed tabs and spaces in indentation.',
          severity: pythonErrorSeverity()
        });
      }

      for (let i = 0; i < line.length; i += 1) {
        const ch = line[i];
        const prev = i > 0 ? line[i - 1] : '';
        if (!quoteState.active && ch === '#') break;

        if ((ch === '"' || ch === "'") && prev !== '\\') {
          if (!quoteState.active) {
            quoteState.active = true;
            quoteState.quote = ch;
            continue;
          }
          if (quoteState.quote === ch) {
            quoteState.active = false;
            quoteState.quote = '';
            continue;
          }
        }

        if (quoteState.active) continue;

        if (openerToCloser[ch]) {
          stack.push({ ch, lineNo, col: i + 1 });
        } else if (closerToOpener[ch]) {
          const top = stack[stack.length - 1];
          if (!top || top.ch !== closerToOpener[ch]) {
            markers.push({
              startLineNumber: lineNo,
              endLineNumber: lineNo,
              startColumn: i + 1,
              endColumn: i + 2,
              message: `Unexpected closing '${ch}'.`,
              severity: pythonErrorSeverity()
            });
          } else {
            stack.pop();
          }
        }
      }
    });

    stack.forEach((open) => {
      markers.push({
        startLineNumber: open.lineNo,
        endLineNumber: open.lineNo,
        startColumn: open.col,
        endColumn: open.col + 1,
        message: `Unclosed '${open.ch}'.`,
        severity: pythonErrorSeverity()
      });
    });

    if (quoteState.active) {
      const lastLine = Math.max(1, lines.length);
      const lastCol = Math.max(1, (lines[lastLine - 1] || '').length);
      markers.push({
        startLineNumber: lastLine,
        endLineNumber: lastLine,
        startColumn: lastCol,
        endColumn: lastCol + 1,
        message: 'Unterminated string literal.',
        severity: pythonErrorSeverity()
      });
    }

    return markers;
  }

  function extractTracebackLine(tracebackLines) {
    const lines = Array.isArray(tracebackLines) ? tracebackLines : [];
    for (let i = lines.length - 1; i >= 0; i -= 1) {
      const m = String(lines[i] || '').match(/line\s+(\d+)/i);
      if (m) return parseInt(m[1], 10);
    }
    return null;
  }

  function notify(message, type = '') {
    if (typeof showToast === 'function') showToast(message, '', type);
  }

  function appendPyOutput(text, level = 'info') {
    const out = $('python-output');
    if (!out) return;
    const line = document.createElement('div');
    if (level === 'error') line.style.color = 'var(--red)';
    if (level === 'ok') line.style.color = 'var(--green)';
    if (level === 'meta') line.style.color = 'var(--text-dim)';
    line.textContent = stripAnsi(text);
    out.appendChild(line);
    out.scrollTop = out.scrollHeight;
  }

  function updatePythonMeta(session = null) {
    const sess = session || appState.activeSession || null;
    const pySessionId = $('py-session-id');
    if (pySessionId) pySessionId.textContent = (sess && sess.id) || '—';
    const pyKernelId = $('py-kernel-id');
    if (pyKernelId) pyKernelId.textContent = (sess && sess.kernel_id) || '—';
    const pyWsUrl = $('py-ws-url');
    if (pyWsUrl) pyWsUrl.textContent = 'Hidden';
    const pyMsgId = $('py-msg-id');
    if (pyMsgId) pyMsgId.textContent = appState.pyCurrentMsgId || '—';
    const pyWsBadge = $('python-ws-badge');
    if (pyWsBadge) {
      pyWsBadge.textContent = appState.pyWs && appState.pyWs.readyState === WebSocket.OPEN ? 'WS: CONNECTED' : 'WS: DISCONNECTED';
      pyWsBadge.className = appState.pyWs && appState.pyWs.readyState === WebSocket.OPEN ? 'badge badge-green' : 'badge badge-blue';
    }
  }

  function clearPythonOutputPane() {
    const out = $('python-output');
    if (out) out.textContent = '';
  }

  function setWsProxyAuthCookies(token) {
    // The local dev proxy reads these cookies and injects websocket headers for the router.
    const isDevServer = window.location.port === '5173';
    if (!isDevServer) return;
    const attrs = '; path=/; SameSite=Lax';
    document.cookie = `qos_ws_token=${encodeURIComponent(token || '')}${attrs}`;
    document.cookie = `qos_user_id=${encodeURIComponent(appState.endUserId || appState.userId || '')}${attrs}`;
  }

  function clearWsProxyAuthCookies() {
    const attrs = '; path=/; Max-Age=0; SameSite=Lax';
    document.cookie = `qos_ws_token=${attrs}`;
    document.cookie = `qos_user_id=${attrs}`;
  }

  function populateSessionPanel() {
    const sess = appState.activeSession;

    $('sess-id').textContent = (sess && sess.id) || '—';
    $('sess-kernel').textContent = (sess && sess.kernel_id) || '—';
    const sessWs = $('sess-ws');
    if (sessWs) sessWs.textContent = 'Hidden';
    $('sess-started').textContent = formatElapsedSince(sess && sess.started_at);
    $('sess-user').textContent = (sess && (sess.end_user_id || sess.user_id)) || appState.endUserId || appState.userId || '—';
    $('sess-state').innerHTML = sess ? badgeHtmlSafe(sess.state) : badgeHtmlSafe('idle');
    if (sess && sess.id) $('job-session-id').value = sess.id;
  }

  function startCountdown() {
    if (appState.countdownInterval) clearInterval(appState.countdownInterval);

    appState.countdownInterval = setInterval(() => {
      const sess = appState.activeSession;
      if (!sess || !sess.expires_at) {
        $('sess-countdown').textContent = '—';
        return;
      }
      const rem = new Date(sess.expires_at).getTime() - Date.now();
      if (rem <= 0) {
        $('sess-countdown').textContent = '0m 0s 0ms';
        return;
      }
      $('sess-countdown').textContent = formatDurationMs(rem);
    }, 1000);
  }

  function renderSessionHistory() {
    const tbody = $('session-history-body');
    if (!appState.sessions.length) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:24px">No sessions found.</td></tr>';
      $('sess-count-label').textContent = '0 sessions';
      return;
    }

    tbody.innerHTML = appState.sessions.map((s) => `
      <tr>
        <td class="td-mono">${s.id}</td>
        <td>${badgeHtmlSafe(s.state)}</td>
        <td class="td-mono">${s.kernel_id || '—'}</td>
        <td class="text-muted">${formatElapsedSince(s.started_at)}</td>
        <td>${!SESSION_TERMINAL.has((s.state || '').toLowerCase()) ? `<button class="btn btn-red btn-sm" onclick="terminateSession('${s.id}')">Terminate</button>` : '<span class="text-muted text-xs">—</span>'}</td>
      </tr>
    `).join('');

    $('sess-count-label').textContent = `${appState.sessions.length} sessions`;
  }

  async function loadSessions(showErrors = false) {
    try {
      const data = await apiRequest('/sessions', 'GET', null, 'integrator');
      const items = Array.isArray(data && data.items) ? data.items : [];
      appState.sessions = items.map(normalizeSession);
      appState.activeSession = getActiveSession();
      if (appState.activeSession && appState.activeSession.session_token) {
        appState.sessionToken = appState.activeSession.session_token;
      }
      populateSessionPanel();
      renderSessionHistory();
      startCountdown();
      if (!appState.activeSession) $('sess-countdown').textContent = '—';
    } catch (err) {
      if (showErrors) notify(`Session sync failed: ${err.message}`, 'error');
    }
  }

  async function loadJobs(showErrors = false) {
    try {
      const data = await apiRequest('/jobs', 'GET', null, 'pod');
      const items = Array.isArray(data && data.items) ? data.items : [];
      appState.jobs = items.map(normalizeJob);
    } catch (err) {
      if (showErrors) notify(`Job sync failed: ${err.message}`, 'error');
    }
  }

  async function loadJobById(jobId) {
    const data = await apiRequest(`/jobs/${encodeURIComponent(jobId)}`, 'GET', null, 'pod');
    const job = normalizeJob(data);
    const idx = appState.jobs.findIndex((j) => j.id === job.id);
    if (idx >= 0) appState.jobs[idx] = job;
    else appState.jobs.unshift(job);
    return job;
  }

  function renderDashboardFromState() {
    const completed = appState.jobs.filter((j) => (j.status || '').toLowerCase() === 'completed').length;
    const running = appState.jobs.filter((j) => (j.status || '').toLowerCase() === 'running').length;

    $('dash-total-sessions').textContent = String(appState.sessions.length);
    $('dash-total-jobs').textContent = String(appState.jobs.length);
    $('dash-completed').textContent = String(completed);
    $('dash-running').textContent = String(running);

    const sess = appState.activeSession;
    const sessBody = $('dash-session-body');

    if (sess) {
      sessBody.innerHTML = `
        <div class="session-kv"><span class="session-k">Session ID</span><span class="session-v td-mono">${sess.id}</span></div>
        <div class="session-kv"><span class="session-k">Kernel</span><span class="session-v td-mono">${sess.kernel_id || '—'}</span></div>
        <div class="session-kv"><span class="session-k">TTL Remaining</span><span class="session-v text-yellow">${formatRemainingUntil(sess.expires_at)}</span></div>
        <div class="session-kv"><span class="session-k">State</span><span>${badgeHtmlSafe(sess.state)}</span></div>
      `;
      $('dash-session-badge').textContent = 'ACTIVE';
      $('dash-session-badge').className = 'badge badge-green';
    } else {
      sessBody.innerHTML = `<div class="no-session-msg">No active session.<br><button class="btn btn-primary" style="margin-top:10px" onclick="goPage('sessions',null)">Open Sessions</button></div>`;
      $('dash-session-badge').textContent = 'NONE';
      $('dash-session-badge').className = 'badge badge-gray';
    }

    const recentJobs = appState.jobs.slice(0, 5);
    const rj = $('dash-recent-jobs');
    if (!recentJobs.length) {
      rj.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);font-size:13px">No jobs yet.</div>';
    } else {
      rj.innerHTML = recentJobs.map((j) => `
        <div class="job-row" onclick="goToJobMonitor('${j.id}')">
          <span class="job-id">${j.id}</span>
          <span class="text-dim">${j.backend}</span>
          <span class="text-dim">${j.shots}</span>
          <span>${badgeHtmlSafe(j.status)}</span>
          <span class="text-muted">${formatElapsedSince(j.created_at || j.submitted_at)}</span>
        </div>
      `).join('');
    }
  }

  async function refreshDashboardImpl() {
    await updateHealth();
    await loadSessions(false);
    if (appState.activeSession) {
      await ensureActiveSessionToken(appState.activeSession);
      await loadJobs(false);
    } else {
      appState.jobs = [];
    }
    renderDashboardFromState();
  }

  function renderHistory() {
    const tbody = $('history-table-body');
    let jobs = appState.jobs;
    if (appState.historyFilter !== 'all') {
      jobs = jobs.filter((j) => (j.status || '').toLowerCase() === appState.historyFilter);
    }

    if (!jobs.length) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--text-muted);padding:24px">No jobs found.</td></tr>';
      return;
    }

    tbody.innerHTML = jobs.map((j) => `
      <tr onclick="goToJobMonitor('${j.id}')" style="cursor:pointer">
        <td class="td-mono">${j.id}</td>
        <td><span class="badge badge-purple" style="font-size:10px">${j.backend}</span></td>
        <td class="text-mono">${j.shots}</td>
        <td>${badgeHtmlSafe(j.status)}</td>
        <td class="text-muted">${formatElapsedSince(j.created_at || j.submitted_at)}</td>
        <td class="text-mono">${formatDurationMs(j.duration_ms)}</td>
        <td>
          <div style="display:flex;gap:6px">
            <button class="btn btn-ghost btn-sm" onclick="event.stopPropagation();goToJobMonitor('${j.id}')">Monitor</button>
            ${(j.status || '').toLowerCase() === 'completed' ? `<button class="btn btn-blue btn-sm" onclick="event.stopPropagation();goPage('results',null);renderResultsById('${j.id}')">Results</button>` : ''}
          </div>
        </td>
      </tr>
    `).join('');
  }

  function renderJobDetail(job) {
    $('job-detail-wrap').style.display = 'block';
    $('monitor-job-id-sub').textContent = `Job: ${job.id}`;
    $('monitor-status-badge').innerHTML = badgeHtmlSafe(job.status);
    const exportBtn = $('monitor-export-btn');
    if (exportBtn) exportBtn.style.display = 'inline-flex';

    const steps = ['created', 'queued', 'running', 'completed'];
    const status = (job.status || '').toLowerCase();
    const failed = status === 'failed' || status === 'cancelled';
    const currentIdx = failed ? 2 : Math.max(0, steps.indexOf(status));

    $('job-pipeline').innerHTML = steps.map((s, i) => {
      let cls = '';
      if (failed && i === currentIdx) cls = 'failed';
      else if (i < currentIdx || (status === 'completed' && i === 3)) cls = 'done';
      else if (i === currentIdx) cls = 'active';
      const iconHtml = failed && i === currentIdx
        ? '<i class="bi bi-x-lg"></i>'
        : s === 'completed'
          ? '<i class="bi bi-check-lg"></i>'
          : s === 'running'
            ? '<i class="bi bi-play-fill"></i>'
            : s === 'queued'
              ? '<i class="bi bi-hourglass-split"></i>'
              : '<i class="bi bi-dot"></i>';
      return `<div class="pipeline-step ${cls}"><div class="pipeline-dot">${iconHtml}</div><div class="pipeline-label">${s.toUpperCase()}</div></div>`;
    }).join('');

    const queuedAt = job.queue_enqueued_at || job.queued_at || null;
    const runningAt = job.queue_dequeued_at || job.started_at || null;
    const timingBase = job.created_at || queuedAt || runningAt || job.execution_started_at || null;
    const timingRows = [
      { label: 'Created', ts: job.created_at },
      { label: 'Queued', ts: queuedAt },
      { label: 'Dequeued', ts: runningAt },
      { label: 'Exec Start', ts: job.execution_started_at },
      { label: 'Exec End', ts: job.execution_finished_at },
      { label: 'Completed', ts: job.completed_at },
      { label: 'Updated', ts: job.updated_at }
    ];

    const filled = timingRows.filter((r) => r.ts).length || 1;
    $('timing-panel').innerHTML = timingRows.map((t, i) => {
      const pct = t.ts ? Math.round(((i + 1) / filled) * 100) : 0;
      return `
        <div class="timing-row">
          <span class="timing-label">${t.label}</span>
          <div class="timing-bar-wrap"><div class="timing-bar" style="width:${pct}%;background:${t.ts ? 'linear-gradient(90deg,var(--purple),var(--blue))' : 'var(--bg2)'}"></div></div>
          <span class="timing-ts">${t.ts ? (timingBase ? formatOffsetFrom(timingBase, t.ts) : formatElapsedSince(t.ts)) : '—'}</span>
        </div>`;
    }).join('');

    $('circuit-profile-grid').innerHTML = [
      { k: 'Qubits', v: job.qubits !== null && job.qubits !== undefined ? job.qubits : '—', c: 'blue' },
      { k: 'Depth', v: job.depth !== null && job.depth !== undefined ? job.depth : '—', c: 'purple' },
      { k: 'Gate Count', v: job.gate_count !== null && job.gate_count !== undefined ? job.gate_count : '—', c: 'green' },
      { k: '2Q Gates', v: job.two_qubit_gate_count !== null && job.two_qubit_gate_count !== undefined ? job.two_qubit_gate_count : '—', c: 'yellow' }
    ].map((m) => `
      <div style="background:var(--glass);border:1px solid var(--border);border-radius:8px;padding:12px">
        <div class="text-muted text-xs" style="margin-bottom:4px">${m.k}</div>
        <div style="font-size:22px;font-weight:700;font-family:var(--mono);color:var(--${m.c})">${m.v}</div>
      </div>`).join('');

    const schemaSections = getJobSchemaSections(job, 'monitor');
    const resourceGridEl = $('resource-grid');
    resourceGridEl.classList.add('job-schema-grid');
    resourceGridEl.classList.remove('job-schema-grid-single');
    resourceGridEl.innerHTML = renderSchemaSections(schemaSections);

    const live = !JOB_TERMINAL.has(status);
    $('monitor-live-badge').style.display = live ? 'flex' : 'none';
    $('monitor-cancel-btn').style.display = live ? 'inline-flex' : 'none';

    if (appState.monitorInterval) clearInterval(appState.monitorInterval);
    if (live) {
      appState.monitorInterval = setInterval(async () => {
        try {
          const fresh = await loadJobById(job.id);
          if (JOB_TERMINAL.has((fresh.status || '').toLowerCase())) {
            clearInterval(appState.monitorInterval);
          }
          renderJobDetail(fresh);
        } catch {
          clearInterval(appState.monitorInterval);
        }
      }, 2000);
    }
  }

  function renderResults(job) {
    const counts = job.result_counts || {};
    const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    if (!entries.length) {
      notify('No inline result_counts yet for this job', 'yellow');
      return;
    }

    $('results-empty').style.display = 'none';
    $('results-content').style.display = 'block';
    $('results-job-sub').textContent = `Job: ${job.id}`;
    $('results-shots-label').textContent = `${job.shots} shots`;

    const total = entries.reduce((acc, [, c]) => acc + c, 0);
    const maxCount = Math.max(...entries.map(([, c]) => c));
    const colors = [
      'linear-gradient(180deg,var(--blue),var(--purple))',
      'linear-gradient(180deg,var(--purple),#ec4899)',
      'linear-gradient(180deg,var(--green),var(--blue))',
      'linear-gradient(180deg,var(--yellow),var(--red))'
    ];

    $('result-histogram').innerHTML = entries.map(([label, count], i) => `
      <div class="hist-bar-wrap">
        <div class="hist-count">${count}</div>
        <div class="hist-bar" style="height:${Math.max(4, Math.round((count / maxCount) * 140))}px;background:${colors[i % colors.length]}"></div>
        <div class="hist-label">|${label}⟩</div>
      </div>`).join('');

    $('prob-distribution').innerHTML = entries.map(([label, count], i) => {
      const pct = (count / total) * 100;
      return `
        <div class="prob-row">
          <span class="prob-label">|${label}⟩</span>
          <div class="prob-bar-wrap"><div class="prob-bar" style="width:${Math.round(pct)}%;background:${colors[i % colors.length]}"></div></div>
          <span class="prob-count">${count}</span>
          <span class="prob-pct">${pct.toFixed(1)}%</span>
        </div>`;
    }).join('');

    const summaryRows = [
      { k: 'job_id', v: job.job_id || job.id || '—' },
      { k: 'backend', v: job.backend || '—' },
      { k: 'device', v: job.device || '—' },
      { k: 'simulation_type', v: job.simulation_type || '—' },
      { k: 'engine', v: (job.result_metadata && job.result_metadata.engine) || '—' },
      { k: 'shots', v: job.shots || '—' },
      { k: 'unique_states', v: entries.length },
      {
        k: 'execution_time_seconds',
        v: job.execution_time_seconds !== null && job.execution_time_seconds !== undefined
          ? job.execution_time_seconds
          : (job.duration_ms !== null && job.duration_ms !== undefined ? job.duration_ms / 1000 : null)
      },
      { k: 'cpu_seconds_total', v: job.cpu_seconds_total },
      { k: 'has_external_artifact', v: job.has_external_artifact ? 'true' : 'false' }
    ];
    const summaryKeys = new Set(summaryRows.map((row) => row.k));
    const schemaSections = getJobSchemaSections(job, 'results', summaryKeys);
    const metadataSections = [
      {
        title: 'Result Summary',
        subtitle: 'Key output signals',
        rows: summaryRows
      }
    ].concat(schemaSections);
    const resultsMetadataEl = $('results-metadata');
    resultsMetadataEl.classList.add('job-schema-grid', 'job-schema-grid-single');
    resultsMetadataEl.innerHTML = renderSchemaSections(metadataSections);

    if (job.has_external_artifact) {
      $('download-artifact-btn').style.display = 'inline-flex';
      $('download-artifact-btn').dataset.jobId = job.id;
    } else {
      $('download-artifact-btn').style.display = 'none';
      delete $('download-artifact-btn').dataset.jobId;
    }
  }

  async function startPythonSessionInternal() {
    const sessionResp = await apiRequest('/sessions/start', 'POST', {}, 'integrator');
    let sess = syncSessionState(sessionResp) || normalizeSession(sessionResp);

    // If API returned an already-active session (or no token), fetch a fresh ws_token.
    let wsToken = sessionResp && sessionResp.ws_token ? sessionResp.ws_token : '';
    if (!wsToken && sess.id) {
      const tokenResp = await apiRequest(`/sessions/${encodeURIComponent(sess.id)}/reconnect-token`, 'POST', {}, 'integrator');
      wsToken = tokenResp && tokenResp.ws_token ? tokenResp.ws_token : '';
      sess = syncSessionState({ ...sess, ...tokenResp }) || normalizeSession({ ...sess, ...tokenResp });
    }

    sess.ws_token = wsToken || '';
    appState.pyWsToken = sess.ws_token;
    appState.activeSession = sess;
    if (sess.session_token) {
      appState.sessionToken = sess.session_token;
    }

    const idx = appState.sessions.findIndex((s) => s.id === sess.id);
    if (idx >= 0) appState.sessions[idx] = sess;
    else appState.sessions.unshift(sess);

    populateSessionPanel();
    renderSessionHistory();
    startCountdown();
    updatePythonMeta(sess);
    return sess;
  }

  function ensurePythonWsHandlers(ws) {
    ws.onopen = () => {
      appendPyOutput('WebSocket connected.', 'ok');
      updatePythonMeta();
    };

    ws.onclose = () => {
      appendPyOutput('WebSocket disconnected.', 'meta');
      appState.pyWs = null;
      clearWsProxyAuthCookies();
      updatePythonMeta();
    };

    ws.onerror = () => {
      appendPyOutput('WebSocket error occurred.', 'error');
      updatePythonMeta();
    };

    ws.onmessage = (ev) => {
      let msg = null;
      try {
        msg = JSON.parse(ev.data);
      } catch {
        appendPyOutput(String(ev.data || ''), 'meta');
        return;
      }

      const parent = msg.parent_header || {};
      if (appState.pyCurrentMsgId && parent.msg_id !== appState.pyCurrentMsgId) return;

      const header = msg.header || {};
      const content = msg.content || {};
      const msgType = header.msg_type;

      if (msgType === 'stream') {
        if (content.text) appendPyOutput(content.text, 'info');
      } else if (msgType === 'execute_result' || msgType === 'display_data') {
        const data = content.data || {};
        if (data['text/plain'] !== undefined) appendPyOutput(String(data['text/plain']), 'info');
      } else if (msgType === 'error') {
        const traceback = content.traceback || [];
        appState.pySawExecutionError = true;
        if (traceback.length) appendPyOutput(traceback.join('\n'), 'error');
        else appendPyOutput(content.evalue || 'Kernel execution error', 'error');
        const errLine = extractTracebackLine(traceback);
        if (errLine && appState.pyEditor && appState.pyEditor.getModel) {
          const model = appState.pyEditor.getModel();
          const lineCount = model ? model.getLineCount() : 0;
          const targetLine = Math.min(Math.max(1, errLine), Math.max(1, lineCount));
          const lineText = model ? model.getLineContent(targetLine) : '';
          setPythonRuntimeMarkers([{
            startLineNumber: targetLine,
            endLineNumber: targetLine,
            startColumn: 1,
            endColumn: Math.max(2, (lineText || '').length + 1),
            message: `${content.ename || 'PythonError'}: ${content.evalue || 'Execution error'}`,
            severity: pythonErrorSeverity()
          }]);
        }
      } else if (msgType === 'execute_reply') {
        if (content.status === 'ok' || !appState.pySawExecutionError) {
          appendPyOutput(`execute_reply: ${content.status || 'unknown'}`, content.status === 'ok' ? 'ok' : 'error');
        }
        if (content.status === 'ok') clearPythonRuntimeMarkers();
      } else if (msgType === 'status' && content.execution_state === 'idle') {
        appendPyOutput('Kernel is idle.', 'meta');
      }
    };
  }

  // ===== Exposed functions (onclick handlers) =====
  window.toggleTheme = function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
    applyTheme(current === 'light' ? 'dark' : 'light');
  };

  window.doLogin = async function doLogin() {
    const apiKey = $('loginApiKeyInput').value.trim();
    const endUserId = $('loginEndUserIdInput').value.trim();
    if (!apiKey || !endUserId) {
      notify('Enter both an API key and an end-user ID', 'yellow');
      return;
    }

    try {
      setDirectAuth({ apiKey, endUserId });
      await apiRequest('/me', 'GET', null, 'integrator');
    } catch (err) {
      clearDirectAuth();
      clearWsProxyAuthCookies();
      setSidebarUser();
      notify(`Login failed: ${err.message}`, 'error');
      return;
    }

    $('loginScreen').style.display = 'none';
    $('app').style.display = 'flex';
    setSidebarUser();

    window.goPage('sessions', null);
    await loadSessions(true);
    if (appState.activeSession) {
      await ensureActiveSessionToken(appState.activeSession);
      await loadJobs(true);
    }
    await window.refreshDashboard();

    notify(`Signed in as ${appState.endUserId}`, 'success');
  };

  window.doLogout = async function doLogout() {
    if (appState.monitorInterval) clearInterval(appState.monitorInterval);
    if (appState.countdownInterval) clearInterval(appState.countdownInterval);
    if (appState.pyWs) {
      try { appState.pyWs.close(); } catch { }
    }
    appState.pyWs = null;
    appState.pyWsToken = null;
    clearWsProxyAuthCookies();
    clearDirectAuth();
    $('loginScreen').style.display = 'flex';
    $('app').style.display = 'none';
    const apiKeyInput = $('loginApiKeyInput');
    const endUserInput = $('loginEndUserIdInput');
    if (apiKeyInput) apiKeyInput.value = '';
    if (endUserInput) endUserInput.value = '';
    setSidebarUser();
  };

  window.startPythonSession = async function startPythonSession() {
    if (!appState.integratorApiKey || !appState.endUserId) {
      notify('Login first', 'yellow');
      return;
    }
    try {
      await ensurePythonEditor();
      const sess = await startPythonSessionInternal();
      appendPyOutput(`Session started: ${sess.id}`, 'ok');
      await window.connectPythonWs();
      notify('Python session started', 'success');
    } catch (err) {
      appendPyOutput(`Session start failed: ${err.message}`, 'error');
      notify(`Session start failed: ${err.message}`, 'error');
    }
  };

  window.connectPythonWs = async function connectPythonWs() {
    try {
      if (appState.pyWs && appState.pyWs.readyState === WebSocket.OPEN) {
        appendPyOutput('WebSocket already connected.', 'meta');
        updatePythonMeta();
        return;
      }

      let sess = appState.activeSession;
      if (!sess || !sess.ws_url || !sess.kernel_id) {
        sess = await startPythonSessionInternal();
      }

      if (!sess.ws_token && sess.id) {
        const tokenResp = await apiRequest(`/sessions/${encodeURIComponent(sess.id)}/reconnect-token`, 'POST', {}, 'integrator');
        sess = syncSessionState({ ...sess, ...tokenResp }) || normalizeSession({ ...sess, ...tokenResp });
        sess.ws_token = tokenResp && tokenResp.ws_token ? tokenResp.ws_token : '';
        appState.pyWsToken = sess.ws_token;
        appState.activeSession = sess;
      }

      const wsUrl = String(sess.ws_url || '');
      if (!wsUrl) throw new Error('Session ws_url missing from start session response');
      if (!sess.ws_token) throw new Error('ws_token missing; cannot authorize websocket');

      // Token is not put in URL; Node proxy reads it from cookies and injects X-WS-Token.
      setWsProxyAuthCookies(sess.ws_token);
      const wsUrlForBrowser = toDevProxyWsUrl(wsUrl);
      appState.pyWs = new WebSocket(wsUrlForBrowser);
      ensurePythonWsHandlers(appState.pyWs);
      updatePythonMeta(sess);
      appendPyOutput('Connecting to kernel channel...', 'meta');
    } catch (err) {
      appendPyOutput(`WS connect failed: ${err.message}`, 'error');
      notify(`WS connect failed: ${err.message}`, 'error');
    }
  };

  window.disconnectPythonWs = function disconnectPythonWs() {
    if (appState.pyWs) {
      try { appState.pyWs.close(); } catch { }
      appState.pyWs = null;
    }
    clearWsProxyAuthCookies();
    updatePythonMeta();
  };

  window.clearPythonOutput = function clearPythonOutput() {
    clearPythonOutputPane();
  };

  window.runPythonCode = async function runPythonCode() {
    let code = getPythonCode();
    if (!code.trim()) {
      notify('Python code is empty', 'yellow');
      return;
    }

    const lintMarkers = runBasicPythonLint(code);
    setPythonLintMarkers(lintMarkers);
    if (lintMarkers.length) {
      notify('Fix syntax errors before running code.', 'error');
      return;
    }

    appState.pySawExecutionError = false;
    clearPythonRuntimeMarkers();

    if (!appState.pyWs || appState.pyWs.readyState !== WebSocket.OPEN) {
      await window.connectPythonWs();
    }

    if (!appState.pyWs || appState.pyWs.readyState !== WebSocket.OPEN) {
      appendPyOutput('WebSocket is not connected.', 'error');
      return;
    }

    const clientSessionId = uid();
    const executeMsgId = uid();
    appState.pyCurrentMsgId = executeMsgId;
    updatePythonMeta();

    const executeRequest = {
      header: {
        msg_id: executeMsgId,
        username: 'web-client',
        session: clientSessionId,
        msg_type: 'execute_request',
        version: '5.3'
      },
      parent_header: {},
      metadata: {},
      channel: 'shell',
      content: {
        code,
        silent: false,
        store_history: true,
        user_expressions: {},
        allow_stdin: false,
        stop_on_error: true
      }
    };

    appendPyOutput(`Sending execute_request ${executeMsgId}`, 'meta');
    appState.pyWs.send(JSON.stringify(executeRequest));
  };

  window.goPage = function goPage(id, navEl) {
    document.querySelectorAll('.page').forEach((p) => p.classList.remove('active'));
    const page = $(`page-${id}`);
    if (page) page.classList.add('active');

    document.querySelectorAll('.nav-item').forEach((n) => n.classList.remove('active'));
    if (navEl) navEl.classList.add('active');
    else {
      document.querySelectorAll('.nav-item').forEach((ni) => {
        const handler = ni.getAttribute('onclick') || '';
        if (handler.includes(`'${id}'`)) ni.classList.add('active');
      });
    }

    if (id === 'sessions') {
      loadSessions(false);
    } else if (id === 'dashboard') {
      window.refreshDashboard();
    } else if (id === 'history') {
      window.refreshHistory();
    } else if (id === 'submit') {
      if (!appState.activeSession) loadSessions(false);
      else $('job-session-id').value = appState.activeSession.id;
    } else if (id === 'python') {
      updatePythonMeta();
      ensurePythonEditor();
      if (appState.integratorApiKey && appState.endUserId) {
        window.connectPythonWs();
      }
    }
  };

  window.refreshDashboard = async function refreshDashboard() {
    await refreshDashboardImpl();
  };

  window.startSession = async function startSession() {
    if (!appState.integratorApiKey || !appState.endUserId) return;
    try {
      notify('Starting session...', 'blue');
      const sess = syncSessionState(await apiRequest('/sessions/start', 'POST', {}, 'integrator'));
      if (sess && sess.session_token) {
        appState.sessionToken = sess.session_token;
      }
      await loadSessions(false);
      await loadJobs(false);
      await window.refreshDashboard();
      notify('Session started', 'success');
    } catch (err) {
      notify(`Start failed: ${err.message}`, 'error');
    }
  };

  window.startSessionQuick = function startSessionQuick() {
    return window.startSession();
  };

  window.heartbeat = async function heartbeat() {
    const sess = appState.activeSession;
    if (!sess) {
      notify('No active session', 'yellow');
      return;
    }

    try {
      await apiRequest(`/sessions/${encodeURIComponent(sess.id)}/heartbeat`, 'POST', {}, 'pod');
      await loadSessions(false);
      notify('Heartbeat sent', 'success');
    } catch (err) {
      notify(`Heartbeat failed: ${err.message}`, 'error');
    }
  };

  window.refreshToken = async function refreshToken() {
    const sess = appState.activeSession;
    if (!sess) {
      notify('No active session', 'yellow');
      return;
    }

    try {
      const tokenResp = await apiRequest(`/sessions/${encodeURIComponent(sess.id)}/reconnect-token`, 'POST', {}, 'integrator');
      syncSessionState({ ...sess, ...tokenResp });
      notify('Reconnect token refreshed', 'success');
    } catch (err) {
      notify(`Token refresh failed: ${err.message}`, 'error');
    }
  };

  window.terminateSession = async function terminateSession(sessionId) {
    const target = sessionId || (appState.activeSession && appState.activeSession.id);
    if (!target) {
      notify('No active session', 'yellow');
      return;
    }

    try {
      await apiRequest(`/sessions/${encodeURIComponent(target)}/terminate`, 'POST', {}, 'integrator');
      await loadSessions(false);
      notify('Session terminated', 'blue');
    } catch (err) {
      notify(`Terminate failed: ${err.message}`, 'error');
    }
  };

  window.loadTemplate = function loadTemplate(name) {
    if (!name || !templates[name]) return;
    $('circuitCode').value = templates[name];
    window.updateCircuitStats();
  };

  window.clearCircuit = function clearCircuit() {
    $('circuitCode').value = '';
    window.updateCircuitStats();
  };

  window.updateCircuitStats = function updateCircuitStats() {
    const code = $('circuitCode').value;
    const qMatch = code.match(/qubit\[(\d+)\]/);
    const qubits = qMatch ? parseInt(qMatch[1], 10) : 0;
    const gates = (code.match(/^[a-z]+/gim) || []).length;
    $('circuit-stats').textContent = `${qubits} qubits · ~${gates} gates`;
  };

  window.submitJob = async function submitJob() {
    const btn = $('submitBtn');
    const code = $('circuitCode').value.trim();
    const backend = $('job-backend').value;
    const device = $('job-device') ? $('job-device').value : 'cpu';
    const simulationType = $('job-simulation-type') ? $('job-simulation-type').value : 'statevector';
    const jobName = $('job-name') ? $('job-name').value.trim() : '';
    const seedRaw = $('job-seed') ? $('job-seed').value.trim() : '';
    const tagsInput = $('job-tags') ? $('job-tags').value : '';
    const tags = parseTagInput(tagsInput);
    const shots = parseInt($('job-shots').value, 10);
    const sessionId = $('job-session-id').value.trim() || (appState.activeSession && appState.activeSession.id);
    const seed = seedRaw === '' ? null : parseInt(seedRaw, 10);

    if (!code) {
      notify('Circuit code is empty', 'yellow');
      return;
    }
    if (!sessionId) {
      notify('No active session. Start one first.', 'yellow');
      return;
    }
    if (seedRaw !== '' && !Number.isInteger(seed)) {
      notify('Seed must be a whole number', 'yellow');
      return;
    }

    btn.disabled = true;
    btn.innerHTML = '<div class="spinner"></div> Submitting...';

    try {
      const jobResp = await apiRequest('/jobs/submit', 'POST', {
        session_id: sessionId,
        circuit_qasm: code,
        backend,
        shots,
        device,
        simulation_type: simulationType,
        seed,
        job_name: jobName || null,
        metadata: {},
        options: {},
        tags
      }, 'pod');

      const job = normalizeJob(jobResp);
      appState.currentJobId = job.id;
      appState.jobs.unshift(job);

      $('submitResult').className = 'submit-result show';
      $('submitResult').innerHTML = `
        <div class="row-between">
          <div>
            <div style="font-size:11px;color:var(--text-muted);margin-bottom:4px">JOB SUBMITTED</div>
            <div class="td-mono" style="font-size:14px">${job.id}</div>
          </div>
          ${badgeHtmlSafe(job.status)}
        </div>
        <div class="divider"></div>
        <div class="row" style="gap:8px;flex-wrap:wrap">
          <button class="btn btn-blue btn-sm" onclick="goToJobMonitor('${job.id}')">Monitor Job</button>
          <span class="text-muted text-xs">Backend: ${job.backend} · Device: ${job.device || device} · Sim: ${job.simulation_type || simulationType} · Shots: ${job.shots}</span>
        </div>`;

      notify(`Job submitted: ${job.id}`, 'success');
    } catch (err) {
      notify(`Submit failed: ${err.message}`, 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = 'Submit Job';
    }
  };

  window.goToJobMonitor = async function goToJobMonitor(jobId) {
    appState.currentJobId = jobId;
    $('monitorJobId').value = jobId;
    window.goPage('monitor', null);
    try {
      const job = await loadJobById(jobId);
      renderJobDetail(job);
    } catch (err) {
      notify(`Load failed: ${err.message}`, 'error');
    }
  };

  window.loadJob = async function loadJob() {
    const id = $('monitorJobId').value.trim();
    if (!id) {
      notify('Enter a Job ID', 'yellow');
      return;
    }
    appState.currentJobId = id;
    try {
      const job = await loadJobById(id);
      renderJobDetail(job);
    } catch (err) {
      notify(`Job not found: ${id}`, 'error');
    }
  };

  window.loadRandomJob = async function loadRandomJob() {
    if (!appState.jobs.length) await loadJobs(false);
    if (!appState.jobs.length) {
      notify('No jobs available', 'yellow');
      return;
    }
    const pick = appState.jobs[Math.floor(Math.random() * appState.jobs.length)];
    $('monitorJobId').value = pick.id;
    appState.currentJobId = pick.id;
    renderJobDetail(pick);
  };

  window.cancelJob = async function cancelJob() {
    if (!appState.currentJobId) return;
    try {
      await apiRequest(`/jobs/${encodeURIComponent(appState.currentJobId)}/cancel`, 'POST', {}, 'pod');
      const job = await loadJobById(appState.currentJobId);
      renderJobDetail(job);
      notify('Job cancelled', 'blue');
    } catch (err) {
      notify(`Cancel failed: ${err.message}`, 'error');
    }
  };

  window.exportCurrentJob = async function exportCurrentJob() {
    const jobId = appState.currentJobId || ($('monitorJobId') ? $('monitorJobId').value.trim() : '');
    if (!jobId) {
      notify('Load a job first to export.', 'yellow');
      return;
    }

    try {
      const job = await loadJobById(jobId);
      const payload = {
        exported_at: new Date().toISOString(),
        source: 'fastqubit-frontend',
        type: 'single_job_timing_breakdown',
        timing_breakdown: buildJobTimingBreakdown(job)
      };
      const safeId = String(job.id || jobId).replace(/[^a-zA-Z0-9_-]/g, '_');
      downloadJsonFile(`fastqubit-job-timing-${safeId}-${compactIsoTimestamp()}.json`, payload);
      notify(`Exported timing for job ${job.id}`, 'success');
    } catch (err) {
      notify(`Export failed: ${err.message}`, 'error');
    }
  };

  window.exportAllJobs = async function exportAllJobs() {
    try {
      await loadJobs(true);
      const payload = {
        exported_at: new Date().toISOString(),
        source: 'fastqubit-frontend',
        type: 'all_jobs_timing_breakdown',
        total_jobs: appState.jobs.length,
        jobs: appState.jobs.map(buildJobTimingBreakdown)
      };
      downloadJsonFile(`fastqubit-jobs-timing-${compactIsoTimestamp()}.json`, payload);
      notify(`Exported timing for ${appState.jobs.length} jobs`, 'success');
    } catch (err) {
      notify(`Export failed: ${err.message}`, 'error');
    }
  };

  window.loadResultsForJob = async function loadResultsForJob() {
    if (!appState.currentJobId) return window.loadResultsQuick();
    try {
      const job = await loadJobById(appState.currentJobId);
      renderResults(job);
    } catch (err) {
      notify(`Result load failed: ${err.message}`, 'error');
    }
  };

  window.loadResultsQuick = async function loadResultsQuick() {
    await loadJobs(false);
    const completed = appState.jobs.filter((j) => (j.status || '').toLowerCase() === 'completed');
    if (!completed.length) {
      notify('No completed jobs yet', 'yellow');
      return;
    }
    renderResults(completed[0]);
  };

  window.downloadArtifact = async function downloadArtifact() {
    const jobId = $('download-artifact-btn').dataset.jobId;
    if (!jobId) return;

    try {
      const resp = await apiRequest(`/jobs/${encodeURIComponent(jobId)}/result-url`, 'GET', null, 'pod');
      if (resp && resp.available && resp.result_url) {
        window.open(resp.result_url, '_blank', 'noopener,noreferrer');
        notify('Opening artifact URL', 'success');
      } else {
        notify((resp && resp.message) || 'No external artifact for this job', 'blue');
      }
    } catch (err) {
      notify(`Artifact fetch failed: ${err.message}`, 'error');
    }
  };

  window.filterHistory = function filterHistory(filter, el) {
    document.querySelectorAll('.filter-pill').forEach((p) => p.classList.remove('active'));
    if (el) el.classList.add('active');
    appState.historyFilter = filter;
    renderHistory();
  };

  window.refreshHistory = async function refreshHistory() {
    await loadJobs(true);
    renderHistory();
  };

  window.renderResultsById = async function renderResultsById(jobId) {
    try {
      const job = await loadJobById(jobId);
      appState.currentJobId = job.id;
      renderResults(job);
    } catch (err) {
      notify(`Result load failed: ${err.message}`, 'error');
    }
  };

  // Bootstrap: restore direct auth from local storage and validate it against FastQubit.
  async function bootstrapIdentity() {
    try {
      const stored = readStoredAuth();
      if (stored) {
        appState.integratorApiKey = stored.apiKey || null;
        appState.endUserId = stored.endUserId || null;
        appState.userId = appState.endUserId;
      }
      const loginApiKeyInput = $('loginApiKeyInput');
      const loginEndUserIdInput = $('loginEndUserIdInput');
      if (loginApiKeyInput && appState.integratorApiKey) loginApiKeyInput.value = appState.integratorApiKey;
      if (loginEndUserIdInput && appState.endUserId) loginEndUserIdInput.value = appState.endUserId;
      if (!appState.integratorApiKey || !appState.endUserId) return;

      await apiRequest('/me', 'GET', null, 'integrator');
      $('loginScreen').style.display = 'none';
      $('app').style.display = 'flex';
      setSidebarUser();
      window.goPage('dashboard', null);
      await loadSessions(false);
      if (appState.activeSession) {
        await ensureActiveSessionToken(appState.activeSession);
      }
      await loadJobs(false);
      await window.refreshDashboard();
    } catch {
      clearDirectAuth();
    }
  }

  // Initial UI setup
  window.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem(THEME_KEY) || 'dark';
    applyTheme(savedTheme);
    window.updateCircuitStats();
    bootstrapIdentity();
  });
})();
