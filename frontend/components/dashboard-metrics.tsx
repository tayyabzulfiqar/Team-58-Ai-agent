'use client'

import { useEffect, useState } from 'react'
import { cn } from '../lib/utils'
import { 
  TrendingUp, 
  Zap, 
  DollarSign, 
  Target,
  Activity,
  Database,
  Clock,
  Wifi,
  ArrowUpRight
} from 'lucide-react'

interface DashboardMetricsProps {
  scores?: number[]
  opportunities?: Array<{
    id: number
    name: string
    company: string
    score: number
    status: string
    revenue_potential: number
    industry: string
    location: string
  }>
}

interface Metric {
  label: string
  value: number
  prefix?: string
  suffix?: string
  format?: boolean
  icon: React.ElementType
  color: string
  bg: string
  border: string
  trend: string
  trendUp: boolean
}

function AnimatedNumber({ value, prefix = '', suffix = '', format = false }: { 
  value: number
  prefix?: string
  suffix?: string
  format?: boolean 
}) {
  const [display, setDisplay] = useState(0)

  useEffect(() => {
    const duration = 1200
    const steps = 40
    const increment = value / steps
    let current = 0
    
    const timer = setInterval(() => {
      current += increment
      if (current >= value) {
        setDisplay(value)
        clearInterval(timer)
      } else {
        setDisplay(Math.floor(current))
      }
    }, duration / steps)

    return () => clearInterval(timer)
  }, [value])

  return (
    <span className="font-mono">
      {prefix}{format ? display.toLocaleString() : display}{suffix}
    </span>
  )
}

function MetricCard({ metric, index }: { metric: Metric; index: number }) {
  const Icon = metric.icon
  const [hovered, setHovered] = useState(false)

  return (
    <div 
      className={cn(
        "relative glass-panel-elevated rounded-xl border p-5 transition-all duration-300 hover-elevate cursor-pointer",
        metric.border
      )}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div className={cn(
        "absolute -top-8 -right-8 w-24 h-24 rounded-full blur-2xl transition-opacity duration-500",
        metric.bg,
        hovered ? "opacity-30" : "opacity-15"
      )} />

      <div className="relative flex items-start justify-between">
        <div className="flex-1">
          <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-[0.12em] mb-3">
            {metric.label}
          </p>
          <p className={cn("text-2xl font-semibold", metric.color)}>
            <AnimatedNumber 
              value={metric.value} 
              prefix={metric.prefix}
              suffix={metric.suffix}
              format={metric.format}
            />
          </p>
          <div className="mt-3 flex items-center gap-2">
            <div className={cn(
              "flex items-center gap-1 px-1.5 py-0.5 rounded",
              metric.trendUp ? "bg-neon-green/10" : "bg-destructive/10"
            )}>
              <ArrowUpRight className={cn(
                "w-3 h-3",
                metric.trendUp ? "text-neon-green" : "text-destructive rotate-90"
              )} />
              <span className={cn(
                "text-[10px] font-mono font-medium",
                metric.trendUp ? "text-neon-green" : "text-destructive"
              )}>
                {metric.trend}
              </span>
            </div>
            <span className="text-[9px] text-muted-foreground">vs last week</span>
          </div>
        </div>
        
        <div className={cn(
          "w-12 h-12 rounded-lg flex items-center justify-center transition-all duration-300",
          metric.bg,
          hovered && "scale-110"
        )}>
          <Icon className={cn("w-5 h-5", metric.color)} />
        </div>
      </div>
    </div>
  )
}

export function DashboardMetrics({ scores, opportunities }: DashboardMetricsProps) {
  const totalOpportunities = opportunities?.length || 0
  const activeCampaigns = opportunities?.filter(o => o.score > 80).length || 0
  const pipelineValue = opportunities?.reduce((sum, o) => sum + (o.revenue_potential || 0), 0) || 0
  const avgScore = scores?.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0

  const metrics: Metric[] = [
    {
      label: 'Total Opportunities',
      value: totalOpportunities,
      icon: Target,
      color: 'text-primary',
      bg: 'bg-primary/10',
      border: 'border-primary/20',
      trend: '+12.5%',
      trendUp: true
    },
    {
      label: 'Active Campaigns',
      value: activeCampaigns,
      icon: Zap,
      color: 'text-neon-cyan',
      bg: 'bg-neon-cyan/10',
      border: 'border-neon-cyan/20',
      trend: '+3',
      trendUp: true
    },
    {
      label: 'Pipeline Value',
      value: pipelineValue,
      prefix: '$',
      format: true,
      icon: DollarSign,
      color: 'text-neon-green',
      bg: 'bg-neon-green/10',
      border: 'border-neon-green/20',
      trend: '+8.2%',
      trendUp: true
    },
    {
      label: 'Avg Score',
      value: avgScore,
      suffix: '%',
      icon: TrendingUp,
      color: 'text-neon-orange',
      bg: 'bg-neon-orange/10',
      border: 'border-neon-orange/20',
      trend: '+1.3%',
      trendUp: true
    }
  ]

  const miniMetrics = [
    { label: 'System Health', value: '98%', icon: Activity, color: 'text-neon-green' },
    { label: 'Data Processed', value: '2.4M', icon: Database, color: 'text-neon-cyan' },
    { label: 'Uptime', value: '99.9%', icon: Clock, color: 'text-primary' },
    { label: 'Connections', value: '47', icon: Wifi, color: 'text-neon-orange' }
  ]

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-4 gap-4">
        {metrics.map((metric, index) => (
          <MetricCard key={metric.label} metric={metric} index={index} />
        ))}
      </div>

      <div className="glass-panel rounded-lg p-4">
        <div className="grid grid-cols-4 gap-4">
          {miniMetrics.map((metric) => {
            const Icon = metric.icon
            return (
              <div 
                key={metric.label} 
                className="flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-300 hover:bg-secondary/30 cursor-pointer group"
              >
                <div className="w-9 h-9 rounded-lg bg-secondary/50 flex items-center justify-center group-hover:bg-secondary transition-all">
                  <Icon className={cn("w-4 h-4", metric.color)} />
                </div>
                <div>
                  <p className="text-[9px] text-muted-foreground uppercase tracking-wide mb-0.5">
                    {metric.label}
                  </p>
                  <p className={cn("text-sm font-semibold font-mono", metric.color)}>
                    {metric.value}
                  </p>
                </div>
                <div className="ml-auto">
                  <div className={cn("w-1.5 h-1.5 rounded-full", metric.color.replace('text-', 'bg-'))} />
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

