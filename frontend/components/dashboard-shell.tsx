'use client'

import { ReactNode } from 'react'
import { CommandSidebar } from '../components/command-sidebar'
import { IntelligenceFeed } from '../components/intelligence-feed'

export function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />
        <div className="absolute inset-0 grid-pattern opacity-30" />
        <div className="absolute top-1/2 left-1/2 h-[800px] w-[800px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/5 blur-3xl" />
      </div>

      <CommandSidebar />

      <main className="relative flex-1 overflow-y-auto">{children}</main>

      <IntelligenceFeed />
    </div>
  )
}
