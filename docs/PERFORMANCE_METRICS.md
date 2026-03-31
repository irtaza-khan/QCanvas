# QCanvas — Performance Metrics Guide
> A Web IDE & Quantum Circuit Platform (Next.js + FastAPI + WebSocket)

This document catalogues every performance metric relevant to QCanvas — a web-based quantum circuit IDE with real-time simulation, Monaco editor integration, 3D visualizations (Three.js), and a Python FastAPI backend. Each metric is explained, anchored to a specific part of the QCanvas stack, and accompanied by measurement tools and implementation guidance.

---

## Table of Contents

1. [Core Web Vitals (User-Facing)](#1-core-web-vitals-user-facing)
   - 1.1 [Largest Contentful Paint (LCP)](#11-largest-contentful-paint-lcp)
   - 1.2 [Cumulative Layout Shift (CLS)](#12-cumulative-layout-shift-cls)
   - 1.3 [Interaction to Next Paint (INP)](#13-interaction-to-next-paint-inp)
   - 1.4 [First Contentful Paint (FCP)](#14-first-contentful-paint-fcp)
   - 1.5 [Time to First Byte (TTFB)](#15-time-to-first-byte-ttfb)
2. [IDE-Specific Frontend Metrics](#2-ide-specific-frontend-metrics)
   - 2.1 [Monaco Editor Load Time](#21-monaco-editor-load-time)
   - 2.2 [Editor Input Latency (Keystroke Lag)](#22-editor-input-latency-keystroke-lag)
   - 2.3 [Syntax Highlighting Render Time](#23-syntax-highlighting-render-time)
   - 2.4 [3D Circuit Visualization FPS](#24-3d-circuit-visualization-fps)
   - 2.5 [D3 Circuit Diagram Render Time](#25-d3-circuit-diagram-render-time)
3. [Network & API Metrics](#3-network--api-metrics)
   - 3.1 [API Response Time (Latency)](#31-api-response-time-latency)
   - 3.2 [Circuit Conversion Time](#32-circuit-conversion-time)
   - 3.3 [Simulation Execution Time](#33-simulation-execution-time)
   - 3.4 [WebSocket Latency](#34-websocket-latency)
   - 3.5 [Error Rate (API 4xx/5xx)](#35-error-rate-api-4xx5xx)
   - 3.6 [Throughput (Requests per Second)](#36-throughput-requests-per-second)
4. [Resource Utilization Metrics](#4-resource-utilization-metrics)
   - 4.1 [JavaScript Bundle Size](#41-javascript-bundle-size)
   - 4.2 [Memory Usage (Heap)](#42-memory-usage-heap)
   - 4.3 [CPU Usage (Frontend)](#43-cpu-usage-frontend)
   - 4.4 [Backend CPU & Memory](#44-backend-cpu--memory)
   - 4.5 [Database Query Time](#45-database-query-time)
   - 4.6 [Redis Cache Hit Rate](#46-redis-cache-hit-rate)
5. [Quantum-Specific Metrics](#5-quantum-specific-metrics)
   - 5.1 [Circuit Conversion Accuracy Rate](#51-circuit-conversion-accuracy-rate)
   - 5.2 [Simulation Fidelity](#52-simulation-fidelity)
   - 5.3 [Qubit Scaling Performance](#53-qubit-scaling-performance)
6. [User Experience Metrics](#6-user-experience-metrics)
   - 6.1 [Time to Interactive (TTI)](#61-time-to-interactive-tti)
   - 6.2 [Page Load Time](#62-page-load-time)
   - 6.3 [Session Error Rate](#63-session-error-rate)
   - 6.4 [Feature Adoption Rate](#64-feature-adoption-rate)
7. [Reliability & Availability Metrics](#7-reliability--availability-metrics)
   - 7.1 [Uptime / Availability](#71-uptime--availability)
   - 7.2 [Mean Time to Recovery (MTTR)](#72-mean-time-to-recovery-mttr)
   - 7.3 [WebSocket Connection Stability](#73-websocket-connection-stability)
8. [Measurement Tools Summary](#8-measurement-tools-summary)
9. [Recommended Benchmarks (Targets)](#9-recommended-benchmarks-targets)

---

## 1. Core Web Vitals (User-Facing)

Core Web Vitals are Google's standardized signals for measuring real-world user experience. They directly affect SEO ranking and user retention.

---

### 1.1 Largest Contentful Paint (LCP)

**What it is:**  
LCP measures how long it takes for the **largest visible element** on the screen to render. For QCanvas, the largest element is typically the Monaco editor pane or the circuit visualization area on the main IDE page (`/app`).

**Why it matters for QCanvas:**  
Users land on the IDE and immediately need the editor. If the Monaco editor or the sidebar takes too long to appear, users perceive the app as slow — even if it is technically loading.

**Target:** ≤ 2.5 seconds (Good), ≤ 4.0s (Needs Improvement), > 4.0s (Poor)

**How to Measure:**
```bash
# In Chrome DevTools → Lighthouse tab → Run audit
# Or in browser console:
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('LCP:', entry.startTime, 'ms', entry.element);
  }
}).observe({ type: 'largest-contentful-paint', buffered: true });
```
```bash
# CLI with PageSpeed Insights API
npx lighthouse http://localhost:3000/app --only-categories=performance --output=json
```

**How to Implement / Improve:**
1. **Lazy-load Monaco Editor** — Monaco is ~4MB. Load it only when the editor pane is in view:
   ```tsx
   // frontend/components/EditorPane.tsx
   import dynamic from 'next/dynamic';
   const MonacoEditor = dynamic(() => import('@monaco-editor/react'), {
     ssr: false,
     loading: () => <EditorSkeleton />, // skeleton placeholder
   });
   ```
2. **Preload critical fonts** — Add to `frontend/app/layout.tsx`:
   ```html
   <link rel="preload" href="/fonts/JetBrainsMono.woff2" as="font" crossOrigin="anonymous" />
   ```
3. **Use Next.js Image component** for any large hero images on the landing page.
4. **Enable Next.js `output: 'standalone'`** for smaller Docker image and faster cold starts.

---

### 1.2 Cumulative Layout Shift (CLS)

**What it is:**  
CLS measures the total unexpected visual shifts of page content during loading. A score of 0 means no shifts; any score > 0.1 is noticeable.

**Why it matters for QCanvas:**  
The editor pane, sidebar, and `ResultsPane` all load asynchronously. If the Monaco editor loads and pushes surrounding content down, users lose their place — especially damaging in an IDE.

**Target:** ≤ 0.1 (Good), ≤ 0.25 (Needs Improvement), > 0.25 (Poor)

**How to Measure:**
```javascript
// In browser console
new PerformanceObserver((list) => {
  let clsScore = 0;
  for (const entry of list.getEntries()) {
    clsScore += entry.value;
  }
  console.log('CLS Score:', clsScore);
}).observe({ type: 'layout-shift', buffered: true });
```

**How to Implement / Improve:**
1. **Reserve space for the editor** using fixed height CSS before Monaco loads:
   ```css
   /* globals.css */
   .editor-container {
     min-height: 500px; /* prevents layout shift */
   }
   ```
2. **Reserve space for the ResultsPane** (simulation output) so results appearing don't push content.
3. **Avoid injecting DOM nodes** above existing content (e.g., toast notifications from `react-hot-toast` should be positioned `fixed`).
4. **Set explicit `width` and `height`** on all `<img>` and `<canvas>` elements, including Three.js canvas.

---

### 1.3 Interaction to Next Paint (INP)

**What it is:**  
INP measures the latency from **any user interaction** (click, keypress, tap) to the **next visual update**. It replaced First Input Delay (FID) as of March 2024. It is the most critical metric for interactive apps like IDEs.

**Why it matters for QCanvas:**  
Every time a user types in the Monaco editor, clicks "Convert", runs a simulation, or expands the sidebar — the UI must respond within milliseconds. Long INP means the app feels "frozen."

**Target:** ≤ 200ms (Good), ≤ 500ms (Needs Improvement), > 500ms (Poor)

**How to Measure:**
```javascript
// Using web-vitals library (install: npm i web-vitals)
import { onINP } from 'web-vitals';
onINP((metric) => {
  console.log('INP:', metric.value, 'ms');
  // Send to analytics: sendToAnalytics(metric);
});
```

**How to Implement / Improve:**
1. **Debounce API calls** triggered by editor changes (already good practice, but verify in `EditorPane.tsx`):
   ```tsx
   const debouncedConvert = useCallback(
     debounce((code) => triggerConversion(code), 500),
     []
   );
   ```
2. **Use `startTransition`** for non-urgent state updates (e.g., updating `ResultsPane` after simulation):
   ```tsx
   import { startTransition } from 'react';
   startTransition(() => setSimulationResults(data));
   ```
3. **Offload heavy JS** (circuit parsing, local validation) to Web Workers so the main thread stays free.
4. **Avoid synchronous layout reads** (`getBoundingClientRect`, `offsetHeight`) inside event handlers.

---

### 1.4 First Contentful Paint (FCP)

**What it is:**  
FCP measures the time from navigation to when the browser **renders the first bit of content** (text, image, canvas). It tells you how fast the user sees *something*.

**Why it matters for QCanvas:**  
The landing page (`/`) and the login page (`/login`) should show content fast to avoid blank-screen abandonment.

**Target:** ≤ 1.8 seconds (Good)

**How to Measure:**
```javascript
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.name === 'first-contentful-paint') {
      console.log('FCP:', entry.startTime, 'ms');
    }
  }
}).observe({ type: 'paint', buffered: true });
```

**How to Implement / Improve:**
1. **Use Next.js Server-Side Rendering (SSR)** for pages like `/login` and `/signup` so HTML is sent pre-rendered.
2. **Inline critical CSS** — Next.js does this automatically; ensure `globals.css` is minimal for above-the-fold content.
3. **Reduce render-blocking scripts** — use `next/script` with `strategy="lazyOnload"` for non-critical scripts.

---

### 1.5 Time to First Byte (TTFB)

**What it is:**  
TTFB is the time from the browser making an HTTP request to receiving the first byte of the response. It reflects server processing speed and network latency.

**Why it matters for QCanvas:**  
Both the Next.js frontend (served by Vercel/Nginx) and the FastAPI backend contribute to TTFB. A slow `/api/convert` response delays the entire conversion workflow.

**Target:** ≤ 800ms (Good)

**How to Measure:**
```javascript
// In browser DevTools → Network tab → click any request → "Timing" tab
// Or programmatically:
const { responseStart, requestStart } = performance.timing;
console.log('TTFB:', responseStart - requestStart, 'ms');
```
```bash
# Using curl to test FastAPI backend TTFB
curl -o /dev/null -w "TTFB: %{time_starttransfer}s\n" http://localhost:8000/api/health/
```

**How to Implement / Improve:**
1. **Enable Redis caching** for repeated conversion requests (same circuit code → same output):
   ```python
   # backend/app/api/routes/converter.py
   cache_key = f"convert:{hash(source_code)}:{source_fw}:{target_fw}"
   cached = await redis.get(cache_key)
   if cached:
       return json.loads(cached)
   ```
2. **Use Uvicorn with multiple workers** in production:
   ```bash
   uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
   ```
3. **Enable HTTP/2** via Nginx reverse proxy to multiplex requests.

---

## 2. IDE-Specific Frontend Metrics

These metrics are unique to QCanvas as a **web-based IDE** and directly affect the code editing experience.

---

### 2.1 Monaco Editor Load Time

**What it is:**  
The time from page navigation to when Monaco editor becomes fully interactive (ready to accept input, syntax highlighting applied).

**Why it matters for QCanvas:**  
Monaco (`@monaco-editor/react`) is the core of the QCanvas IDE. If it takes 5+ seconds to load, the app is unusable. Monaco is a large library (~4MB minified) with Web Workers.

**Target:** ≤ 2 seconds after page load

**How to Measure:**
```tsx
// In EditorPane.tsx — track Monaco mount time
const editorMountStart = useRef(performance.now());

<Editor
  onMount={(editor) => {
    const loadTime = performance.now() - editorMountStart.current;
    console.log('Monaco Load Time:', loadTime.toFixed(2), 'ms');
    // Log to analytics
  }}
/>
```

**How to Implement / Improve:**
1. **Code-split Monaco** with `next/dynamic` (see §1.1) to avoid blocking initial page render.
2. **Configure Monaco Web Workers** explicitly to prevent them from being lazy-loaded at first keystroke:
   ```tsx
   // In _app.tsx or layout.tsx
   import { loader } from '@monaco-editor/react';
   loader.config({ paths: { vs: '/monaco-editor/min/vs' } }); // serve locally
   ```
3. **Preload Monaco chunk** using `<link rel="modulepreload">` after initial page load:
   ```tsx
   // In layout.tsx
   <link rel="modulepreload" href="/_next/static/chunks/monaco.js" />
   ```

---

### 2.2 Editor Input Latency (Keystroke Lag)

**What it is:**  
The time from when a user presses a key to when the character appears in the Monaco editor. Ideally this should feel instantaneous (< 16ms = one frame at 60fps).

**Why it matters for QCanvas:**  
Quantum circuit code can be complex (multi-line Qiskit/Cirq code). If the editor lags during typing, it breaks the developer flow and makes QCanvas feel unprofessional.

**Target:** ≤ 16ms (imperceptible), ≤ 50ms (acceptable)

**How to Measure:**
```tsx
// Custom hook to measure editor keystroke latency
useEffect(() => {
  if (!editorRef.current) return;
  const model = editorRef.current.getModel();
  model?.onDidChangeContent(() => {
    // Monaco fires this synchronously after content change
    // Track with performance.mark / measure
    performance.mark('keystroke-processed');
    performance.measure('keystroke-latency', 'keystroke-start', 'keystroke-processed');
  });
}, []);
```

**How to Implement / Improve:**
1. **Disable expensive Monaco features** for large files (e.g., turn off code folding, minimap for files > 500 lines):
   ```tsx
   <Editor
     options={{
       minimap: { enabled: lineCount < 300 },
       folding: lineCount < 500,
       renderWhitespace: 'none',
     }}
   />
   ```
2. **Do not run circuit validation on every keystroke** — debounce validation to every 500ms.
3. **Use `useCallback` and `useMemo`** to prevent unnecessary re-renders of `EditorPane`.

---

### 2.3 Syntax Highlighting Render Time

**What it is:**  
The time Monaco takes to apply syntax highlighting (tokenization) after a code change. For custom languages (OpenQASM, Cirq-specific syntax), this depends on the grammar definition complexity.

**Target:** ≤ 100ms for circuits up to 1000 lines

**How to Measure:**
```tsx
// Use Monaco's internal tokenization APIs
const model = monaco.editor.getModels()[0];
const start = performance.now();
monaco.editor.tokenize(model.getValue(), 'qasm'); // force tokenization
console.log('Tokenization time:', performance.now() - start, 'ms');
```

**How to Implement / Improve:**
1. **Register custom Monaco language** for OpenQASM 3.0 with an efficient tokenizer (avoid overly complex regex patterns):
   ```tsx
   // In EditorPane.tsx
   monaco.languages.register({ id: 'openqasm' });
   monaco.languages.setMonarchTokensProvider('openqasm', qasmTokenizer);
   ```
2. **Use incremental tokenization** — Monaco does this by default; avoid calling `model.getValue()` in hot paths.

---

### 2.4 3D Circuit Visualization FPS

**What it is:**  
Frames Per Second (FPS) rendered by the Three.js / React Three Fiber (`@react-three/fiber`, `@react-three/drei`) 3D circuit visualization (`CircuitVisualization3D.tsx`). 60 FPS is the target for smooth visuals.

**Why it matters for QCanvas:**  
The 3D Bloch sphere and circuit gate visualizations are flagship QCanvas features. Dropped frames make the app feel laggy and damage the premium feel.

**Target:** ≥ 60 FPS (ideal), ≥ 30 FPS (minimum acceptable)

**How to Measure:**
```tsx
// Using @react-three/fiber's performance monitor
import { PerformanceMonitor } from '@react-three/drei';

<Canvas>
  <PerformanceMonitor
    onIncline={() => console.log('Performance improving')}
    onDecline={() => console.log('FPS dropping — reduce quality')}
    onChange={({ factor }) => setDpr(Math.floor(0.5 + 1.5 * factor, 2))}
  />
  {/* ... scene objects */}
</Canvas>
```
```tsx
// Manual FPS counter using useFrame
import { useFrame } from '@react-three/fiber';
const lastTime = useRef(performance.now());
useFrame(() => {
  const now = performance.now();
  const fps = 1000 / (now - lastTime.current);
  lastTime.current = now;
  // Display or log fps
});
```

**How to Implement / Improve:**
1. **Adaptive DPR (Device Pixel Ratio)** — lower resolution on low-end devices:
   ```tsx
   <Canvas dpr={[1, 2]} performance={{ min: 0.5 }}>
   ```
2. **Instanced meshes** for repeated gate objects (e.g., many Hadamard gates with the same geometry):
   ```tsx
   import { Instances, Instance } from '@react-three/drei';
   // Render 100 gates with 1 draw call instead of 100
   ```
3. **Suspend non-visible 3D scenes** when the tab is not active using the Page Visibility API.
4. **Use `dispose()` on Three.js geometries/materials** when the component unmounts to prevent memory leaks.

---

### 2.5 D3 Circuit Diagram Render Time

**What it is:**  
The time to render / re-render the 2D circuit diagram (`CircuitVisualization.tsx`) built with D3.js after receiving a new circuit from the API.

**Target:** ≤ 200ms for circuits with up to 50 qubits and 200 gates

**How to Measure:**
```tsx
const renderStart = performance.now();
renderCircuitDiagram(circuitData); // your D3 render function
const renderTime = performance.now() - renderStart;
console.log('D3 Render Time:', renderTime.toFixed(2), 'ms');
```

**How to Implement / Improve:**
1. **Use `d3.join()` for incremental DOM updates** instead of clearing and re-drawing the entire SVG.
2. **Virtualize large circuits** — only render gates visible in the current scroll window.
3. **Memoize D3 scale computations** with `useMemo` since scales don't change unless qubit count changes.

---

## 3. Network & API Metrics

---

### 3.1 API Response Time (Latency)

**What it is:**  
The total round-trip time from when the frontend sends an HTTP request to when it receives the complete response. Measured for all FastAPI endpoints.

**Why it matters for QCanvas:**  
Every "Convert" and "Simulate" button click triggers an API call. Users equate API speed with app speed.

**Targets by endpoint:**
| Endpoint | Target |
|---|---|
| `GET /api/health/` | ≤ 50ms |
| `POST /api/convert/` | ≤ 500ms |
| `POST /api/simulate/` | ≤ 2000ms |
| `GET /api/convert/frameworks` | ≤ 100ms |
| Auth endpoints | ≤ 200ms |

**How to Measure:**
```typescript
// In frontend API utility
const start = performance.now();
const response = await fetch('/api/convert', { method: 'POST', body: ... });
const latency = performance.now() - start;
console.log('API Latency:', latency.toFixed(1), 'ms');
```
```python
# FastAPI middleware to log response time (backend/app/main.py)
import time
from starlette.middleware.base import BaseHTTPMiddleware

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = (time.perf_counter() - start) * 1000
        response.headers['X-Response-Time'] = f"{duration:.2f}ms"
        return response

app.add_middleware(TimingMiddleware)
```

**How to Implement / Improve:**
1. **Redis caching** for identical conversion requests (same input hash → cache lookup).
2. **Async database operations** — use SQLAlchemy async sessions to avoid blocking Uvicorn's event loop.
3. **Background tasks** via FastAPI `BackgroundTasks` for logging/stats that don't need to block the response.

---

### 3.2 Circuit Conversion Time

**What it is:**  
The server-side time to convert a quantum circuit between frameworks (e.g., Cirq → Qiskit via OpenQASM 3.0). This is the core computational metric for QCanvas's primary feature.

**Target:** ≤ 300ms for circuits ≤ 20 qubits / 100 gates

**How to Measure:**
```python
# In backend/app/api/routes/converter.py
import time

@router.post("/convert/")
async def convert_circuit(request: ConversionRequest):
    start = time.perf_counter()
    result = await conversion_service.convert(request)
    duration_ms = (time.perf_counter() - start) * 1000
    
    # Include in response for frontend display
    return ConversionResponse(
        ...result,
        conversion_time_ms=round(duration_ms, 2)
    )
```

**How to Implement / Improve:**
1. **Profile the conversion pipeline** to find bottlenecks: parsing, OpenQASM generation, or target framework compilation.
2. **Cache OpenQASM intermediate** — if converting Cirq→Qiskit and Cirq→PennyLane, reuse the OpenQASM generation step.
3. **Use `asyncio.run_in_executor`** to run blocking quantum library calls in a thread pool:
   ```python
   import asyncio
   loop = asyncio.get_event_loop()
   result = await loop.run_in_executor(None, blocking_conversion_fn, args)
   ```

---

### 3.3 Simulation Execution Time

**What it is:**  
The time taken by the quantum simulator (statevector/density matrix/stabilizer) to execute a circuit and return results. This is compute-bound and scales exponentially with qubit count.

**Target (simulation only, server-side):**
| Qubits | Target |
|---|---|
| ≤ 10 qubits | ≤ 1 second |
| 11–20 qubits | ≤ 10 seconds |
| > 20 qubits | Background job with WebSocket updates |

**How to Measure:**
```python
# In backend/app/api/routes/simulator.py
from app.utils.logging import performance_logger

@router.post("/simulate/")
async def simulate_circuit(request: SimulationRequest):
    with performance_logger.timer("simulation_execution"):
        result = await simulator.run(request)
    return result
```

**How to Implement / Improve:**
1. **Enforce qubit limits** — reject requests > N qubits (configurable in `settings.py`):
   ```python
   MAX_QUBITS_SYNC = 20  # sync response
   MAX_QUBITS_ASYNC = 30  # WebSocket background job
   ```
2. **Use optimized backends** — PennyLane's `lightning.qubit` is significantly faster than the default for statevector simulation.
3. **Stream results** via WebSocket for long-running simulations so users see partial progress:
   ```python
   await websocket_manager.broadcast({"type": "progress", "percent": 45})
   ```

---

### 3.4 WebSocket Latency

**What it is:**  
The round-trip time of a WebSocket message from the frontend to the FastAPI backend and back. WebSockets are used in QCanvas for real-time simulation progress updates.

**Target:** ≤ 50ms round-trip (on localhost), ≤ 200ms (production)

**How to Measure:**
```typescript
// Ping-pong latency measurement
const ws = new WebSocket('ws://localhost:8000/ws');
let pingTime: number;

ws.onopen = () => {
  pingTime = performance.now();
  ws.send(JSON.stringify({ type: 'ping' }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === 'pong') {
    console.log('WS RTT:', performance.now() - pingTime, 'ms');
  }
};
```

**How to Implement / Improve:**
1. **Add ping/pong heartbeat** in `backend/app/core/websocket_manager.py` to detect stale connections.
2. **Use binary frames** (`ArrayBuffer`) instead of JSON strings for large numeric simulation results.
3. **Reconnect logic** on the frontend with exponential backoff when connection drops.

---

### 3.5 Error Rate (API 4xx/5xx)

**What it is:**  
The percentage of API requests that return client errors (4xx) or server errors (5xx). A high rate indicates bugs, invalid inputs, or infrastructure problems.

**Target:** < 1% server errors (5xx), < 5% client errors (4xx) during normal operation

**How to Measure:**
```python
# FastAPI middleware to count errors
# backend/app/main.py
from prometheus_client import Counter

request_error_counter = Counter(
    'qcanvas_http_errors_total',
    'Total HTTP errors',
    ['method', 'path', 'status_code']
)

# Track in middleware after response
if response.status_code >= 400:
    request_error_counter.labels(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code
    ).inc()
```

**How to Implement / Improve:**
1. **Return descriptive error responses** with `QCanvasException` subtypes so the frontend can display helpful messages.
2. **Add input validation** via Pydantic models for all API endpoints to catch 422 errors early.
3. **Monitor via Prometheus + Grafana** (already in `docker-compose.yml`).

---

### 3.6 Throughput (Requests per Second)

**What it is:**  
The number of API requests the FastAPI backend can handle per second before response times degrade. This matters for concurrent users.

**Target:** ≥ 50 req/s for `/api/convert/` under load

**How to Measure:**
```bash
# Using Apache Bench (ab) — install via chocolatey on Windows
ab -n 1000 -c 50 -p circuit_payload.json -T application/json \
   http://localhost:8000/api/convert/

# Using Locust (Python-based load testing)
pip install locust
# Create locustfile.py and run: locust --headless -u 50 -r 10 -H http://localhost:8000
```

**How to Implement / Improve:**
1. **Scale Uvicorn workers** to match CPU cores: `--workers $(nproc)`.
2. **Add a rate limiter** using `slowapi` to protect against abuse:
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   @limiter.limit("10/minute")
   async def convert_circuit(...):
   ```
3. **Use async database sessions** to prevent thread-blocking under load.

---

## 4. Resource Utilization Metrics

---

### 4.1 JavaScript Bundle Size

**What it is:**  
The total size of JavaScript files the browser must download to run the QCanvas frontend. Smaller bundles = faster loads. QCanvas has heavy dependencies: Monaco (~4MB), Three.js (~600KB), D3 (~280KB).

**Target:**
| Bundle | Target |
|---|---|
| Initial page load JS (First Load JS) | ≤ 250KB gzipped |
| Total JS | ≤ 2MB gzipped |
| Monaco chunk (lazy-loaded) | Acceptable up to 4MB, loaded on demand |

**How to Measure:**
```bash
# Analyze Next.js bundle
cd frontend
npm run build
# Next.js prints bundle sizes after build

# For detailed analysis:
npx @next/bundle-analyzer
# Add to next.config.js:
# const withBundleAnalyzer = require('@next/bundle-analyzer')({ enabled: true })
```

**How to Implement / Improve:**
1. **Dynamic imports** for Monaco, Three.js, and D3 — load only when the user navigates to the IDE page.
2. **Tree-shake D3** — import only needed submodules:
   ```tsx
   import { select } from 'd3-selection'; // instead of 'd3'
   import { scaleLinear } from 'd3-scale';
   ```
3. **Use `next/dynamic`** with `ssr: false` for Three.js components (they can't SSR anyway).
4. **Check `_next/static/chunks`** output — split vendor chunks from app code.

---

### 4.2 Memory Usage (Heap)

**What it is:**  
The amount of JavaScript heap memory consumed by the QCanvas frontend. Monaco editor, Three.js scene, and D3 SVG nodes can collectively consume hundreds of MB if not managed.

**Target:** ≤ 200MB heap in steady state (with editor open)

**How to Measure:**
```javascript
// Chrome DevTools → Memory tab → Take Heap Snapshot
// Or programmatically (Chrome only):
const mem = performance.memory;
console.log({
  used: (mem.usedJSHeapSize / 1024 / 1024).toFixed(2) + ' MB',
  total: (mem.totalJSHeapSize / 1024 / 1024).toFixed(2) + ' MB',
  limit: (mem.jsHeapSizeLimit / 1024 / 1024).toFixed(2) + ' MB',
});
```

**How to Implement / Improve:**
1. **Dispose Three.js objects** when `CircuitVisualization3D` unmounts:
   ```tsx
   useEffect(() => {
     return () => {
       geometry.dispose();
       material.dispose();
       renderer.dispose();
     };
   }, []);
   ```
2. **Clear Monaco editor models** when switching between circuits; do not accumulate stale models.
3. **Limit simulation result history** stored in Zustand store — keep only the last N results.

---

### 4.3 CPU Usage (Frontend)

**What it is:**  
Browser main-thread and worker CPU utilization. High CPU leads to dropped frames (low FPS) and sluggish UI.

**Target:** Main thread idle > 60% during normal editing

**How to Measure:**
```bash
# Chrome DevTools → Performance tab → Record → Interact → Stop
# Look for "Long Tasks" (red bars) > 50ms — these block interaction
# Also check "Main" thread breakdown: scripting vs rendering vs painting
```

**How to Implement / Improve:**
1. **Move circuit validation to a Web Worker** to avoid blocking the main thread during complex gate syntax checking.
2. **Use `React.memo`** on expensive components like `ResultsPane`, `Sidebar`, and `CircuitVisualization`:
   ```tsx
   export default React.memo(ResultsPane);
   ```
3. **Profile with `React DevTools Profiler`** to find components that re-render unnecessarily.
4. **Avoid `useEffect` with heavy computation** — use `useMemo` or off-thread workers.

---

### 4.4 Backend CPU & Memory

**What it is:**  
CPU and memory usage of the FastAPI + Uvicorn process and quantum simulation workers. Quantum simulation is compute-intensive and can spike to 100% CPU for large circuits.

**Target:**
| Metric | Target |
|---|---|
| Idle CPU | ≤ 5% |
| Peak CPU (during simulation) | ≤ 80% per core |
| Memory (baseline) | ≤ 512MB |
| Memory (during 20-qubit sim) | ≤ 4GB |

**How to Measure:**
```bash
# Docker stats (when running with docker-compose)
docker stats qcanvas-backend

# Prometheus metrics endpoint (already configured in project)
curl http://localhost:8000/metrics

# Python-level profiling
pip install py-spy
py-spy top --pid <uvicorn_pid>
```

**How to Implement / Improve:**
1. **Set memory limits** in `docker-compose.yml`:
   ```yaml
   backend:
     mem_limit: 4g
     cpus: '2.0'
   ```
2. **Implement circuit size limits** before simulation begins (enforce in Pydantic model validator).
3. **Use Celery + Redis** for long-running simulations to avoid holding Uvicorn threads:
   ```python
   # Offload to Celery task
   task = simulate_circuit_async.delay(circuit_data)
   return {"task_id": task.id}
   ```

---

### 4.5 Database Query Time

**What it is:**  
The time taken by SQLAlchemy to execute queries against PostgreSQL (user data, conversion history, project saves). Slow queries degrade API response times.

**Target:** ≤ 10ms for simple lookups, ≤ 50ms for complex joins

**How to Measure:**
```python
# SQLAlchemy query timing with events
from sqlalchemy import event

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.perf_counter()

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = (time.perf_counter() - context._query_start_time) * 1000
    if total > 50:  # log slow queries
        logger.warning(f"Slow query ({total:.1f}ms): {statement[:100]}")
```

**How to Implement / Improve:**
1. **Add database indexes** on frequently queried columns (user ID, project ID, conversion timestamps).
2. **Use SQLAlchemy `selectinload`** instead of lazy loading related objects.
3. **Connection pooling** — configure a pool size appropriate for the number of workers:
   ```python
   engine = create_async_engine(DATABASE_URL, pool_size=10, max_overflow=20)
   ```

---

### 4.6 Redis Cache Hit Rate

**What it is:**  
The percentage of cache lookups that find a valid cached result. A high hit rate means fewer expensive computations.

**Target:** ≥ 70% hit rate for conversion requests

**How to Measure:**
```bash
# Redis CLI
redis-cli info stats | grep keyspace_hits
redis-cli info stats | grep keyspace_misses

# Hit rate = hits / (hits + misses) * 100
```
```python
# Prometheus metric
cache_hit_counter = Counter('qcanvas_cache_hits_total', 'Cache hits', ['operation'])
cache_miss_counter = Counter('qcanvas_cache_misses_total', 'Cache misses', ['operation'])
```

**How to Implement / Improve:**
1. **Cache converted circuits** keyed by `hash(source_code + source_fw + target_fw)` with a TTL of 1 hour.
2. **Cache simulation results** for identical circuits + parameters.
3. **Use Redis pipeline** to batch multiple cache operations into a single round-trip.

---

## 5. Quantum-Specific Metrics

These are metrics unique to QCanvas as a quantum computing platform.

---

### 5.1 Circuit Conversion Accuracy Rate

**What it is:**  
The percentage of conversion requests that produce a **functionally equivalent** output circuit. A converted circuit should implement the same unitary transformation as the original.

**Target:** ≥ 99% accuracy across supported gate sets

**How to Measure:**
```python
# In tests/test_conversion_accuracy.py
import numpy as np
from qiskit import QuantumCircuit
from cirq.testing import assert_allclose_up_to_global_phase

def test_cirq_to_qiskit_accuracy(cirq_circuit):
    """Verify converted circuit produces same unitary."""
    original_unitary = cirq.unitary(cirq_circuit)
    
    qasm = convert_cirq_to_qasm(cirq_circuit)
    qiskit_circuit = QuantumCircuit.from_qasm_str(qasm)
    converted_unitary = qiskit.quantum_info.Operator(qiskit_circuit).data
    
    np.testing.assert_allclose(
        original_unitary, converted_unitary, atol=1e-6
    )
    
# Track pass rate across test suite
accuracy_rate = passed_tests / total_tests * 100
```

**How to Implement / Improve:**
1. **Unit test every supported gate** in the conversion pipeline against known unitaries.
2. **Use `ConversionResult.warnings`** to flag partial conversions (unsupported gates become blanks).
3. **Report conversion accuracy** in the API response so frontend can warn users:
   ```json
   { "accuracy_warning": "2 gates could not be exactly represented in target framework" }
   ```

---

### 5.2 Simulation Fidelity

**What it is:**  
How closely the simulator's output matches the theoretically correct quantum state. For ideal (noise-free) simulators, fidelity should be 1.0 (perfect). With noise models, it measures how real-world-like the simulation is.

**Target:** Fidelity ≥ 0.999 for ideal statevector simulation

**How to Measure:**
```python
# Compare simulated state to analytically known state
import numpy as np
from qiskit.quantum_info import state_fidelity, Statevector

def compute_fidelity(circuit, expected_state):
    """Compare simulated vs expected quantum state."""
    simulated = Statevector.from_instruction(circuit)
    expected = Statevector(expected_state)
    fidelity = state_fidelity(simulated, expected)
    return fidelity

# Example: Bell state should have fidelity 1.0
bell_fidelity = compute_fidelity(bell_circuit, bell_expected)
assert bell_fidelity > 0.999, f"Fidelity too low: {bell_fidelity}"
```

**How to Implement / Improve:**
1. **Run fidelity tests** as part of CI/CD pipeline for all example circuits.
2. **Display fidelity information** in `ResultsPane` when a noise model is applied.
3. **Validate simulation backends** against Qiskit's statevector simulator as a reference.

---

### 5.3 Qubit Scaling Performance

**What it is:**  
How simulation time grows as qubit count increases. Statevector simulation is exponential (O(2^n)) in memory and time. This metric tracks where QCanvas becomes impractical.

**Target / Expectation:**
| Qubits | Expected Simulation Time |
|---|---|
| 5 | < 10ms |
| 10 | < 100ms |
| 15 | < 2 seconds |
| 20 | < 30 seconds |
| 25+ | Background job required |

**How to Measure:**
```python
# Benchmark script: benchmarks/qubit_scaling.py
import time
import numpy as np

for n_qubits in range(5, 26):
    circuit = create_random_circuit(n_qubits, depth=10)
    start = time.perf_counter()
    simulate(circuit)
    elapsed = time.perf_counter() - start
    print(f"n={n_qubits}: {elapsed:.3f}s, memory≈{2**(n_qubits+4)/1e9:.2f}GB")
```

**How to Implement / Improve:**
1. **Enforce qubit limits** in the API (`MAX_QUBITS_SYNC = 20`) and display clear error messages.
2. **Offer automatic backend selection** — for n > 15 qubits, switch to a faster backend like `lightning.qubit`.
3. **Show expected execution time** in the UI before the user submits a large simulation.

---

## 6. User Experience Metrics

---

### 6.1 Time to Interactive (TTI)

**What it is:**  
The time from page load until the page is **reliably interactive** — all main-thread scripts have run, the editor is mounted, and the user can start typing.

**Target:** ≤ 5 seconds on a typical broadband connection

**How to Measure:**
```bash
# Google Lighthouse (includes TTI in report)
npx lighthouse http://localhost:3000/app --only-categories=performance

# Or in DevTools → Performance → "Time to Interactive" marker
```

**How to Implement / Improve:**
1. **Minimize long tasks (> 50ms)** on the main thread during page load.
2. **Defer non-critical initialization** (e.g., initializing D3 scales, loading example circuits) until after TTI.
3. **Show a skeleton UI** immediately so users feel the app is responsive even before TTI.

---

### 6.2 Page Load Time

**What it is:**  
The total time for all page resources (HTML, CSS, JS, fonts, images) to fully load. Measured by the browser's `load` event.

**Target:** ≤ 3 seconds on a 4G connection

**How to Measure:**
```javascript
window.addEventListener('load', () => {
  const { loadEventEnd, navigationStart } = performance.timing;
  console.log('Page Load Time:', loadEventEnd - navigationStart, 'ms');
});
```

**How to Implement / Improve:**
1. **Enable Next.js Image optimization** for all images.
2. **Use `next/font`** for self-hosted fonts to eliminate external font round-trips.
3. **Enable gzip/brotli compression** in Nginx.

---

### 6.3 Session Error Rate

**What it is:**  
The percentage of user sessions in which at least one unhandled JavaScript error, failed API call, or crash occurs.

**Target:** < 2% of sessions experience an error

**How to Measure:**
```tsx
// Global error boundary in layout.tsx
class ErrorBoundary extends React.Component {
  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Report to Sentry or your analytics
    reportError({ error: error.message, stack: info.componentStack });
  }
}
```
```bash
# Set up Sentry for automatic error tracking
npm install @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
```

**How to Implement / Improve:**
1. **Wrap all async operations** in try/catch with user-friendly toast messages via `react-hot-toast`.
2. **Add global `window.onerror`** and `window.onunhandledrejection` handlers to catch all errors.
3. **Validate API responses** in the frontend before rendering to catch malformed data.

---

### 6.4 Feature Adoption Rate

**What it is:**  
The percentage of active users who use a specific feature. Helps prioritize which features to optimize (no point optimizing a feature nobody uses).

**Target:** > 50% of users use the circuit converter weekly

**How to Measure:**
```tsx
// Simple analytics event tracking
const trackEvent = (event: string, properties?: Record<string, unknown>) => {
  // Send to Plausible (privacy-friendly) or custom endpoint
  fetch('/api/analytics/event', {
    method: 'POST',
    body: JSON.stringify({ event, properties, timestamp: Date.now() }),
  });
};

// In TopBar.tsx — track convert button clicks
<button onClick={() => { trackEvent('circuit_convert', { source: sourceFramework }); handleConvert(); }}>
  Convert
</button>
```

---

## 7. Reliability & Availability Metrics

---

### 7.1 Uptime / Availability

**What it is:**  
The percentage of time the QCanvas service is accessible. Measured as `(total_time - downtime) / total_time * 100`.

**Target:** ≥ 99.5% uptime (< 44 minutes downtime/month)

**How to Measure:**
```bash
# Use the existing health check endpoint
# backend/app/api/routes/health.py → GET /api/health/ready

# External monitoring with UptimeRobot (free tier)
# Or cron-based internal check:
*/5 * * * * curl -f http://localhost:8000/api/health/simple || alert_team
```

**How to Implement / Improve:**
1. **Configure Docker health checks** — already present in `docker-compose.yml`, ensure `restart: always`.
2. **Kubernetes readiness probes** at `/api/health/ready` for cloud deployments.
3. **Graceful shutdown** — handle `SIGTERM` in FastAPI to finish in-flight requests before stopping.

---

### 7.2 Mean Time to Recovery (MTTR)

**What it is:**  
The average time it takes to restore service after a failure. This includes detecting the failure, diagnosing, and deploying a fix.

**Target:** MTTR ≤ 30 minutes for minor failures

**How to Measure:**
```
MTTR = Total Downtime / Number of Incidents
```
Track incidents with timestamps in a runbook or issue tracker.

**How to Implement / Improve:**
1. **Structured logging** — already implemented in `backend/app/utils/logging.py`. Ensure all errors include full context.
2. **Grafana alerts** triggered by Prometheus metrics (e.g., error rate spike, CPU > 90%) to detect issues before users report them.
3. **Docker auto-restart** (`restart: always`) for quick recovery from crashes.
4. **Database backups** — PostgreSQL daily backups with tested restore procedure.

---

### 7.3 WebSocket Connection Stability

**What it is:**  
The percentage of WebSocket sessions that complete without unexpected disconnection or message loss.

**Target:** ≥ 99% of WebSocket sessions complete without unexpected drops

**How to Measure:**
```python
# Track in backend/app/core/websocket_manager.py
ws_connection_counter = Counter('qcanvas_ws_connections_total', 'WebSocket connections', ['status'])

# On connect:
ws_connection_counter.labels(status='connected').inc()

# On disconnect:
ws_connection_counter.labels(status='disconnected').inc()

# Error rate = disconnected_unexpectedly / total_connected
```

**How to Implement / Improve:**
1. **Heartbeat / ping-pong** every 30 seconds to keep connections alive through proxies.
2. **Client-side auto-reconnect** with exponential backoff (50ms → 100ms → 200ms → ...).
3. **Message acknowledgment** — have the frontend confirm receipt of simulation progress messages.

---

## 8. Measurement Tools Summary

| Tool | What It Measures | Integration |
|---|---|---|
| **Google Lighthouse** | LCP, CLS, INP, FCP, TTI, bundle size | Run via Chrome DevTools or CLI |
| **Chrome DevTools** | All browser metrics, memory, network, CPU profiling | Built into Chrome |
| **web-vitals (npm)** | Core Web Vitals in production | `npm install web-vitals` |
| **Next.js Bundle Analyzer** | JS bundle sizes per chunk | `@next/bundle-analyzer` |
| **Prometheus** | Backend request rates, error rates, custom metrics | Already in `docker-compose.yml` |
| **Grafana** | Visualization of Prometheus metrics | Already in `docker-compose.yml` |
| **Locust** | Load testing, throughput, concurrent users | `pip install locust` |
| **Apache Bench (ab)** | Simple load testing | `choco install apache-httpd` |
| **Redis CLI** | Cache hit/miss rates | `redis-cli info stats` |
| **py-spy** | Python CPU profiling | `pip install py-spy` |
| **Sentry** | Frontend/backend error tracking | `@sentry/nextjs` |
| **React DevTools Profiler** | Component render times, unnecessary re-renders | Browser extension |
| **@react-three/drei PerformanceMonitor** | Three.js FPS | Already a dependency |
| **Docker Stats** | Container CPU & memory in real-time | `docker stats` |

---

## 9. Recommended Benchmarks (Targets)

A consolidated quick-reference table for all metrics:

| Metric | Tool | Good Target | Action if Violated |
|---|---|---|---|
| **LCP** | Lighthouse | ≤ 2.5s | Lazy-load Monaco, optimize images |
| **CLS** | Lighthouse | ≤ 0.1 | Reserve layout space for editor |
| **INP** | web-vitals | ≤ 200ms | Debounce API calls, use startTransition |
| **FCP** | Lighthouse | ≤ 1.8s | Use SSR, inline critical CSS |
| **TTFB** | curl / DevTools | ≤ 800ms | Redis caching, async DB queries |
| **Monaco Load Time** | Custom mark | ≤ 2s | Dynamic import, local CDN |
| **Keystroke Latency** | Custom mark | ≤ 16ms | Avoid sync work in editor handlers |
| **3D FPS** | PerformanceMonitor | ≥ 60 FPS | Instanced meshes, adaptive DPR |
| **Circuit Conversion Time** | API header | ≤ 500ms | Redis cache, async executor |
| **Simulation Time (10q)** | API header | ≤ 2s | lightning.qubit backend, qubit limits |
| **WebSocket Latency** | Custom ping | ≤ 50ms local | Heartbeats, binary frames |
| **API Error Rate** | Prometheus | < 1% (5xx) | Pydantic validation, error handling |
| **Bundle Size (initial)** | Bundle Analyzer | ≤ 250KB gz | Tree-shake D3, dynamic imports |
| **Heap Memory** | DevTools Memory | ≤ 200MB | Dispose Three.js objects, limit history |
| **DB Query Time** | SQLAlchemy events | ≤ 50ms | Add indexes, connection pooling |
| **Redis Hit Rate** | redis-cli | ≥ 70% | Cache by circuit hash, set TTL |
| **Conversion Accuracy** | Unit tests | ≥ 99% | Test all gate mappings |
| **Simulation Fidelity** | State fidelity | ≥ 0.999 | Validate against reference simulator |
| **Uptime** | Health checks | ≥ 99.5% | Docker restart policies, health probes |
| **Session Error Rate** | Sentry | < 2% | Error boundaries, API try/catch |

---

*Last updated: March 2026 | QCanvas v0.1.0 | Stack: Next.js 14 + FastAPI + PennyLane/Qiskit/Cirq*
