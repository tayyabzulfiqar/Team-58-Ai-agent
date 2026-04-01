import { CommandSidebar } from '@/components/command-sidebar'
import { IntelligenceFeed } from '@/components/intelligence-feed'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Background effects */}
      <div className="fixed inset-0 pointer-events-none">
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />
        
        {/* Grid pattern */}
        <div className="absolute inset-0 grid-pattern opacity-30" />
        
        {/* Radial glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-primary/5 blur-3xl" />
      </div>

      {/* Sidebar */}
      <CommandSidebar />

      {/* Main content */}
      <main className="flex-1 overflow-y-auto relative">
        {children}
      </main>

      {/* Intelligence Feed */}
      <IntelligenceFeed />
    </div>
  )
}
