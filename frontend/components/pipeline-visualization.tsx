'use client'

import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'
import { Search, Cpu, Brain, Target, Megaphone, ChevronRight } from 'lucide-react'

interface PipelineVisualizationProps {
  decisions?: string[]
}

const agentIcons = {
  research: Search,
  processing: Cpu,
  intelligence: Brain,
  decision: Target,
  campaign: Megaphone
}

const statusMessages = {
  research: [
    'Analyzing data points...',
    'Scanning market intelligence...',
    'Processing social signals...',
    'Extracting entity profiles...',
    'Monitoring data streams...'
  ],
  processing: [
    'Normalizing batch...',
    'Enriching records...',
    'Validating schema integrity...',
    'Compressing data pipeline...',
    'Synchronizing clusters...'
  ],
  intelligence: [
    'Generating predictive models...',
    'Correlating opportunity signals...',
    'Analyzing competitor patterns...',
    'Computing risk vectors...',
    'Synthesizing insights...'
  ],
  decision: [
    'Evaluating strategies...',
    'Optimizing resource allocation...',
    'Ranking priority targets...',
    'Executing decision tree...',
    'Computing probability matrix...'
  ],
  campaign: [
    'Executing sequence...',
    'Optimizing engagement flow...',
    'Tracking conversions...',
    'Analyzing response rates...',
    'Refining audience segments...'
  ]
}

export function PipelineVisualization({ decisions = [] }: PipelineVisualizationProps) {
  const [activeAgent, setActiveAgent] = useState(0)
  const [statusText, setStatusText] = useState('Initializing AI pipeline...')

  const agents = [
    { id: 'research', name: 'Research Agent', color: 'text-neon-cyan', bg: 'bg-neon-cyan/10' },
    { id: 'processing', name: 'Processing Agent', color: 'text-neon-orange', bg: 'bg-neon-orange/10' },
    { id: 'intelligence', name: 'Intelligence Agent', color: 'text-neon-green', bg: 'bg-neon-green/10' },
    { id: 'decision', name: 'Decision Agent', color: 'text-primary', bg: 'bg-primary/10' },
    { id: 'campaign', name: 'Campaign Agent', color: 'text-neon-cyan', bg: 'bg-neon-cyan/10' }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveAgent((prev) => (prev + 1) % agents.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const agent = agents[activeAgent].id as keyof typeof statusMessages
    const messages = statusMessages[agent]
    const randomMessage = messages[Math.floor(Math.random() * messages.length)]
    setStatusText(randomMessage)
  }, [activeAgent])

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-sm font-semibold text-foreground">AI Pipeline Status</h3>
          <p className="text-[10px] text-muted-foreground">Real-time agent execution</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
          <span className="text-xs text-neon-green font-medium">{statusText}</span>
        </div>
      </div>

      <div className="flex items-center gap-4 mb-8">
        {agents.map((agent, index) => {
          const Icon = agentIcons[agent.id as keyof typeof agentIcons]
          const isActive = index === activeAgent
          const isComplete = index < activeAgent
          
          return (
            <div key={agent.id} className="flex items-center gap-2">
              <div className={cn(
                "w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-300",
                isActive ? agent.bg : isComplete ? 'bg-neon-green/20' : 'bg-secondary/30',
                isActive && "ring-2 ring-offset-2 ring-offset-background ring-current"
              )}>
                <Icon className={cn(
                  "w-5 h-5",
                  isActive ? agent.color : isComplete ? 'text-neon-green' : 'text-muted-foreground'
                )} />
              </div>
              {index < agents.length - 1 && (
                <ChevronRight className={cn(
                  "w-4 h-4",
                  isComplete ? 'text-neon-green' : 'text-muted-foreground'
                )} />
              )}
            </div>
          )
        })}
      </div>

      {decisions.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xs font-semibold text-foreground uppercase tracking-wide">AI Decisions</h4>
          <div className="space-y-2">
            {decisions.slice(0, 5).map((decision, index) => (
              <div 
                key={index}
                className="flex items-center gap-3 p-3 rounded-lg bg-secondary/30 border border-border/10"
              >
                <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-[10px] font-bold text-primary">
                  {index + 1}
                </div>
                <p className="text-sm text-foreground flex-1">{decision}</p>
                <div className="w-2 h-2 rounded-full bg-neon-green" />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

