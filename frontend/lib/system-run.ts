export type AgentStatus = 'active' | 'processing' | 'idle' | 'error'

export type FeedEntryType = 'info' | 'success' | 'warning' | 'processing'

export type Campaign = {
  strategy?: string
  headline?: string
  hook?: string
  cta?: string
}

export type DecisionMeta = {
  selected_strategy?: string
  alternatives?: string[]
  reason?: string
  confidence?: number
  status?: string
}

export type AgentSnapshot = {
  id: string
  name: string
  shortName: string
  status: AgentStatus
  currentTask: string
  confidence?: number
}

export type FeedEntry = {
  id: string
  agent: string
  type: FeedEntryType
  message: string
  detail?: string | null
  timestamp: string
}

export type SystemRunData = {
  input?: string
  objective?: string
  insight?: string
  summary?: string
  best_campaign?: Campaign
  all_campaigns?: Campaign[]
  optimization_score?: number
  decision_meta?: DecisionMeta
  agent_states?: AgentSnapshot[]
  feed?: FeedEntry[]
  simulated?: boolean
  error?: string | null
}

export type RunSystemResponse = {
  status?: string
  message?: string
  data?: SystemRunData | null
}

export const defaultAgentStates: AgentSnapshot[] = [
  {
    id: 'research',
    name: 'Research Agent',
    shortName: 'RESEARCH',
    status: 'idle',
    currentTask: 'Waiting for the next business input',
    confidence: 0,
  },
  {
    id: 'processing',
    name: 'Data Agent',
    shortName: 'DATA',
    status: 'idle',
    currentTask: 'Standing by for structured signal processing',
    confidence: 0,
  },
  {
    id: 'intelligence',
    name: 'Intelligence Agent',
    shortName: 'INTEL',
    status: 'idle',
    currentTask: 'Ready to score strategic opportunities',
    confidence: 0,
  },
  {
    id: 'decision',
    name: 'Decision Agent',
    shortName: 'DECIDE',
    status: 'idle',
    currentTask: 'Awaiting the next recommendation cycle',
    confidence: 0,
  },
  {
    id: 'campaign',
    name: 'Campaign Agent',
    shortName: 'CAMPAIGN',
    status: 'idle',
    currentTask: 'Prepared to generate the next launch plan',
    confidence: 0,
  },
]

export const defaultFeed: FeedEntry[] = [
  {
    id: 'feed-awaiting',
    agent: 'Team 58 AI System',
    type: 'info',
    message: 'System ready. Submit a business input to run the live pipeline.',
    detail: 'The dashboard will replace placeholder intelligence with the next backend response.',
    timestamp: new Date(0).toISOString(),
  },
]
