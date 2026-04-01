'use client'

import { cn } from '@/lib/utils'
import { Target, TrendingUp, AlertTriangle, CheckCircle2, Info, Shield } from 'lucide-react'

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

interface OpportunitiesTableProps {
  opportunities?: Opportunity[]
}

const statusStyles: Record<string, { bg: string; text: string; label: string }> = {
  new: { bg: 'bg-primary/10', text: 'text-primary', label: 'New' },
  engaged: { bg: 'bg-neon-cyan/10', text: 'text-neon-cyan', label: 'Engaged' },
  qualified: { bg: 'bg-neon-green/10', text: 'text-neon-green', label: 'Qualified' },
  closed: { bg: 'bg-muted/30', text: 'text-muted-foreground', label: 'Closed' },
  Pending: { bg: 'bg-neon-orange/10', text: 'text-neon-orange', label: 'Pending' },
  Approved: { bg: 'bg-neon-green/10', text: 'text-neon-green', label: 'Approved' },
  Rejected: { bg: 'bg-destructive/10', text: 'text-destructive', label: 'Rejected' }
}

function getRiskLevel(score: number): { level: string; color: string; icon: React.ElementType } {
  if (score >= 85) return { level: 'Low', color: 'text-neon-green', icon: Shield }
  if (score >= 70) return { level: 'Medium', color: 'text-neon-orange', icon: Info }
  return { level: 'High', color: 'text-destructive', icon: AlertTriangle }
}

function getReason(score: number, industry: string): string {
  if (score >= 90) return `Exceptional engagement in ${industry} sector`
  if (score >= 80) return `High revenue potential and strong fit`
  if (score >= 70) return `Moderate interest, worth nurturing`
  return `Early stage, monitor for growth`
}

export function OpportunitiesTable({ opportunities = [] }: OpportunitiesTableProps) {
  const displayOpportunities = opportunities.length > 0 ? opportunities : []

  return (
    <div className="glass-panel-elevated rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4 border-b border-border/20">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <Target className="w-4 h-4 text-primary" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground text-sm">High-Value Opportunities</h3>
            <p className="text-[10px] text-muted-foreground">AI-detected targets with analysis</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <TrendingUp className="w-3.5 h-3.5 text-neon-green" />
          <span className="text-xs text-neon-green font-medium">+{opportunities.length} this week</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border/15 bg-secondary/10">
              <th className="text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wide px-5 py-3">Company</th>
              <th className="text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wide px-5 py-3">Confidence</th>
              <th className="text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wide px-5 py-3">Risk</th>
              <th className="text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wide px-5 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {displayOpportunities.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-5 py-8 text-center text-muted-foreground">
                  <div className="flex flex-col items-center gap-2">
                    <Target className="w-8 h-8 text-muted-foreground/30" />
                    <p>No opportunities available</p>
                    <p className="text-xs">Run the AI pipeline to generate data</p>
                  </div>
                </td>
              </tr>
            ) : (
              displayOpportunities.map((opp, index) => {
                const statusKey = opp.status || 'new'
                const statusStyle = statusStyles[statusKey] || statusStyles.new
                const risk = getRiskLevel(opp.score)
                const RiskIcon = risk.icon
                const reason = getReason(opp.score, opp.industry)
                
                return (
                  <tr key={opp.id || index} className="border-b border-border/10 hover:bg-secondary/5 transition-colors group">
                    <td className="px-5 py-4">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-xs font-bold text-primary flex-shrink-0">
                          {opp.company?.charAt(0) || '?'}
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-foreground truncate">{opp.name}</p>
                          <p className="text-[10px] text-muted-foreground">{opp.company} • {opp.industry}</p>
                          <p className="text-[9px] text-muted-foreground/70 mt-1 truncate">{reason}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 rounded-full bg-secondary/50 overflow-hidden">
                            <div 
                              className="h-full rounded-full bg-gradient-to-r from-neon-cyan to-neon-green transition-all duration-500"
                              style={{ width: `${opp.score || 0}%` }}
                            />
                          </div>
                          <span className="text-xs font-medium text-foreground">{opp.score || 0}%</span>
                        </div>
                        <p className="text-[9px] text-muted-foreground">Revenue: ${(opp.revenue_potential || 0).toLocaleString()}</p>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-1.5">
                        <RiskIcon className={cn("w-3.5 h-3.5", risk.color)} />
                        <span className={cn("text-xs font-medium", risk.color)}>{risk.level}</span>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <span className={cn(
                        "px-2 py-1 rounded-full text-[10px] font-medium",
                        statusStyle.bg,
                        statusStyle.text
                      )}>
                        {statusStyle.label}
                      </span>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
