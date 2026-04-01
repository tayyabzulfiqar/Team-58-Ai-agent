'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { agents } from '@/lib/mock-data'
import { 
  ArrowLeft,
  Activity,
  Zap,
  Clock,
  Target,
  TrendingUp,
  BarChart3,
  Play,
  Pause,
  RefreshCw,
  Settings
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'

const statusConfig = {
  active: {
    label: 'ACTIVE',
    color: 'text-neon-green',
    bg: 'bg-neon-green/20',
    border: 'border-neon-green/30',
    glow: 'neon-glow-green'
  },
  processing: {
    label: 'PROCESSING',
    color: 'text-neon-cyan',
    bg: 'bg-neon-cyan/20',
    border: 'border-neon-cyan/30',
    glow: 'neon-glow-cyan'
  },
  idle: {
    label: 'IDLE',
    color: 'text-muted-foreground',
    bg: 'bg-muted',
    border: 'border-muted',
    glow: ''
  }
}

function MetricBox({ 
  label, 
  value, 
  suffix = '', 
  icon: Icon, 
  trend 
}: { 
  label: string
  value: string | number
  suffix?: string
  icon: React.ComponentType<{ className?: string }>
  trend?: string
}) {
  return (
    <div className="glass-panel rounded-xl border border-border p-4">
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
          <Icon className="w-5 h-5 text-primary" />
        </div>
        {trend && (
          <div className="flex items-center gap-1">
            <TrendingUp className="w-3 h-3 text-neon-green" />
            <span className="text-xs text-neon-green font-mono">{trend}</span>
          </div>
        )}
      </div>
      <p className="text-2xl font-bold text-foreground font-mono">
        {value}{suffix}
      </p>
      <p className="text-xs text-muted-foreground uppercase tracking-wider mt-1">
        {label}
      </p>
    </div>
  )
}

function CapabilityChip({ capability }: { capability: string }) {
  return (
    <div className="px-3 py-1.5 rounded-lg bg-secondary border border-border text-xs font-medium text-foreground">
      {capability}
    </div>
  )
}

export default function AgentDetailPage() {
  const params = useParams()
  const agent = agents.find(a => a.id === params.id)

  if (!agent) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">Agent not found</p>
      </div>
    )
  }

  const status = statusConfig[agent.status]

  return (
    <div className="p-8 space-y-8">
      {/* Back navigation */}
      <Link 
        href="/"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Command Center
      </Link>

      {/* Header */}
      <header className="flex items-start justify-between">
        <div className="flex items-start gap-6">
          {/* Agent icon */}
          <div className={cn(
            "w-20 h-20 rounded-2xl flex items-center justify-center",
            status.bg,
            status.border,
            status.glow,
            "border"
          )}>
            <Activity className={cn("w-10 h-10", status.color)} />
          </div>

          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-foreground">
                {agent.name}
              </h1>
              <Badge 
                variant="outline" 
                className={cn(
                  "text-xs font-bold",
                  status.bg,
                  status.color,
                  status.border
                )}
              >
                <span className={cn(
                  "w-1.5 h-1.5 rounded-full mr-1.5",
                  agent.status === 'active' && "bg-neon-green animate-pulse",
                  agent.status === 'processing' && "bg-neon-cyan animate-pulse",
                  agent.status === 'idle' && "bg-muted-foreground"
                )} />
                {status.label}
              </Badge>
            </div>
            <p className="text-muted-foreground max-w-md">
              {agent.description}
            </p>
            <p className="text-xs text-muted-foreground mt-2 font-mono">
              Last active: {agent.lastActive}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-2">
            <RefreshCw className="w-4 h-4" />
            Restart
          </Button>
          <Button variant="outline" size="sm" className="gap-2">
            {agent.status === 'active' || agent.status === 'processing' ? (
              <>
                <Pause className="w-4 h-4" />
                Pause
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Start
              </>
            )}
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </header>

      {/* Current Task */}
      <div className={cn(
        "glass-panel rounded-xl border p-6",
        status.border
      )}>
        <div className="flex items-center gap-2 mb-3">
          <div className={cn(
            "w-2 h-2 rounded-full",
            agent.status !== 'idle' ? "animate-pulse" : "",
            agent.status === 'active' && "bg-neon-green",
            agent.status === 'processing' && "bg-neon-cyan",
            agent.status === 'idle' && "bg-muted-foreground"
          )} />
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Current Task
          </span>
        </div>
        <p className="text-lg font-medium text-foreground font-mono">
          {agent.currentTask}
        </p>
        {agent.status !== 'idle' && (
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-muted-foreground">Progress</span>
              <span className="text-xs text-foreground font-mono">67%</span>
            </div>
            <Progress value={67} className="h-2" />
          </div>
        )}
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricBox 
          label="Confidence Score" 
          value={agent.confidence} 
          suffix="%" 
          icon={Target}
          trend="+2.3%"
        />
        <MetricBox 
          label="Items Processed" 
          value={agent.processedItems.toLocaleString()} 
          icon={BarChart3}
          trend="+847"
        />
        <MetricBox 
          label="Success Rate" 
          value={agent.successRate} 
          suffix="%" 
          icon={Zap}
          trend="+0.4%"
        />
        <MetricBox 
          label="Avg Latency" 
          value={agent.metrics.latency} 
          suffix="ms" 
          icon={Clock}
        />
      </div>

      {/* Performance Metrics */}
      <div className="glass-panel rounded-xl border border-border p-6">
        <h2 className="text-sm font-bold text-foreground uppercase tracking-wider mb-6">
          Performance Metrics
        </h2>
        <div className="grid grid-cols-3 gap-8">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-muted-foreground">Throughput</span>
              <span className="text-xs font-mono text-foreground">
                {agent.metrics.throughput}/min
              </span>
            </div>
            <Progress value={75} className="h-2" />
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-muted-foreground">Latency</span>
              <span className="text-xs font-mono text-foreground">
                {agent.metrics.latency}ms
              </span>
            </div>
            <Progress value={30} className="h-2" />
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-muted-foreground">Accuracy</span>
              <span className="text-xs font-mono text-foreground">
                {agent.metrics.accuracy}%
              </span>
            </div>
            <Progress value={agent.metrics.accuracy} className="h-2" />
          </div>
        </div>
      </div>

      {/* Capabilities */}
      <div className="glass-panel rounded-xl border border-border p-6">
        <h2 className="text-sm font-bold text-foreground uppercase tracking-wider mb-4">
          Capabilities
        </h2>
        <div className="flex flex-wrap gap-2">
          {agent.capabilities.map((capability) => (
            <CapabilityChip key={capability} capability={capability} />
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="glass-panel rounded-xl border border-border p-6">
        <h2 className="text-sm font-bold text-foreground uppercase tracking-wider mb-4">
          Recent Activity
        </h2>
        <div className="space-y-3">
          {[
            { time: '2 seconds ago', action: 'Processed batch #4521 successfully' },
            { time: '15 seconds ago', action: 'Received new data stream from API' },
            { time: '32 seconds ago', action: 'Completed entity extraction task' },
            { time: '1 minute ago', action: 'Started processing pipeline cycle' },
            { time: '2 minutes ago', action: 'Health check passed' }
          ].map((activity, index) => (
            <div key={index} className="flex items-center gap-3 text-sm">
              <div className="w-1.5 h-1.5 rounded-full bg-primary" />
              <span className="text-foreground">{activity.action}</span>
              <span className="text-muted-foreground text-xs ml-auto font-mono">
                {activity.time}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
