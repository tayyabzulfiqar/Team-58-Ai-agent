'use client'

import { createContext, ReactNode, useContext, useState } from 'react'
import {
  defaultAgentStates,
  defaultFeed,
  type AgentSnapshot,
  type FeedEntry,
  type RunSystemResponse,
  type SystemRunData,
} from '@/lib/system-run'

type SystemRunContextValue = {
  latestRun: SystemRunData | null
  setLatestRunFromResponse: (response: RunSystemResponse) => void
  agentStates: AgentSnapshot[]
  feedItems: FeedEntry[]
}

const SystemRunContext = createContext<SystemRunContextValue | null>(null)

export function SystemRunProvider({ children }: { children: ReactNode }) {
  const [latestRun, setLatestRun] = useState<SystemRunData | null>(null)

  const setLatestRunFromResponse = (response: RunSystemResponse) => {
    setLatestRun(response.data ?? null)
  }

  return (
    <SystemRunContext.Provider
      value={{
        latestRun,
        setLatestRunFromResponse,
        agentStates: latestRun?.agent_states?.length ? latestRun.agent_states : defaultAgentStates,
        feedItems: latestRun?.feed?.length ? latestRun.feed : defaultFeed,
      }}
    >
      {children}
    </SystemRunContext.Provider>
  )
}

export function useSystemRun() {
  const context = useContext(SystemRunContext)

  if (!context) {
    throw new Error('useSystemRun must be used within a SystemRunProvider')
  }

  return context
}
