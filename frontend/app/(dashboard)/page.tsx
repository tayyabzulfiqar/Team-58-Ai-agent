'use client'

import { useEffect, useState, useCallback } from 'react'
import { PipelineVisualization } from '@/components/pipeline-visualization'
import { DashboardMetrics } from '@/components/dashboard-metrics'
import { OpportunitiesTable } from '@/components/opportunities-table'
import { CampaignsTable } from '@/components/campaigns-table'
import { IntelligenceFeed } from '@/components/intelligence-feed'
import { AgentControlPanel } from '@/components/agent-control-panel'
import { 
  Shield, 
  Radio, 
  Satellite, 
  AlertTriangle, 
  Loader2,
  RefreshCw,
  Activity,
  Brain,
  Cpu
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface DashboardData {
  opportunities: Array<{
    id: number
    name: string
    company: string
    score: number
    status: string
    revenue_potential: number
    industry: string
    location: string
  }>
  scores: number[]
  decisions: string[]
  campaigns: Array<{
    id: number
    name: string
    status: string
    budget: number
    roi: number
    target: string
  }>
  status: string
  message?: string
}

export default function DashboardPage() {
  const [systemTime, setSystemTime] = useState('')
  const [threatLevel, setThreatLevel] = useState<'LOW' | 'MEDIUM' | 'HIGH'>('LOW')
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isPaused, setIsPaused] = useState(false)

  // Clock update
  useEffect(() => {
    const updateTime = () => {
      setSystemTime(new Date().toLocaleTimeString('en-US', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }))
    }
    updateTime()
    const interval = setInterval(updateTime, 1000)
    return () => clearInterval(interval)
  }, [])

  // Threat level simulation
  useEffect(() => {
    const interval = setInterval(() => {
      const rand = Math.random()
      setThreatLevel(rand > 0.92 ? 'HIGH' : rand > 0.75 ? 'MEDIUM' : 'LOW')
    }, 12000)
    return () => clearInterval(interval)
  }, [])

  // Fetch data function
  const fetchData = useCallback(async (showLoading = true) => {
    if (isPaused) return
    
    try {
      if (showLoading) setLoading(true)
      setError(null)
      
      const response = await fetch('/api/run-system', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.status === 'error') {
        throw new Error(result.message || 'Unknown error')
      }
      
      setData(result)
      setLastUpdated(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'System temporarily unavailable')
      console.error('Dashboard fetch error:', err)
    } finally {
      if (showLoading) setLoading(false)
    }
  }, [isPaused])

  // Initial load
  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Auto refresh every 45 seconds
  useEffect(() => {
    if (isPaused) return
    
    const interval = setInterval(() => {
      fetchData(false)
    }, 45000)
    
    return () => clearInterval(interval)
  }, [fetchData, isPaused])

  const handleRunSystem = () => {
    fetchData(true)
  }

  const handlePause = () => {
    setIsPaused(!isPaused)
  }

  return (
    <div className="p-8 space-y-6 min-h-screen transition-all duration-500">
      {/* Header */}
      <header className="flex items-center justify-between animate-fade-in">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="relative">
              <Shield className="w-6 h-6 text-primary" />
              <div className="absolute inset-0 animate-ping opacity-30">
                <Shield className="w-6 h-6 text-primary" />
              </div>
            </div>
            <h1 className="text-xl font-semibold text-foreground tracking-wide uppercase">
              AI Command Center
            </h1>
          </div>
          <p className="text-muted-foreground font-mono text-xs uppercase tracking-[0.15em]">
            Multi-Agent Intelligence System / v3.0.0
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Threat Level */}
          <div className={cn(
            "glass-panel rounded-lg px-4 py-2.5 border transition-all duration-300 hover:scale-105",
            threatLevel === 'LOW' && "border-neon-green/30",
            threatLevel === 'MEDIUM' && "border-neon-orange/30",
            threatLevel === 'HIGH' && "border-destructive/40"
          )}>
            <div className="flex items-center gap-3">
              <AlertTriangle className={cn(
                "w-4 h-4 transition-colors duration-300",
                threatLevel === 'LOW' && "text-neon-green",
                threatLevel === 'MEDIUM' && "text-neon-orange",
                threatLevel === 'HIGH' && "text-destructive animate-pulse"
              )} />
              <div>
                <p className="text-[9px] text-muted-foreground uppercase tracking-wide">Threat</p>
                <p className={cn(
                  "text-sm font-semibold font-mono transition-colors duration-300",
                  threatLevel === 'LOW' && "text-neon-green",
                  threatLevel === 'MEDIUM' && "text-neon-orange",
                  threatLevel === 'HIGH' && "text-destructive"
                )}>
                  {threatLevel}
                </p>
              </div>
            </div>
          </div>

          {/* System Status */}
          <div className="glass-panel rounded-lg px-4 py-2.5 border border-neon-green/30 hover:scale-105 transition-transform duration-300">
            <div className="flex items-center gap-3">
              <div className="relative">
                <Radio className="w-4 h-4 text-neon-green" />
                <div className="absolute inset-0 animate-ping opacity-40">
                  <Radio className="w-4 h-4 text-neon-green" />
                </div>
              </div>
              <div>
                <p className="text-[9px] text-muted-foreground uppercase tracking-wide">Status</p>
                <p className="text-sm font-semibold font-mono text-neon-green">OPERATIONAL</p>
              </div>
            </div>
          </div>

          {/* Time */}
          <div className="glass-panel rounded-lg px-4 py-2.5 border border-border/40 hover:scale-105 transition-transform duration-300">
            <div className="flex items-center gap-3">
              <Satellite className="w-4 h-4 text-neon-cyan animate-pulse" />
              <div>
                <p className="text-[9px] text-muted-foreground uppercase tracking-wide">Sync</p>
                <p className="text-sm font-semibold font-mono text-foreground" suppressHydrationWarning>
                  {systemTime || '--:--:--'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Control Panel */}
      <AgentControlPanel 
        onRunSystem={handleRunSystem}
        onPause={handlePause}
        isPaused={isPaused}
        isLoading={loading}
        lastUpdated={lastUpdated}
      />

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-16 space-y-4 animate-fade-in">
          <div className="relative">
            <Loader2 className="w-12 h-12 animate-spin text-primary" />
            <div className="absolute inset-0 animate-ping opacity-20">
              <Loader2 className="w-12 h-12 text-primary" />
            </div>
          </div>
          <div className="text-center space-y-2">
            <p className="text-lg font-medium text-foreground">Initializing AI system...</p>
            <p className="text-sm text-muted-foreground">Executing data → processing → intelligence → decision pipeline</p>
          </div>
          <div className="flex items-center gap-4 mt-4">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Brain className="w-4 h-4 text-neon-cyan animate-pulse" />
              <span>Intelligence Agent</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Cpu className="w-4 h-4 text-neon-green animate-pulse" />
              <span>Processing Agent</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Activity className="w-4 h-4 text-neon-orange animate-pulse" />
              <span>Decision Agent</span>
            </div>
          </div>
        </div>
      )}

      {/* Error State - Graceful */}
      {error && (
        <div className="glass-panel rounded-xl p-8 border border-destructive/30 bg-destructive/5 animate-fade-in">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center flex-shrink-0">
              <AlertTriangle className="w-6 h-6 text-destructive" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-destructive mb-1">System temporarily unavailable</h3>
              <p className="text-sm text-muted-foreground mb-4">
                The AI pipeline is experiencing connectivity issues. Your data is safe and will resume shortly.
              </p>
              <div className="flex items-center gap-3">
                <button 
                  onClick={() => fetchData(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  Retry Connection
                </button>
                <span className="text-xs text-muted-foreground">
                  Auto-retry in 45 seconds
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Data Display */}
      {!loading && !error && data && (
        <div className="space-y-6 animate-fade-in">
          {/* Main Grid with Intelligence Feed */}
          <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
            <div className="xl:col-span-3 space-y-6">
              {/* Metrics */}
              <DashboardMetrics scores={data.scores} opportunities={data.opportunities} />

              {/* Pipeline */}
              <section className="glass-panel-elevated rounded-xl overflow-hidden transition-all duration-300 hover:shadow-lg hover:shadow-primary/5">
                <PipelineVisualization decisions={data.decisions} />
              </section>

              {/* Tables */}
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <OpportunitiesTable opportunities={data.opportunities} />
                <CampaignsTable campaigns={data.campaigns} />
              </div>
            </div>

            {/* Intelligence Feed Panel */}
            <div className="xl:col-span-1">
              <IntelligenceFeed 
                opportunities={data.opportunities}
                isPaused={isPaused}
              />
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="flex items-center justify-between text-xs text-muted-foreground pt-4 border-t border-border/20">
        <div className="flex items-center gap-4">
          <span>AI Agents: 4 active</span>
          <span className="w-1 h-1 rounded-full bg-muted-foreground/30" />
          <span>Data Sources: Live</span>
          <span className="w-1 h-1 rounded-full bg-muted-foreground/30" />
          <span>Version: 3.0.0</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
          <span>System Operational</span>
        </div>
      </footer>
    </div>
  )
}
