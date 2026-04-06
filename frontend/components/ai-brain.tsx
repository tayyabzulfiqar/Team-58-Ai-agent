'use client'

import { useEffect, useState } from 'react'
import { cn } from '../lib/utils'
import { Brain, Zap, Activity, Cpu } from 'lucide-react'

const thinkingStates = [
  'Analyzing opportunity patterns...',
  'Processing neural pathways...',
  'Synthesizing market intelligence...',
  'Optimizing decision matrix...',
  'Correlating data streams...',
  'Executing predictive models...',
  'Evaluating risk vectors...',
  'Computing probability scores...'
]

export function AIBrain() {
  const [thinkingText, setThinkingText] = useState(thinkingStates[0])
  const [neuralLoad, setNeuralLoad] = useState(72)
  const [decisions, setDecisions] = useState(1247)
  const [activeNodes, setActiveNodes] = useState(89)

  useEffect(() => {
    const textInterval = setInterval(() => {
      setThinkingText(thinkingStates[Math.floor(Math.random() * thinkingStates.length)])
    }, 3500)

    const loadInterval = setInterval(() => {
      setNeuralLoad(prev => Math.min(95, Math.max(55, prev + (Math.random() - 0.5) * 8)))
    }, 2000)

    const decisionInterval = setInterval(() => {
      setDecisions(prev => prev + Math.floor(Math.random() * 3))
    }, 2500)

    const nodeInterval = setInterval(() => {
      setActiveNodes(prev => Math.min(98, Math.max(80, prev + Math.floor((Math.random() - 0.5) * 4))))
    }, 3000)

    return () => {
      clearInterval(textInterval)
      clearInterval(loadInterval)
      clearInterval(decisionInterval)
      clearInterval(nodeInterval)
    }
  }, [])

  return (
    <div className="relative glass-panel rounded-xl p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-primary" />
          <span className="text-xs font-semibold uppercase tracking-[0.15em] text-foreground">
            System Core
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-neon-green" />
          <span className="text-[10px] text-neon-green font-medium">Online</span>
        </div>
      </div>

      {/* Brain visualization */}
      <div className="relative flex items-center justify-center py-4">
        {/* Outer ring */}
        <svg className="absolute w-28 h-28 animate-rotate-slow opacity-40" viewBox="0 0 112 112">
          <circle
            cx="56"
            cy="56"
            r="50"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            strokeDasharray="12 8"
            className="text-primary/50"
          />
        </svg>

        {/* Inner ring */}
        <svg className="absolute w-20 h-20 animate-rotate-reverse opacity-50" viewBox="0 0 80 80">
          <circle
            cx="40"
            cy="40"
            r="36"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            strokeDasharray="8 6"
            className="text-neon-cyan/40"
          />
        </svg>

        {/* Core */}
        <div className="relative w-14 h-14 rounded-full bg-gradient-to-br from-primary/20 to-accent/10 flex items-center justify-center">
          <Cpu className="w-6 h-6 text-primary animate-pulse-soft" />
          <div className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-neon-green animate-pulse" />
        </div>
      </div>

      {/* Thinking status */}
      <div className="glass-panel rounded-lg p-3 mb-4">
        <div className="flex items-center gap-2 mb-1.5">
          <Activity className="w-3 h-3 text-neon-cyan animate-pulse-soft" />
          <span className="text-[10px] text-muted-foreground uppercase tracking-wide">Current Process</span>
        </div>
        <p className="text-xs font-mono text-neon-cyan">
          {thinkingText}
        </p>
      </div>

      {/* Neural load */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[10px] text-muted-foreground uppercase tracking-wide">Neural Load</span>
          <span className={cn(
            "text-xs font-mono font-semibold",
            neuralLoad > 85 ? "text-neon-orange" : "text-neon-cyan"
          )}>
            {Math.round(neuralLoad)}%
          </span>
        </div>
        <div className="h-1.5 w-full bg-muted/30 rounded-full overflow-hidden">
          <div 
            className={cn(
              "h-full rounded-full transition-all duration-700",
              neuralLoad > 85 
                ? "bg-gradient-to-r from-neon-orange to-neon-red" 
                : "bg-gradient-to-r from-neon-cyan to-primary"
            )}
            style={{ width: `${neuralLoad}%` }}
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3">
        <div className="glass-panel rounded-lg p-3 text-center">
          <div className="flex items-center justify-center gap-1.5 mb-1">
            <Zap className="w-3 h-3 text-neon-green" />
            <span className="text-[9px] text-muted-foreground uppercase">Decisions</span>
          </div>
          <p className="text-base font-semibold font-mono text-foreground">{decisions.toLocaleString()}</p>
        </div>
        <div className="glass-panel rounded-lg p-3 text-center">
          <div className="flex items-center justify-center gap-1.5 mb-1">
            <Activity className="w-3 h-3 text-neon-cyan" />
            <span className="text-[9px] text-muted-foreground uppercase">Active</span>
          </div>
          <p className="text-base font-semibold font-mono text-foreground">{activeNodes}%</p>
        </div>
      </div>
    </div>
  )
}

