export type CirqAgentName =
  | 'designer'
  | 'validator'
  | 'optimizer'
  | 'final_validator'
  | 'educational'

export type AgentStepStatus = 'success' | 'warning' | 'info' | 'error'

export interface CirqAgentStep {
  name: CirqAgentName | string
  status: AgentStepStatus | string
  summary?: string
  code?: string | null
  logs?: string | null
  metrics?: Record<string, unknown> | null
}

export interface CirqExplanation {
  markdown?: string
  depth?: 'low' | 'intermediate' | 'high' | 'very_high' | string
  [key: string]: unknown
}

export interface GenerateCirqResponse {
  run_id: string
  status: 'completed' | 'error' | string
  created_at: string
  prompt: string
  algorithm?: string | null
  agents: CirqAgentStep[]
  final_code?: string | null
  explanation?: CirqExplanation | null
  raw_result: Record<string, unknown>
}

export interface CirqRunSummary {
  run_id: string
  created_at: string
  prompt_preview: string
  status: string
  enable_validator: boolean
  enable_optimizer: boolean
  enable_educational: boolean
}

export type EducationalDepth = 'low' | 'intermediate' | 'high' | 'very_high'

export interface CirqAgentClientConfig {
  optimizerEnabled: boolean
  educationalDepth: EducationalDepth
  maxOptimizationLoops: number
}
