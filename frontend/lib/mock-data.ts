export type AgentStatus = 'active' | 'processing' | 'idle'

export interface Agent {
  id: string
  name: string
  shortName: string
  status: AgentStatus
  currentTask: string
  confidence: number
  processedItems: number
  successRate: number
  lastActive: string
  description: string
  capabilities: string[]
  metrics: {
    throughput: number
    latency: number
    accuracy: number
  }
}

export interface Opportunity {
  id: string
  name: string
  value: number
  confidence: number
  source: string
  status: 'new' | 'qualified' | 'engaged' | 'closed'
  discoveredAt: string
}

export interface Campaign {
  id: string
  name: string
  status: 'active' | 'paused' | 'completed' | 'scheduled'
  reach: number
  engagement: number
  conversions: number
  startDate: string
  agent: string
}

export interface LogEntry {
  id: string
  timestamp: string
  agent: string
  type: 'info' | 'success' | 'warning' | 'error'
  message: string
}

export const agents: Agent[] = [
  {
    id: 'research',
    name: 'Research Agent',
    shortName: 'RESEARCH',
    status: 'active',
    currentTask: 'Scanning market signals from 47 data sources',
    confidence: 94,
    processedItems: 12847,
    successRate: 98.7,
    lastActive: '2 seconds ago',
    description: 'Autonomous market intelligence gathering and signal detection',
    capabilities: ['Web Scraping', 'API Integration', 'NLP Analysis', 'Pattern Recognition'],
    metrics: {
      throughput: 1250,
      latency: 45,
      accuracy: 97.8
    }
  },
  {
    id: 'processing',
    name: 'Processing Agent',
    shortName: 'PROCESS',
    status: 'processing',
    currentTask: 'Normalizing dataset batch #4521',
    confidence: 89,
    processedItems: 8934,
    successRate: 99.2,
    lastActive: 'just now',
    description: 'Data transformation, cleaning, and enrichment pipeline',
    capabilities: ['Data Cleaning', 'Entity Extraction', 'Deduplication', 'Schema Mapping'],
    metrics: {
      throughput: 3400,
      latency: 12,
      accuracy: 99.1
    }
  },
  {
    id: 'intelligence',
    name: 'Intelligence Agent',
    shortName: 'INTEL',
    status: 'active',
    currentTask: 'Generating insights from competitor analysis',
    confidence: 91,
    processedItems: 5621,
    successRate: 96.4,
    lastActive: '5 seconds ago',
    description: 'Advanced analytics and predictive intelligence generation',
    capabilities: ['Predictive Analytics', 'Trend Analysis', 'Risk Assessment', 'Opportunity Scoring'],
    metrics: {
      throughput: 890,
      latency: 78,
      accuracy: 94.5
    }
  },
  {
    id: 'decision',
    name: 'Decision Agent',
    shortName: 'DECIDE',
    status: 'idle',
    currentTask: 'Awaiting new intelligence reports',
    confidence: 96,
    processedItems: 3287,
    successRate: 97.8,
    lastActive: '12 seconds ago',
    description: 'Autonomous decision-making and strategy optimization',
    capabilities: ['Strategy Generation', 'Resource Allocation', 'Priority Ranking', 'Approval Workflows'],
    metrics: {
      throughput: 450,
      latency: 156,
      accuracy: 96.2
    }
  },
  {
    id: 'campaign',
    name: 'Campaign Agent',
    shortName: 'CAMPAIGN',
    status: 'active',
    currentTask: 'Executing outreach sequence #782',
    confidence: 88,
    processedItems: 15234,
    successRate: 94.5,
    lastActive: '1 second ago',
    description: 'Multi-channel campaign execution and optimization',
    capabilities: ['Email Automation', 'Social Outreach', 'A/B Testing', 'Performance Tracking'],
    metrics: {
      throughput: 2100,
      latency: 23,
      accuracy: 93.8
    }
  }
]

export const opportunities: Opportunity[] = [
  {
    id: 'opp-001',
    name: 'Enterprise SaaS Deal - TechCorp',
    value: 285000,
    confidence: 94,
    source: 'LinkedIn Signal',
    status: 'qualified',
    discoveredAt: '2 hours ago'
  },
  {
    id: 'opp-002',
    name: 'Mid-Market Expansion - DataFlow Inc',
    value: 127500,
    confidence: 87,
    source: 'Intent Data',
    status: 'engaged',
    discoveredAt: '4 hours ago'
  },
  {
    id: 'opp-003',
    name: 'Strategic Partnership - CloudNine',
    value: 450000,
    confidence: 72,
    source: 'News Analysis',
    status: 'new',
    discoveredAt: '6 hours ago'
  },
  {
    id: 'opp-004',
    name: 'Upsell Opportunity - Existing Client',
    value: 89000,
    confidence: 91,
    source: 'Usage Analytics',
    status: 'qualified',
    discoveredAt: '8 hours ago'
  },
  {
    id: 'opp-005',
    name: 'Government Contract - FedTech',
    value: 780000,
    confidence: 65,
    source: 'RFP Monitor',
    status: 'new',
    discoveredAt: '12 hours ago'
  }
]

export const campaigns: Campaign[] = [
  {
    id: 'camp-001',
    name: 'Q1 Enterprise Outreach',
    status: 'active',
    reach: 12450,
    engagement: 8.7,
    conversions: 234,
    startDate: '2024-01-15',
    agent: 'Campaign Agent'
  },
  {
    id: 'camp-002',
    name: 'Product Launch - AI Suite',
    status: 'active',
    reach: 45670,
    engagement: 12.3,
    conversions: 567,
    startDate: '2024-02-01',
    agent: 'Campaign Agent'
  },
  {
    id: 'camp-003',
    name: 'Re-engagement Campaign',
    status: 'paused',
    reach: 8900,
    engagement: 6.2,
    conversions: 89,
    startDate: '2024-01-20',
    agent: 'Campaign Agent'
  },
  {
    id: 'camp-004',
    name: 'Partner Referral Program',
    status: 'completed',
    reach: 3200,
    engagement: 15.8,
    conversions: 145,
    startDate: '2023-12-01',
    agent: 'Campaign Agent'
  },
  {
    id: 'camp-005',
    name: 'Industry Event Follow-up',
    status: 'scheduled',
    reach: 0,
    engagement: 0,
    conversions: 0,
    startDate: '2024-03-15',
    agent: 'Campaign Agent'
  }
]

export const logs: LogEntry[] = [
  {
    id: 'log-001',
    timestamp: '14:32:45',
    agent: 'Research',
    type: 'success',
    message: 'Discovered 23 new high-intent signals from LinkedIn'
  },
  {
    id: 'log-002',
    timestamp: '14:32:42',
    agent: 'Processing',
    type: 'info',
    message: 'Batch #4521 processing: 847/1200 records complete'
  },
  {
    id: 'log-003',
    timestamp: '14:32:38',
    agent: 'Intelligence',
    type: 'success',
    message: 'Generated 5 actionable insights from competitor data'
  },
  {
    id: 'log-004',
    timestamp: '14:32:35',
    agent: 'Campaign',
    type: 'info',
    message: 'Sequence #782: 156 emails delivered, 34 opened'
  },
  {
    id: 'log-005',
    timestamp: '14:32:30',
    agent: 'Decision',
    type: 'warning',
    message: 'Resource allocation review recommended for Q2 planning'
  },
  {
    id: 'log-006',
    timestamp: '14:32:25',
    agent: 'Research',
    type: 'info',
    message: 'API rate limit approaching on source: Clearbit (87%)'
  },
  {
    id: 'log-007',
    timestamp: '14:32:20',
    agent: 'Processing',
    type: 'success',
    message: 'Data quality score improved to 98.7% (+0.3%)'
  },
  {
    id: 'log-008',
    timestamp: '14:32:15',
    agent: 'Intelligence',
    type: 'info',
    message: 'Market sentiment analysis: Bullish trend detected'
  },
  {
    id: 'log-009',
    timestamp: '14:32:10',
    agent: 'Campaign',
    type: 'success',
    message: 'A/B test concluded: Variant B +23% conversion rate'
  },
  {
    id: 'log-010',
    timestamp: '14:32:05',
    agent: 'Decision',
    type: 'info',
    message: 'Strategy #47 approved for automatic execution'
  }
]

export const systemMetrics = {
  totalOpportunities: 1247,
  activeCapaigns: 12,
  pipelineValue: 4250000,
  conversionRate: 8.7,
  systemHealth: 99.2,
  dataProcessed: '2.4TB',
  uptime: '99.97%',
  activeConnections: 47
}
