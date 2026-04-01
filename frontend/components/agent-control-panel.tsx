'use client'

import { cn } from '@/lib/utils'
import { 
  Play, 
  Pause, 
  RefreshCw, 
  Clock,
  Activity,
  Shield,
  Zap,
  Target
} from 'lucide-react'

interface AgentControlPanelProps {
  onRunSystem: () => void
  onPause: () => void
  isPaused: boolean
  isLoading: boolean
  lastUpdated: Date | null
}

export function AgentControlPanel({ 
  onRunSystem, 
  onPause, 
  isPaused, 
  isLoading,
  lastUpdated 
}: AgentControlPanelProps) {
  const formatTime = (date: Date | null) => {
    if (!date) return 'Never'
    const now = new Date()
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
    if (diff < 60) return `${diff}s ago`
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    return `${Math.floor(diff / 3600)}h ago`
  }

  return (
    <div className="glass-panel-elevated rounded-xl p-4 border border-border/30">
      <div className="flex items-center justify-between">
        {/* Left: Agent Status */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-neon-green/10 flex items-center justify-center">
              <Shield className="w-5 h-5 text-neon-green" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wide">System Status</p>
              <p className="text-sm font-semibold text-foreground">
                {isPaused ? 'Paused' : isLoading ? 'Processing...' : 'Active'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <div className="w-1 h-1 rounded-full bg-neon-green" />
            <span>Data Agent</span>
            <div className="w-1 h-1 rounded-full bg-neon-cyan" />
            <span>Processing</span>
            <div className="w-1 h-1 rounded-full bg-neon-orange" />
            <span>Intelligence</span>
            <div className="w-1 h-1 rounded-full bg-primary" />
            <span>Decision</span>
          </div>
        </div>

        {/* Right: Controls */}
        <div className="flex items-center gap-3">
          {/* Last Updated */}
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-secondary/30">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">
              Updated: {formatTime(lastUpdated)}
            </span>
          </div>

          {/* Pause Button */}
          <button
            onClick={onPause}
            disabled={isLoading}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300",
              isPaused 
                ? "bg-neon-orange/10 text-neon-orange hover:bg-neon-orange/20" 
                : "bg-secondary/50 text-foreground hover:bg-secondary",
              isLoading && "opacity-50 cursor-not-allowed"
            )}
          >
            {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
            {isPaused ? 'Resume' : 'Pause'}
          </button>

          {/* Run System Button */}
          <button
            onClick={onRunSystem}
            disabled={isLoading || isPaused}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300",
              "bg-primary text-primary-foreground hover:bg-primary/90",
              "shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30",
              (isLoading || isPaused) && "opacity-50 cursor-not-allowed"
            )}
          >
            {isLoading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Zap className="w-4 h-4" />
            )}
            {isLoading ? 'Running...' : 'Run System'}
          </button>
        </div>
      </div>
    </div>
  )
}
