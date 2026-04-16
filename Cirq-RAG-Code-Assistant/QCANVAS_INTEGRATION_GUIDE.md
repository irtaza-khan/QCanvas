# QCanvas × Cirq-RAG-Code-Assistant — Integration Guide

> **Author**: Umer Farooq  
> **Purpose**: This document tells the QCanvas frontend team everything they need to know to integrate the Cirq-RAG-Code-Assistant backend. It covers what the backend does, how to talk to it, and what the frontend must functionally support. All UI/UX decisions (layout, icons, theme, placement) are entirely up to the QCanvas team.

---

## Table of Contents

1. [What Is This Backend?](#1-what-is-this-backend)
2. [How the Pipeline Works](#2-how-the-pipeline-works)
3. [Running the Backend Locally](#3-running-the-backend-locally)
4. [API Reference](#4-api-reference)
5. [TypeScript Types & API Client](#5-typescript-types--api-client)
6. [Vite Proxy Setup (Dev)](#6-vite-proxy-setup-dev)
7. [Frontend Functional Requirements](#7-frontend-functional-requirements)
8. [Error Handling & Edge Cases](#8-error-handling--edge-cases)
9. [Context Injection Feature](#9-context-injection-feature)

---

## 1. What Is This Backend?

The **Cirq-RAG-Code-Assistant** is a **multi-agent AI backend** that takes a natural language description from the user and returns a fully generated, optimized, validated, and explained **Google Cirq quantum circuit**.

Tech stack:
- **FastAPI + Uvicorn** (Python 3.11) — HTTP server
- **AWS Bedrock** — LLM provider (separate Claude model per agent)
- **FAISS vector store** — RAG knowledge base (Cirq docs + code examples)
- **Amazon Nova embeddings** — text-to-vector for RAG retrieval
- **Cirq local simulator** — Python-level circuit validation

The backend is **stateless per request**. Every call to `POST /api/v1/generate` runs the full pipeline independently. There is no user session, no persistent database. In-memory run history is available but resets on server restart.

---

## 2. How the Pipeline Works

When the frontend sends a prompt, the backend runs this pipeline internally:

```
User Prompt (natural language)
        │
        ▼
  Designer Agent        ← Always runs. Queries the RAG knowledge base, then calls
                          AWS Bedrock to generate an initial Cirq Python circuit.
        │
        ▼
  Validator Agent       ← Conditional (on by default). Compiles and runs the circuit
                          on a local Cirq simulator to check correctness.
        │
        ▼
  Optimizer Agent       ← Conditional (on by default). Calls AWS Bedrock to reduce
                          gate depth, decompose gates, and improve the circuit.
                          Loops back to re-validate up to N times (default 3).
        │
        ▼
  Final Validator       ← Always runs. One last simulation check on the optimized circuit.
        │
        ▼
  Educational Agent     ← Always runs last. Generates a depth-adaptive Markdown explanation
                          of the final circuit for the user.
        │
        ▼
  Single JSON Response  ← Everything above returns in one HTTP response.
```

**Important:** The API is **synchronous**. There is no streaming. The frontend sends one request and waits for the full response. Depending on prompt complexity and AWS latency, this typically takes **15–60 seconds**.

---

## 3. Running the Backend Locally

### Prerequisites

- Python 3.11+
- The `venv/` virtual environment set up (run `setup-dev.ps1` once)
- AWS credentials in `.env` (already filled in the project)

### Start Command

```powershell
# From the Cirq-RAG-Code-Assistant project root:
.\venv\Scripts\Activate.ps1
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

The server runs at: **`http://localhost:8000`**

### Port Summary

| Service                    | Port   |
|----------------------------|--------|
| Cirq-RAG FastAPI backend   | `8000` |
| QCanvas frontend (Vite)    | whatever QCanvas uses (e.g. 5173) |

### Interactive API Docs

Swagger UI is available at:
```
http://localhost:8000/docs
```
You can test every endpoint directly from the browser here. Useful for debugging during integration.

### Required Environment Variables

The backend reads these from `.env` automatically. No extra setup needed — they are already configured in the project:

```env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1

BEDROCK_INFERENCE_PROFILE_ARN_DESIGNER=arn:aws:bedrock:...
BEDROCK_INFERENCE_PROFILE_ARN_OPTIMIZER=arn:aws:bedrock:...
BEDROCK_INFERENCE_PROFILE_ARN_VALIDATOR=arn:aws:bedrock:...
BEDROCK_INFERENCE_PROFILE_ARN_EDUCATIONAL=arn:aws:bedrock:...
```

---

## 4. API Reference

### Base URL
```
http://localhost:8000          # dev
https://<your-alb-domain>      # prod (ECS Fargate behind ALB, idle timeout ≥ 180s)
```

### Authentication

In any environment where `CIRQ_RAG_API_KEY` is set, every call to `/api/v1/*`
**must** include the header:

```
X-API-Key: <the key from Secrets Manager>
```

Missing or wrong keys return `401` with a JSON envelope:

```json
{ "error": { "code": "invalid_api_key", "message": "Missing or invalid X-API-Key header.", "retryable": false } }
```

`GET /health` and `GET /readiness` are always open (used by ALB/ECS health
checks). In development, if `CIRQ_RAG_API_KEY` is unset the dependency becomes
a no-op so existing local workflows keep working.

### Error envelope

Upstream (Bedrock) throttling or timeouts are mapped to HTTP **`503`** with a
`Retry-After: 15` header and the body:

```json
{ "error": { "code": "ThrottlingException", "message": "...", "retryable": true } }
```

The frontend should treat `retryable: true` as a transient failure and surface
a "please retry in a few seconds" message.

---

### `POST /api/v1/generate` — Run the Full Pipeline

This is the **only endpoint you need for core functionality**.

#### Request Body

```json
{
  "description": "Create a 3-qubit Bell state using Hadamard and CNOT gates",
  "algorithm": "bell_state",
  "enable_validator": true,
  "enable_optimizer": true,
  "enable_educational": true,
  "max_optimization_loops": 3
}
```

| Field                    | Type    | Required | Default | Description |
|--------------------------|---------|----------|---------|-------------|
| `description`            | string  | ✅ Yes   | —       | The user's natural language prompt |
| `algorithm`              | string  | ❌ No    | `null`  | Optional hint: `"vqe"`, `"qaoa"`, `"grover"`, `"qft"`, etc. |
| `enable_validator`       | boolean | ❌ No    | `true`  | Whether to run the Validator stage |
| `enable_optimizer`       | boolean | ❌ No    | `true`  | Whether to run the Optimizer stage |
| `enable_educational`     | boolean | ❌ No    | `true`  | Whether to run the Educational Agent |
| `max_optimization_loops` | integer (1–10) | ❌ No | `3` | Max iterations of the optimizer ↔ validator re-validation loop |

> The `educational_depth` parameter can also be sent as a string field. Valid values: `"low"`, `"intermediate"`, `"high"`, `"very_high"`. This controls how detailed and technical the explanation will be (see §7 for what each level produces).

#### Response Body (`200 OK`)

```json
{
  "run_id": "a3f9d1e2-c4a1-4b3f-9e22-ab12cd34ef56",
  "status": "completed",
  "created_at": "2026-04-05T14:11:57Z",
  "prompt": "Create a 3-qubit Bell state...",
  "algorithm": "bell_state",

  "agents": [
    {
      "name": "designer",
      "status": "success",
      "summary": "Initial Cirq code generated from prompt.",
      "code": "import cirq\n...",
      "logs": null,
      "metrics": null
    },
    {
      "name": "validator",
      "status": "warning",
      "summary": "Initial validation of generated code.",
      "code": null,
      "metrics": {
        "validation_passed": false,
        "details": "..."
      }
    },
    {
      "name": "optimizer",
      "status": "success",
      "summary": "Circuit optimization and resource reduction.",
      "code": "import cirq\n... (optimized)",
      "metrics": {
        "gate_count_before": 12,
        "gate_count_after": 8
      }
    },
    {
      "name": "final_validator",
      "status": "success",
      "summary": "Final validation of the optimized circuit.",
      "metrics": {
        "validation_passed": true,
        "details": "..."
      }
    },
    {
      "name": "educational",
      "status": "success",
      "summary": "Educational explanations generated.",
      "metrics": { "has_explanations": true }
    }
  ],

  "final_code": "import cirq\n\nq0, q1 = cirq.LineQubit.range(2)\n...",

  "explanation": {
    "markdown": "## Overview\nThis circuit creates a Bell state...\n\n## Step-by-Step\n...",
    "depth": "intermediate"
  },

  "raw_result": { ... }
}
```

#### Key Response Fields

| Field          | Type   | What to do with it |
|----------------|--------|-------------------|
| `status`       | `"completed"` or `"error"` | Show overall success/failure |
| `agents`       | array  | Use to show which pipeline stages ran and their result |
| `final_code`   | string | The final Cirq Python code to display to the user |
| `explanation.markdown` | string | A full Markdown document explaining the circuit. Render with a Markdown renderer. |
| `explanation.depth` | string | Which depth level was used (`low` / `intermediate` / `high` / `very_high`) |
| `run_id`       | UUID string | Used to fetch this run later via `GET /api/v1/runs/{id}` |

#### Agent Step Object

Each item in the `agents` array:

| Field     | Type   | Description |
|-----------|--------|-------------|
| `name`    | string | One of: `designer`, `validator`, `optimizer`, `final_validator`, `educational` |
| `status`  | string | `"success"`, `"warning"`, `"info"`, or `"error"` |
| `summary` | string | Short human-readable description of what this stage did |
| `code`    | string or null | Code produced by this stage (designer and optimizer produce code) |
| `metrics` | object or null | Stage-specific data (e.g. validation pass/fail, gate counts) |

---

### `GET /api/v1/runs` — List Recent Runs

Returns up to 50 most recent runs, newest first. In-memory only — resets on backend restart.

```json
[
  {
    "run_id": "a3f9d1e2-...",
    "created_at": "2026-04-05T14:11:57Z",
    "prompt_preview": "Create a 3-qubit Bell state...",
    "status": "completed",
    "enable_validator": true,
    "enable_optimizer": true,
    "enable_educational": true
  }
]
```

---

### `GET /api/v1/runs/{run_id}` — Get a Specific Run

Returns the full response object (same schema as `POST /api/v1/generate`) for a given run ID.

```http
GET /api/v1/runs/a3f9d1e2-c4a1-4b3f-9e22-ab12cd34ef56
```

---

## 5. TypeScript Types & API Client

Copy these into QCanvas. Adjust import paths to match QCanvas's directory structure.

### Types

```typescript
// types/cirqAgent.ts

export type AgentName =
  | 'designer'
  | 'validator'
  | 'optimizer'
  | 'final_validator'
  | 'educational';

export type AgentStepStatus = 'success' | 'warning' | 'info' | 'error';

export interface AgentStep {
  name: AgentName;
  status: AgentStepStatus;
  summary?: string;
  code?: string;
  logs?: string;
  metrics?: Record<string, unknown>;
}

export interface Explanation {
  markdown: string;
  depth: 'low' | 'intermediate' | 'high' | 'very_high';
}

export interface GenerateResponse {
  run_id: string;
  status: 'completed' | 'error';
  created_at: string;           // ISO 8601
  prompt: string;
  algorithm?: string | null;
  agents: AgentStep[];
  final_code?: string | null;
  explanation?: Explanation | null;
  raw_result: Record<string, unknown>;
}

export interface RunSummary {
  run_id: string;
  created_at: string;
  prompt_preview: string;
  status: string;
  enable_validator: boolean;
  enable_optimizer: boolean;
  enable_educational: boolean;
}

export type EducationalDepth = 'low' | 'intermediate' | 'high' | 'very_high';

export interface CirqAgentConfig {
  optimizerEnabled: boolean;
  educationalDepth: EducationalDepth;
  maxOptimizationLoops: number;   // 1–10
}
```

### API Client

```typescript
// api/cirqAgent.ts

import type {
  GenerateResponse,
  RunSummary,
  CirqAgentConfig,
} from '../types/cirqAgent';

// In dev: requests go to /cirq-api/... which Vite proxies to http://localhost:8000
// In prod: replace with the deployed backend URL or a different proxy path
const BASE = '/cirq-api';

// The API key should be provided via build-time env and forwarded by your
// backend/proxy in production. Do NOT ship a production key to the browser -
// have QCanvas's own backend attach the header on server-to-server calls.
const API_KEY = (import.meta as any).env?.VITE_CIRQ_API_KEY ?? '';

function authHeaders(): Record<string, string> {
  return API_KEY ? { 'X-API-Key': API_KEY } : {};
}

async function parseJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Cirq API error ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function generateCirqCode(
  description: string,
  config: CirqAgentConfig,
  algorithm?: string,
): Promise<GenerateResponse> {
  const res = await fetch(`${BASE}/api/v1/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({
      description,
      algorithm: algorithm ?? undefined,
      enable_validator: true,                  // always on
      enable_optimizer: config.optimizerEnabled,
      enable_educational: true,                // always on
      educational_depth: config.educationalDepth,
      max_optimization_loops: config.maxOptimizationLoops,
    }),
  });
  return parseJson<GenerateResponse>(res);
}

export async function listCirqRuns(): Promise<RunSummary[]> {
  const res = await fetch(`${BASE}/api/v1/runs`, { headers: authHeaders() });
  return parseJson<RunSummary[]>(res);
}

export async function getCirqRun(runId: string): Promise<GenerateResponse> {
  const res = await fetch(`${BASE}/api/v1/runs/${runId}`, { headers: authHeaders() });
  return parseJson<GenerateResponse>(res);
}
```

---

## 6. Vite Proxy Setup (Dev)

Add this to QCanvas's `vite.config.ts` to forward requests to the Cirq-RAG backend without CORS issues:

```typescript
server: {
  proxy: {
    '/cirq-api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/cirq-api/, ''),
    },
  },
},
```

> Using `/cirq-api` as the prefix (not `/api`) avoids conflicting with QCanvas's own API routes. The rewrite strips the prefix before forwarding, so the backend receives the original `/api/v1/generate` path.

**For production**, either:
- Deploy the backend and set a full URL in the API client, or
- Add CORS middleware to `src/server.py`:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://your-qcanvas-domain.com"],
      allow_methods=["GET", "POST"],
      allow_headers=["*"],
  )
  ```

---

## 7. Frontend Functional Requirements

This section describes **what the frontend must do** — not how to style it or where to put things. All UI decisions belong to QCanvas.

---

### 7.1 Sending a Prompt

- The user types a natural language prompt describing a quantum circuit or algorithm
- On submit, call `POST /api/v1/generate` with the prompt and current config
- The request is **synchronous and slow** (15–60 seconds). The UI must clearly show a loading state for the entire duration
- While loading, the user should not be able to submit another prompt (disable the input)

---

### 7.2 Displaying the Pipeline Stages

The response includes an `agents` array with one entry per pipeline stage that ran. The frontend should display these stages so the user can see what happened.

The pipeline always runs in this order:
1. `designer` — always present
2. `validator` — present if `enable_validator` was true
3. `optimizer` — present if `enable_optimizer` was true
4. `final_validator` — always present
5. `educational` — always present

Each stage has a `status` (`"success"`, `"warning"`, `"info"`, `"error"`) and a `summary` string. Show both.

Since the API is synchronous, the frontend can **simulate a live pipeline view** by revealing stages one by one with a staggered animation after the response arrives, or simply show them all at once — QCanvas can decide.

---

### 7.3 Displaying the Generated Code

The `final_code` field contains the final Python code using the Cirq library. Display it as a code block with:
- Syntax highlighting for Python
- A **copy to clipboard** button
- A **"Load into Canvas"** button — see §9

---

### 7.4 Rendering the Explanation

The `explanation.markdown` field is a full Markdown document generated by the Educational Agent. The frontend must render it properly using a Markdown renderer (e.g. `react-markdown` with `remark-gfm`).

The content changes based on the `educationalDepth` setting:

| Depth          | What the explanation contains |
|----------------|-------------------------------|
| `low`          | Plain language, analogies, no math, suitable for beginners |
| `intermediate` | Explains each gate, defines quantum terms, structured sections |
| `high`         | Mathematical intuition, state vectors, reasoning for each gate choice |
| `very_high`    | Graduate-level: bra-ket notation, full state evolution, noise analysis, hardware considerations |

If rendering at `very_high` depth, consider adding a math rendering plugin (e.g. `remark-math` + `rehype-katex`) since responses may include LaTeX-style formulas.

---

### 7.5 Circuit Metrics

The optimizer and validator stages return metrics the frontend can optionally display:

- **Gate count before/after optimization**: from `agents.find(a => a.name === 'optimizer')?.metrics`
- **Validation result**: from `agents.find(a => a.name === 'final_validator')?.metrics?.validation_passed` (boolean)

These are optional to display but add useful context for the user.

---

### 7.6 Configuration the User Must Be Able to Control

The frontend must expose these settings to the user:

| Setting                  | What it Does | Type | Default |
|--------------------------|--------------|------|---------|
| **Optimizer on/off**     | Enables or disables the Optimizer stage. The Designer and Validator cannot be disabled. | Toggle | On |
| **Educational Depth**    | Controls how detailed the circuit explanation is. 4 options: `low`, `intermediate`, `high`, `very_high`. | Selector | `intermediate` |
| **Max Optimization Loops** | How many times the Optimizer ↔ Validator loop runs before stopping. | Number input (1–10) | 3 |

The **Designer** and **Validator** are always on and should be shown as non-toggleable/locked in the UI.

---

### 7.7 Run History (Optional but Recommended)

The backend keeps the last 50 runs in memory. The frontend can optionally show a history list:
- Fetch from `GET /api/v1/runs`
- Show prompt preview, timestamp, and status for each run
- Clicking a run loads it via `GET /api/v1/runs/{id}` and displays it the same way as a fresh response

**Important caveat to communicate to the user**: history is session-only and is lost when the backend restarts. Show a note somewhere in the history UI.

---

### 7.8 Quick Starter Prompts (Optional)

When the assistant has no messages yet, show a set of pre-written example prompts the user can click to start quickly. Clicking one fills the input and submits it.

Suggested prompts (QCanvas can customise these):
- `"Create a Bell state in Cirq"`
- `"Implement a 3-qubit Quantum Fourier Transform circuit"`
- `"Build a QAOA circuit for the MaxCut problem"`
- `"Generate a VQE ansatz with alternating CNOT layers"`

---

## 8. Error Handling & Edge Cases

| Scenario | What to show |
|----------|--------------|
| Backend not running / unreachable | Clear error: "Could not connect to the Cirq AI backend. Make sure it is running on port 8000." |
| Request takes too long (> 90s) | Timeout error: "The pipeline timed out. Try a simpler prompt or reduce Max Optimization Loops." |
| `status: "error"` in response | Display the error message. Check `raw_result.errors` array for detail. |
| `final_code` is `null` | Show a message like "Code generation failed" without crashing the UI |
| `explanation` is `null` | Don't render the explanation section at all |
| Optimizer disabled (`enable_optimizer: false`) | Don't show the optimizer stage in the pipeline display |
| Network error (fetch throws) | Catch the error and show an inline error message in the conversation |

---

## 9. Context Injection Feature

These two features connect the AI assistant to the QCanvas circuit editor and are the most powerful part of the integration.

### 9.1 "Ask AI about this circuit" (Canvas → Agent)

Add a way for the user to send their **currently open circuit** to the AI assistant as context. When triggered:

1. Export the current circuit to text (Cirq Python, QASM, or any string representation)
2. Construct a prompt like:
   ```
   I have this quantum circuit open in QCanvas:

   import cirq
   q0, q1 = cirq.LineQubit.range(2)
   circuit = cirq.Circuit([cirq.H(q0), cirq.CNOT(q0, q1)])

   Can you explain what it does and suggest any optimizations?
   ```
3. Open the AI panel if it isn't already open
4. Submit the prompt immediately

### 9.2 "Load into Canvas" (Agent → Canvas)

When the AI generates a circuit, provide a button to inject the `final_code` back into QCanvas. When clicked:

1. Parse `final_code` (it is valid Cirq Python)
2. Load it into QCanvas's Cirq code editor / circuit view
3. Trigger re-simulation if applicable
4. Show a brief success notification

---

## 10. Quick Reference

```bash
# Backend startup
cd Cirq-RAG-Code-Assistant
.\venv\Scripts\Activate.ps1
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000

# Test quickly with curl
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Create a Bell state", "enable_optimizer": true}'

# Interactive API explorer
http://localhost:8000/docs
```

---

*Written by Umer Farooq · umerfarooqcs0891@gmail.com — Huawei ICT Competition Project*
