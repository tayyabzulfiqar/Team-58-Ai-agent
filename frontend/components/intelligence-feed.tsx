'use client'

import { type ElementType, useState } from 'react'
import { cn } from '@/lib/utils'
import { useSystemRun } from './system-run-provider'
import type { FeedEntryType } from '@/lib/system-run'
import {
  Terminal,
  Target,
  AlertCircle,
  CheckCircle2,
  Cpu,
} from 'lucide-react'

const typeConfig: Record<
  FeedEntryType,
  { icon: ElementType; iconColor: string }
> = {
  info: {
    icon: Target,
    iconColor: 'text-primary',
  },
  success: {
    icon: CheckCircle2,
    iconColor: 'text-neon-green',
  },
  warning: {
    icon: AlertCircle,
    iconColor: 'text-neon-orange',
  },
  processing: {
    icon: Cpu,
    iconColor: 'text-neon-cyan',
  },
}

export function IntelligenceFeed() {
  const { feedItems } = useSystemRun()
  const [isExpanded, setIsExpanded] = useState(true)

  const getTypeStyles = (type: FeedEntryType) => {
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
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/20 bg-secondary/20">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-neon-cyan" />
          <h3 className="font-semibold text-foreground text-sm">Intelligence Feed</h3>
        </div>
        <div className="flex items-center gap-2">
          {feedItems.length > 0 && (
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

      {isExpanded && (
        <div className="flex-1 overflow-y-auto p-2 space-y-1 max-h-[600px]">
          {feedItems.map((item, index) => {
            const config = typeConfig[item.type]
            const Icon = config.icon
            const timestamp = new Date(item.timestamp)
            const timeDiff = Math.max(0, Math.floor((Date.now() - timestamp.getTime()) / 1000))
            const timeAgo = timeDiff < 60 ? `${timeDiff}s ago` : `${Math.floor(timeDiff / 60)}m ago`

            return (
              <div
                key={item.id}
                className={cn(
                  'flex items-start gap-2 p-2 rounded-lg transition-all duration-300',
                  'hover:bg-secondary/30 cursor-pointer group',
                  getTypeStyles(item.type),
                  index === 0 && 'animate-fade-in'
                )}
              >
                <div
                  className={cn(
                    'w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0',
                    'bg-secondary/50 group-hover:bg-secondary transition-colors'
                  )}
                >
                  <Icon className={cn('w-3.5 h-3.5', config.iconColor)} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-foreground leading-tight">{item.message}</p>
                  {item.detail && (
                    <p className="text-[10px] text-muted-foreground mt-0.5">{item.detail}</p>
                  )}
                  <p className="text-[9px] text-muted-foreground/60 mt-1">{timeAgo}</p>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {isExpanded && (
        <div className="px-4 py-2 border-t border-border/20 bg-secondary/10">
          <div className="flex items-center justify-between text-[10px] text-muted-foreground">
            <span>Updates: Backend-driven</span>
            <span>{feedItems.length} events</span>
          </div>
        </div>
      )}
    </div>
  )
}
