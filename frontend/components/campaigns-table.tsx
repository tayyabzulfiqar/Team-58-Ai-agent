'use client'

import { cn } from '@/lib/utils'
import { Rocket, TrendingUp, AlertTriangle, CheckCircle2, Target, Zap } from 'lucide-react'

interface Campaign {
  id: number
  name: string
  status: string
  budget: number
  roi: number
  target: string
}

interface CampaignsTableProps {
  campaigns?: Campaign[]
}

const statusStyles: Record<string, { bg: string; text: string; label: string }> = {
  active: { bg: 'bg-neon-green/10', text: 'text-neon-green', label: 'Active' },
  paused: { bg: 'bg-neon-orange/10', text: 'text-neon-orange', label: 'Paused' },
  completed: { bg: 'bg-muted/30', text: 'text-muted-foreground', label: 'Completed' },
  scheduled: { bg: 'bg-primary/10', text: 'text-primary', label: 'Scheduled' },
  Active: { bg: 'bg-neon-green/10', text: 'text-neon-green', label: 'Active' },
  Pending: { bg: 'bg-neon-orange/10', text: 'text-neon-orange', label: 'Pending' }
}

function getPerformanceIndicator(roi: number): { label: string; color: string; icon: React.ElementType } {
  if (roi >= 100) return { label: 'Exceptional', color: 'text-neon-green', icon: Zap }
  if (roi >= 50) return { label: 'Strong', color: 'text-neon-cyan', icon: TrendingUp }
  if (roi >= 20) return { label: 'Good', color: 'text-primary', icon: CheckCircle2 }
  return { label: 'Monitor', color: 'text-neon-orange', icon: AlertTriangle }
}

function getCampaignReason(roi: number, budget: number): string {
  if (roi >= 100) return 'High conversion rate detected'
  if (roi >= 50) return 'Strong audience engagement'
  if (budget > 50000) return 'Significant budget allocation'
  return 'Standard performance metrics'
}

export function CampaignsTable({ campaigns = [] }: CampaignsTableProps) {
  const displayCampaigns = campaigns.length > 0 ? campaigns : []

  return (
    <div className="glass-panel-elevated rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4 border-b border-border/20">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-neon-cyan/10 flex items-center justify-center">
            <Rocket className="w-4 h-4 text-neon-cyan" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground text-sm">Active Campaigns</h3>
            <p className="text-[10px] text-muted-foreground">AI-optimized operations</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-neon-green animate-pulse" />
            <span className="text-[10px] text-neon-green font-medium">{displayCampaigns.length} active</span>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border/15 bg-secondary/10">
              <th className="text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wide px-5 py-3">Campaign</th>
              <th className="text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wide px-5 py-3">Performance</th>
              <th className="text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wide px-5 py-3">ROI</th>
              <th className="text-left text-[10px] font-semibold text-muted-foreground uppercase tracking-wide px-5 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {displayCampaigns.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-5 py-8 text-center text-muted-foreground">
                  <div className="flex flex-col items-center gap-2">
                    <Rocket className="w-8 h-8 text-muted-foreground/30" />
                    <p>No campaigns available</p>
                    <p className="text-xs">Run the AI pipeline to generate campaigns</p>
                  </div>
                </td>
              </tr>
            ) : (
              displayCampaigns.map((campaign, index) => {
                const statusKey = campaign.status || 'active'
                const statusStyle = statusStyles[statusKey] || statusStyles.active
                const perf = getPerformanceIndicator(campaign.roi || 0)
                const PerfIcon = perf.icon
                const reason = getCampaignReason(campaign.roi || 0, campaign.budget || 0)
                
                return (
                  <tr key={campaign.id || index} className="border-b border-border/10 hover:bg-secondary/5 transition-colors group">
                    <td className="px-5 py-4">
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">{campaign.name}</p>
                        <p className="text-[10px] text-muted-foreground">Target: {campaign.target}</p>
                        <p className="text-[9px] text-muted-foreground/70 mt-1">Budget: ${(campaign.budget || 0).toLocaleString()}</p>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <PerfIcon className={cn("w-4 h-4", perf.color)} />
                        <span className={cn("text-xs font-medium", perf.color)}>{perf.label}</span>
                      </div>
                      <p className="text-[9px] text-muted-foreground/70 mt-1">{reason}</p>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-12 h-1.5 rounded-full bg-secondary/50 overflow-hidden">
                          <div 
                            className="h-full rounded-full bg-gradient-to-r from-neon-green to-neon-cyan"
                            style={{ width: `${Math.min((campaign.roi || 0), 100)}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-neon-green">{campaign.roi || 0}x</span>
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

