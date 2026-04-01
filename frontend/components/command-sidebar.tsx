'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { 
  LayoutDashboard, 
  Search, 
  Cpu, 
  Brain, 
  Target, 
  Megaphone,
  Hexagon,
  Settings,
  ChevronRight,
  Radio,
  Zap
} from 'lucide-react'
import { agents } from '@/lib/mock-data'

const navItems = [
  { name: 'Command Center', href: '/', icon: LayoutDashboard },
  { name: 'Research Agent', href: '/agent/research', icon: Search, agentId: 'research' },
  { name: 'Processing Agent', href: '/agent/processing', icon: Cpu, agentId: 'processing' },
  { name: 'Intelligence Agent', href: '/agent/intelligence', icon: Brain, agentId: 'intelligence' },
  { name: 'Decision Agent', href: '/agent/decision', icon: Target, agentId: 'decision' },
  { name: 'Campaign Agent', href: '/agent/campaign', icon: Megaphone, agentId: 'campaign' },
]

function StatusDot({ status }: { status: 'active' | 'processing' | 'idle' }) {
  return (
    <div className="relative">
      <span className={cn(
        "w-2 h-2 rounded-full block",
        status === 'active' && "bg-neon-green",
        status === 'processing' && "bg-neon-cyan",
        status === 'idle' && "bg-muted-foreground/40"
      )} />
      {status !== 'idle' && (
        <span className={cn(
          "absolute inset-0 w-2 h-2 rounded-full animate-ping opacity-60",
          status === 'active' && "bg-neon-green",
          status === 'processing' && "bg-neon-cyan"
        )} />
      )}
    </div>
  )
}

export function CommandSidebar() {
  const pathname = usePathname()
  const [systemTime, setSystemTime] = useState('')
  const [cpuLoad, setCpuLoad] = useState(47)
  const [memoryUsage, setMemoryUsage] = useState(62)

  useEffect(() => {
    const updateTime = () => {
      setSystemTime(new Date().toLocaleTimeString('en-US', { hour12: false }))
    }
    updateTime()
    const interval = setInterval(updateTime, 1000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setCpuLoad(prev => Math.min(90, Math.max(30, prev + (Math.random() - 0.5) * 8)))
      setMemoryUsage(prev => Math.min(85, Math.max(45, prev + (Math.random() - 0.5) * 4)))
    }, 3500)
    return () => clearInterval(interval)
  }, [])

  return (
    <aside className="w-64 h-screen glass-panel-intense border-r border-border/30 flex flex-col">
      {/* Logo */}
      <div className="p-5 border-b border-border/30">
        <div className="flex items-center gap-3">
          <div className="relative w-10 h-10 rounded-lg bg-gradient-to-br from-primary/25 to-accent/15 flex items-center justify-center">
            <Hexagon className="w-5 h-5 text-primary" />
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-neon-green flex items-center justify-center">
              <div className="w-1.5 h-1.5 rounded-full bg-neon-green animate-pulse" />
            </div>
          </div>
          <div>
            <h1 className="font-semibold text-foreground text-lg tracking-[0.1em]">NEXUS</h1>
            <p className="text-[9px] text-muted-foreground font-mono uppercase tracking-wide">AI COMMAND</p>
          </div>
        </div>
        
        {/* System time */}
        <div className="mt-4 flex items-center justify-between glass-panel rounded-lg px-3 py-2">
          <div className="flex items-center gap-2">
            <Radio className="w-3 h-3 text-neon-green animate-pulse-soft" />
            <span className="text-[10px] text-muted-foreground uppercase">System</span>
          </div>
          <span className="text-sm font-mono text-foreground" suppressHydrationWarning>
            {systemTime || '--:--:--'}
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        <p className="text-[9px] font-semibold text-muted-foreground uppercase tracking-[0.15em] px-3 mb-3">
          Navigation
        </p>
        
        {navItems.map((item) => {
          const isActive = pathname === item.href
          const agent = item.agentId ? agents.find(a => a.id === item.agentId) : null
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "relative flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-300 group",
                isActive 
                  ? "bg-primary/10 text-primary" 
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              )}
            >
              {/* Active indicator */}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-primary rounded-r" />
              )}

              <div className={cn(
                "w-8 h-8 rounded-lg flex items-center justify-center transition-all",
                isActive ? "bg-primary/15" : "bg-secondary/40 group-hover:bg-secondary/60"
              )}>
                <item.icon className={cn(
                  "w-4 h-4 transition-all",
                  isActive && "text-primary"
                )} />
              </div>
              
              <div className="flex-1 min-w-0">
                <span className={cn("text-sm font-medium block truncate", isActive && "text-primary")}>
                  {item.name}
                </span>
                {agent && (
                  <span className={cn(
                    "text-[9px] font-mono uppercase tracking-wide",
                    agent.status === 'active' && "text-neon-green",
                    agent.status === 'processing' && "text-neon-cyan",
                    agent.status === 'idle' && "text-muted-foreground"
                  )}>
                    {agent.status === 'active' ? 'Active' : agent.status === 'processing' ? 'Processing' : 'Standby'}
                  </span>
                )}
              </div>
              
              {agent && <StatusDot status={agent.status} />}
              
              <ChevronRight className={cn(
                "w-4 h-4 opacity-0 transition-all",
                "group-hover:opacity-60",
                isActive && "opacity-100 text-primary"
              )} />
            </Link>
          )
        })}
      </nav>

      {/* System Status */}
      <div className="p-4 border-t border-border/30">
        <div className="glass-panel rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="w-3.5 h-3.5 text-neon-green" />
              <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wide">
                Health
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-neon-green" />
              <span className="text-[9px] text-neon-green font-medium">Optimal</span>
            </div>
          </div>
          
          {/* CPU */}
          <div>
            <div className="flex justify-between text-[10px] mb-1">
              <span className="text-muted-foreground">CPU</span>
              <span className={cn("font-mono font-medium", cpuLoad > 75 ? "text-neon-orange" : "text-foreground")}>
                {Math.round(cpuLoad)}%
              </span>
            </div>
            <div className="h-1 bg-secondary/50 rounded-full overflow-hidden">
              <div 
                className={cn("h-full rounded-full transition-all duration-700", cpuLoad > 75 ? "bg-neon-orange" : "bg-primary")}
                style={{ width: `${cpuLoad}%` }}
              />
            </div>
          </div>
          
          {/* Memory */}
          <div>
            <div className="flex justify-between text-[10px] mb-1">
              <span className="text-muted-foreground">Memory</span>
              <span className="text-foreground font-mono font-medium">{(memoryUsage / 10).toFixed(1)} GB</span>
            </div>
            <div className="h-1 bg-secondary/50 rounded-full overflow-hidden">
              <div className="h-full bg-neon-cyan rounded-full transition-all duration-700" style={{ width: `${memoryUsage}%` }} />
            </div>
          </div>

          {/* Uptime */}
          <div className="flex justify-between items-center pt-1">
            <span className="text-[10px] text-muted-foreground">Uptime</span>
            <span className="text-xs font-mono text-neon-green">99.97%</span>
          </div>
        </div>
      </div>

      {/* Settings */}
      <div className="p-4 border-t border-border/30">
        <Link
          href="/settings"
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary/40 transition-all group"
        >
          <div className="w-8 h-8 rounded-lg bg-secondary/40 flex items-center justify-center group-hover:bg-secondary/60 transition-all">
            <Settings className="w-4 h-4 group-hover:rotate-45 transition-transform duration-300" />
          </div>
          <span className="text-sm font-medium">Settings</span>
        </Link>
      </div>
    </aside>
  )
}
