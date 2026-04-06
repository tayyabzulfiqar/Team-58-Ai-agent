'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import { cn } from '../../../lib/utils'
import { agents } from '../../../lib/mock-data'
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
  Settings,
} from 'lucide-react'
import { Button } from '../../../components/ui/button'
import { Progress } from '../../../components/ui/progress'
import { Badge } from '../../../components/ui/badge'
import { DashboardShell } from '../../../components/dashboard-shell'

const statusConfig = {
  active: {
    label: 'ACTIVE',
    color: 'text-neon-green',
    bg: 'bg-neon-green/20',
    border: 'border-neon-green/30',
    glow: 'neon-glow-green',
  },
  processing: {
    label: 'PROCESSING',
    color: 'text-neon-cyan',
    bg: 'bg-neon-cyan/20',
    border: 'border-neon-cyan/30',
    glow: 'neon-glow-cyan',
  },
  idle: {
    label: 'IDLE',
    color: 'text-muted-foreground',
    bg: 'bg-muted',
    border: 'border-muted',
    glow: '',
  },
}

function MetricBox({
  label,
  value,
  suffix = '',
  icon: Icon,
  trend,
}: {
  label: string
  value: string | number
  suffix?: string
  icon: React.ComponentType<{ className?: string }>
  trend?: string
}) {
  return (
    <div className="glass-panel rounded-xl border border-border p-4">
      <div className="mb-3 flex items-start justify-between">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
          <Icon className="h-5 w-5 text-primary" />
        </div>
        {trend && (
          <div className="flex items-center gap-1">
            <TrendingUp className="h-3 w-3 text-neon-green" />
            <span className="text-xs font-mono text-neon-green">{trend}</span>
          </div>
        )}
      </div>
      <p className="font-mono text-2xl font-bold text-foreground">
        {value}
        {suffix}
      </p>
      <p className="mt-1 text-xs uppercase tracking-wider text-muted-foreground">
        {label}
      </p>
    </div>
  )
}

function CapabilityChip({ capability }: { capability: string }) {
  return (
    <div className="rounded-lg border border-border bg-secondary px-3 py-1.5 text-xs font-medium text-foreground">
      {capability}
    </div>
  )
}

export default function AgentDetailPage() {
  const params = useParams()
  const agent = agents.find((item) => item.id === params.id)

  if (!agent) {
    return (
      <DashboardShell>
        <div className="flex h-full items-center justify-center">
          <p className="text-muted-foreground">Agent not found</p>
        </div>
      </DashboardShell>
    )
  }

  const status = statusConfig[agent.status]

  return (
    <DashboardShell>
      <div className="space-y-8 p-8">
        <Link
          href="/agent"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Agents
        </Link>

        <header className="flex items-start justify-between">
          <div className="flex items-start gap-6">
            <div
              className={cn(
                'flex h-20 w-20 items-center justify-center rounded-2xl border',
                status.bg,
                status.border,
                status.glow
              )}
            >
              <Activity className={cn('h-10 w-10', status.color)} />
            </div>

            <div>
              <div className="mb-2 flex items-center gap-3">
                <h1 className="text-3xl font-bold text-foreground">{agent.name}</h1>
                <Badge
                  variant="outline"
                  className={cn('text-xs font-bold', status.bg, status.color, status.border)}
                >
                  <span
                    className={cn(
                      'mr-1.5 h-1.5 w-1.5 rounded-full',
                      agent.status === 'active' && 'bg-neon-green animate-pulse',
                      agent.status === 'processing' && 'bg-neon-cyan animate-pulse',
                      agent.status === 'idle' && 'bg-muted-foreground'
                    )}
                  />
                  {status.label}
                </Badge>
              </div>
              <p className="max-w-md text-muted-foreground">{agent.description}</p>
              <p className="mt-2 text-xs font-mono text-muted-foreground">
                Last active: {agent.lastActive}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" className="gap-2">
              <RefreshCw className="h-4 w-4" />
              Restart
            </Button>
            <Button variant="outline" size="sm" className="gap-2">
              {agent.status === 'active' || agent.status === 'processing' ? (
                <>
                  <Pause className="h-4 w-4" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Start
                </>
              )}
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </header>

        <div className={cn('glass-panel rounded-xl border p-6', status.border)}>
          <div className="mb-3 flex items-center gap-2">
            <div
              className={cn(
                'h-2 w-2 rounded-full',
                agent.status !== 'idle' ? 'animate-pulse' : '',
                agent.status === 'active' && 'bg-neon-green',
                agent.status === 'processing' && 'bg-neon-cyan',
                agent.status === 'idle' && 'bg-muted-foreground'
              )}
            />
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Current Task
            </span>
          </div>
          <p className="font-mono text-lg font-medium text-foreground">{agent.currentTask}</p>
          {agent.status !== 'idle' && (
            <div className="mt-4">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Progress</span>
                <span className="text-xs font-mono text-foreground">67%</span>
              </div>
              <Progress value={67} className="h-2" />
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
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
          <MetricBox label="Avg Latency" value={agent.metrics.latency} suffix="ms" icon={Clock} />
        </div>

        <div className="glass-panel rounded-xl border border-border p-6">
          <h2 className="mb-6 text-sm font-bold uppercase tracking-wider text-foreground">
            Performance Metrics
          </h2>
          <div className="grid grid-cols-3 gap-8">
            <div>
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Throughput</span>
                <span className="text-xs font-mono text-foreground">
                  {agent.metrics.throughput}/min
                </span>
              </div>
              <Progress value={75} className="h-2" />
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Latency</span>
                <span className="text-xs font-mono text-foreground">{agent.metrics.latency}ms</span>
              </div>
              <Progress value={30} className="h-2" />
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Accuracy</span>
                <span className="text-xs font-mono text-foreground">
                  {agent.metrics.accuracy}%
                </span>
              </div>
              <Progress value={agent.metrics.accuracy} className="h-2" />
            </div>
          </div>
        </div>

        <div className="glass-panel rounded-xl border border-border p-6">
          <h2 className="mb-4 text-sm font-bold uppercase tracking-wider text-foreground">
            Capabilities
          </h2>
          <div className="flex flex-wrap gap-2">
            {agent.capabilities.map((capability) => (
              <CapabilityChip key={capability} capability={capability} />
            ))}
          </div>
        </div>

        <div className="glass-panel rounded-xl border border-border p-6">
          <h2 className="mb-4 text-sm font-bold uppercase tracking-wider text-foreground">
            Recent Activity
          </h2>
          <div className="space-y-3">
            {[
              { time: '2 seconds ago', action: 'Processed batch #4521 successfully' },
              { time: '15 seconds ago', action: 'Received new data stream from API' },
              { time: '32 seconds ago', action: 'Completed entity extraction task' },
              { time: '1 minute ago', action: 'Started processing pipeline cycle' },
              { time: '2 minutes ago', action: 'Health check passed' },
            ].map((activity, index) => (
              <div key={index} className="flex items-center gap-3 text-sm">
                <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                <span className="text-foreground">{activity.action}</span>
                <span className="ml-auto text-xs font-mono text-muted-foreground">
                  {activity.time}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardShell>
  )
}

