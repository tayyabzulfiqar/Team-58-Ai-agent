'use client'

import { useEffect, useState } from 'react'
import { cn } from '../lib/utils'
import { logs, type LogEntry } from '../lib/mock-data'
import { 
  Info, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle,
  Terminal,
  ChevronDown
} from 'lucide-react'
import { ScrollArea } from '../components/ui/scroll-area'

const typeConfig = {
  info: {
    icon: Info,
    color: 'text-primary',
    bg: 'bg-primary/10',
    border: 'border-primary/20'
  },
  success: {
    icon: CheckCircle2,
    color: 'text-neon-green',
    bg: 'bg-neon-green/10',
    border: 'border-neon-green/20'
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-neon-orange',
    bg: 'bg-neon-orange/10',
    border: 'border-neon-orange/20'
  },
  error: {
    icon: XCircle,
    color: 'text-destructive',
    bg: 'bg-destructive/10',
    border: 'border-destructive/20'
  }
}

function LogEntryComponent({ log, isNew }: { log: LogEntry; isNew: boolean }) {
  const config = typeConfig[log.type]
  const Icon = config.icon

  return (
    <div className={cn(
      "p-3 rounded-lg border transition-all duration-300",
      config.bg,
      config.border,
      isNew && "animate-in slide-in-from-right-5 fade-in-0"
    )}>
      <div className="flex items-start gap-3">
        <div className={cn(
          "w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0",
          config.bg
        )}>
          <Icon className={cn("w-4 h-4", config.color)} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={cn(
              "text-[10px] font-bold uppercase tracking-wider",
              config.color
            )}>
              {log.agent}
            </span>
            <span className="text-[10px] text-muted-foreground font-mono">
              {log.timestamp}
            </span>
          </div>
          <p className="text-xs text-foreground/90 leading-relaxed">
            {log.message}
          </p>
        </div>
      </div>
    </div>
  )
}

export function ActivityFeed() {
  const [displayLogs, setDisplayLogs] = useState(logs)
  const [newLogIds, setNewLogIds] = useState<Set<string>>(new Set())

  // Simulate new logs arriving
  useEffect(() => {
    const interval = setInterval(() => {
      const newLog: LogEntry = {
        id: `log-${Date.now()}`,
        timestamp: new Date().toLocaleTimeString('en-US', { 
          hour12: false, 
          hour: '2-digit', 
          minute: '2-digit', 
          second: '2-digit' 
        }),
        agent: ['Research', 'Processing', 'Intelligence', 'Campaign', 'Decision'][Math.floor(Math.random() * 5)],
        type: ['info', 'success', 'warning'][Math.floor(Math.random() * 3)] as LogEntry['type'],
        message: [
          'Processing batch completed successfully',
          'New signals detected in market data',
          'Campaign engagement metrics updated',
          'Intelligence report generated',
          'Resource optimization in progress',
          'Data pipeline throughput optimized',
          'Anomaly detection scan completed',
          'API response latency within SLA'
        ][Math.floor(Math.random() * 8)]
      }

      setNewLogIds(prev => new Set([...prev, newLog.id]))
      setDisplayLogs(prev => [newLog, ...prev.slice(0, 19)])

      // Remove from new logs after animation
      setTimeout(() => {
        setNewLogIds(prev => {
          const next = new Set(prev)
          next.delete(newLog.id)
          return next
        })
      }, 500)
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  return (
    <aside className="w-80 h-screen glass-panel border-l border-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-primary" />
            <h2 className="font-bold text-sm text-foreground uppercase tracking-wider">
              Live Activity
            </h2>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-neon-green animate-pulse" />
            <span className="text-[10px] text-neon-green font-mono">LIVE</span>
          </div>
        </div>
      </div>

      {/* Logs */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {displayLogs.map((log) => (
            <LogEntryComponent 
              key={log.id} 
              log={log} 
              isNew={newLogIds.has(log.id)}
            />
          ))}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <button className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors">
          <span className="text-xs text-muted-foreground">View All Logs</span>
          <ChevronDown className="w-3 h-3 text-muted-foreground" />
        </button>
      </div>

      {/* Stats bar */}
      <div className="p-4 border-t border-border">
        <div className="grid grid-cols-3 gap-2">
          <div className="text-center">
            <p className="text-lg font-bold text-foreground font-mono">247</p>
            <p className="text-[10px] text-muted-foreground uppercase">Events/min</p>
          </div>
          <div className="text-center">
            <p className="text-lg font-bold text-neon-green font-mono">98%</p>
            <p className="text-[10px] text-muted-foreground uppercase">Success</p>
          </div>
          <div className="text-center">
            <p className="text-lg font-bold text-foreground font-mono">12ms</p>
            <p className="text-[10px] text-muted-foreground uppercase">Latency</p>
          </div>
        </div>
      </div>
    </aside>
  )
}

