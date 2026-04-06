'use client'

import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'
import { 
  Terminal, 
  Brain, 
  Cpu, 
  Target, 
  Activity,
  Zap,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  TrendingUp,
  Database,
  Search,
  Signal
} from 'lucide-react'

interface Opportunity {
  id: number
  name: string
  company: string
  score: number
  status: string
  revenue_potential: number
  industry: string
  location: string
}

interface IntelligenceFeedProps {
  opportunities?: Opportunity[]
  isPaused?: boolean
}

interface FeedItem {
  id: string
  icon: React.ElementType
  iconColor: string
  message: string
  detail?: string
  timestamp: Date
  type: 'info' | 'success' | 'warning' | 'processing'
}

const agentMessages = [
  { icon: Search, color: 'text-neon-cyan', msg: 'Analyzing {count} data points...', type: 'processing' as const },
  { icon: Brain, color: 'text-neon-orange', msg: 'Opportunity detected (confidence: {score}%)', type: 'success' as const },
  { icon: Target, color: 'text-primary', msg: 'Decision executed: {status}', type: 'info' as const },
  { icon: Cpu, color: 'text-neon-cyan', msg: 'Recalculating priority scores...', type: 'processing' as const },
  { icon: Database, color: 'text-neon-green', msg: 'Processing batch #{id}...', type: 'processing' as const },
  { icon: Activity, color: 'text-neon-orange', msg: 'Risk assessment updated', type: 'warning' as const },
  { icon: Zap, color: 'text-neon-green', msg: 'High-value lead identified', type: 'success' as const },
  { icon: Sparkles, color: 'text-primary', msg: 'Pattern recognized in {industry}', type: 'info' as const },
  { icon: TrendingUp, color: 'text-neon-green', msg: 'Revenue potential: ${value}', type: 'success' as const },
  { icon: Signal, color: 'text-neon-cyan', msg: 'Signal strength: {score}%', type: 'processing' as const },
  { icon: AlertCircle, color: 'text-neon-orange', msg: 'Anomaly detected in {company}', type: 'warning' as const },
  { icon: CheckCircle2, color: 'text-neon-green', msg: 'Verification complete for {name}', type: 'success' as const },
]

export function IntelligenceFeed({ opportunities = [], isPaused = false }: IntelligenceFeedProps) {
  const [feedItems, setFeedItems] = useState<FeedItem[]>([])
  const [isExpanded, setIsExpanded] = useState(true)

  // Generate initial feed items
  useEffect(() => {
    const initialItems: FeedItem[] = [
      {
        id: '1',
        icon: Brain,
        iconColor: 'text-neon-green',
        message: 'AI pipeline initialized',
        detail: '4 agents active',
        timestamp: new Date(),
        type: 'success'
      },
      {
        id: '2',
        icon: Database,
        iconColor: 'text-neon-cyan',
        message: 'Data ingestion complete',
        detail: `${opportunities.length || 4} records processed`,
        timestamp: new Date(Date.now() - 3000),
        type: 'processing'
      },
      {
        id: '3',
        icon: Target,
        iconColor: 'text-primary',
        message: 'Multi-agent analysis running',
        detail: 'Real-time processing',
        timestamp: new Date(Date.now() - 6000),
        type: 'info'
      }
    ]
    setFeedItems(initialItems)
  }, [opportunities.length])

  // Add new feed items periodically
  useEffect(() => {
    if (isPaused) return

    const interval = setInterval(() => {
      const randomMsg = agentMessages[Math.floor(Math.random() * agentMessages.length)]
      const opportunity = opportunities[Math.floor(Math.random() * opportunities.length)] || {
        id: Math.floor(Math.random() * 1000),
        score: Math.floor(Math.random() * 30) + 70,
        company: 'Target Corp',
        industry: 'Technology',
        name: 'Lead #' + Math.floor(Math.random() * 100),
        revenue_potential: Math.floor(Math.random() * 50000) + 25000
      }

      const newItem: FeedItem = {
        id: Date.now().toString(),
        icon: randomMsg.icon,
        iconColor: randomMsg.color,
        message: randomMsg.msg
          .replace('{count}', (Math.floor(Math.random() * 2000) + 500).toLocaleString())
          .replace('{score}', opportunity.score.toString())
          .replace('{status}', opportunity.score > 80 ? 'High-value lead' : 'Standard lead')
          .replace('{id}', opportunity.id.toString())
          .replace('{industry}', opportunity.industry)
          .replace('{company}', opportunity.company)
          .replace('{name}', opportunity.name)
          .replace('{value}', opportunity.revenue_potential.toLocaleString()),
        timestamp: new Date(),
        type: randomMsg.type
      }

      setFeedItems(prev => [newItem, ...prev].slice(0, 20))
    }, 2500)

    return () => clearInterval(interval)
  }, [opportunities, isPaused])

  const getTypeStyles = (type: FeedItem['type']) => {
    switch (type) {
      case 'success':
        return 'border-l-2 border-neon-green/50 bg-neon-green/5'
      case 'warning':
        return 'border-l-2 border-neon-orange/50 bg-neon-orange/5'
      case 'processing':
        return 'border-l-2 border-neon-cyan/50 bg-neon-cyan/5'
      default:
        return 'border-l-2 border-primary/50 bg-primary/5'
    }
  }

  return (
    <div className="glass-panel-elevated rounded-xl overflow-hidden flex flex-col h-full max-h-[800px]">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/20 bg-secondary/20">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-neon-cyan" />
          <h3 className="font-semibold text-foreground text-sm">Intelligence Feed</h3>
        </div>
        <div className="flex items-center gap-2">
          {!isPaused && (
            <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
          )}
          <button 
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            {isExpanded ? 'Collapse' : 'Expand'}
          </button>
        </div>
      </div>

      {/* Feed Items */}
      {isExpanded && (
        <div className="flex-1 overflow-y-auto p-2 space-y-1 max-h-[600px]">
          {feedItems.map((item, index) => {
            const Icon = item.icon
            const timeDiff = Math.floor((Date.now() - item.timestamp.getTime()) / 1000)
            const timeAgo = timeDiff < 60 ? `${timeDiff}s ago` : `${Math.floor(timeDiff / 60)}m ago`
            
            return (
              <div 
                key={item.id}
                className={cn(
                  "flex items-start gap-2 p-2 rounded-lg transition-all duration-300",
                  "hover:bg-secondary/30 cursor-pointer group",
                  getTypeStyles(item.type),
                  index === 0 && "animate-fade-in"
                )}
              >
                <div className={cn(
                  "w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0",
                  "bg-secondary/50 group-hover:bg-secondary transition-colors"
                )}>
                  <Icon className={cn("w-3.5 h-3.5", item.iconColor)} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-foreground leading-tight">
                    {item.message}
                  </p>
                  {item.detail && (
                    <p className="text-[10px] text-muted-foreground mt-0.5">
                      {item.detail}
                    </p>
                  )}
                  <p className="text-[9px] text-muted-foreground/60 mt-1">
                    {timeAgo}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Footer Stats */}
      {isExpanded && (
        <div className="px-4 py-2 border-t border-border/20 bg-secondary/10">
          <div className="flex items-center justify-between text-[10px] text-muted-foreground">
            <span>Updates: Real-time</span>
            <span>{feedItems.length} events</span>
          </div>
        </div>
      )}
    </div>
  )
}

