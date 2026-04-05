import { getApiBase } from '@/lib/api'
import type {
  CirqAgentClientConfig,
  CirqRunSummary,
  GenerateCirqResponse,
} from '@/types/cirqAgent'

/** Client-side ceiling; aligns with guide §8 (~90s). */
export const CIRQ_GENERATE_TIMEOUT_MS = 95_000

async function getCirqFetchBase(): Promise<string> {
  if (
    typeof window !== 'undefined' &&
    process.env.NEXT_PUBLIC_CIRQ_USE_NEXT_REWRITE === 'true'
  ) {
    return '/cirq-api'
  }
  const api = await getApiBase()
  return `${api}/api/cirq-agent`
}

function buildCirqUrl(base: string, path: string): string {
  const p = path.startsWith('/') ? path : `/${path}`
  if (base.startsWith('http')) {
    return `${base.replace(/\/$/, '')}${p}`
  }
  return `${base}${p}`
}

function formatCirqError(status: number, text: string): string {
  try {
    const j = JSON.parse(text) as { detail?: unknown }
    if (typeof j.detail === 'string') return j.detail
    if (Array.isArray(j.detail)) return JSON.stringify(j.detail)
  } catch {
    /* ignore */
  }
  if (status === 503 || status === 504) {
    return (
      text ||
      (status === 504
        ? 'The Cirq AI pipeline timed out. Try a simpler prompt or reduce max optimization loops.'
        : 'Could not connect to the Cirq AI backend. Ensure the service is running and the proxy is configured.')
    )
  }
  return text || `Cirq API error ${status}`
}

async function parseCirqJson<T>(res: Response): Promise<T> {
  const text = await res.text()
  if (!res.ok) {
    throw new Error(formatCirqError(res.status, text))
  }
  try {
    return JSON.parse(text) as T
  } catch {
    throw new Error(text || 'Invalid JSON from Cirq API')
  }
}

function withTimeout(signal?: AbortSignal): AbortSignal {
  const ctrl = new AbortController()
  const t = setTimeout(() => ctrl.abort(), CIRQ_GENERATE_TIMEOUT_MS)
  const onAbort = () => ctrl.abort()
  if (signal) {
    if (signal.aborted) {
      clearTimeout(t)
      ctrl.abort()
      return ctrl.signal
    }
    signal.addEventListener('abort', onAbort, { once: true })
  }
  ctrl.signal.addEventListener(
    'abort',
    () => {
      clearTimeout(t)
      signal?.removeEventListener('abort', onAbort)
    },
    { once: true },
  )
  return ctrl.signal
}

export async function generateCirqCode(
  description: string,
  config: CirqAgentClientConfig,
  algorithm?: string,
  signal?: AbortSignal,
): Promise<GenerateCirqResponse> {
  const base = await getCirqFetchBase()
  const url = buildCirqUrl(base, '/api/v1/generate')

  const combined = withTimeout(signal)
  let res: Response
  try {
    res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        description,
        algorithm: algorithm || undefined,
        enable_validator: true,
        enable_optimizer: config.optimizerEnabled,
        enable_educational: true,
        educational_depth: config.educationalDepth,
        max_optimization_loops: config.maxOptimizationLoops,
      }),
      signal: combined,
    })
  } catch (e) {
    if (e instanceof Error && e.name === 'AbortError') {
      throw new Error(
        'The pipeline timed out or was cancelled. Try a simpler prompt or reduce max optimization loops.',
      )
    }
    if (e instanceof TypeError) {
      throw new Error(
        'Could not connect to the Cirq AI backend. Ensure QCanvas API is running and CIRQ_AGENT_URL points to the Cirq service (e.g. port 8001).',
      )
    }
    throw e
  }

  return parseCirqJson<GenerateCirqResponse>(res)
}

export async function listCirqRuns(signal?: AbortSignal): Promise<CirqRunSummary[]> {
  const base = await getCirqFetchBase()
  const url = buildCirqUrl(base, '/api/v1/runs')

  const res = await fetch(url, { method: 'GET', signal })
  return parseCirqJson<CirqRunSummary[]>(res)
}

export async function getCirqRun(
  runId: string,
  signal?: AbortSignal,
): Promise<GenerateCirqResponse> {
  const base = await getCirqFetchBase()
  const url = buildCirqUrl(
    base,
    `/api/v1/runs/${encodeURIComponent(runId)}`,
  )

  const res = await fetch(url, { method: 'GET', signal })
  return parseCirqJson<GenerateCirqResponse>(res)
}
