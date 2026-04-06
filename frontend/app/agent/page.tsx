import Link from 'next/link'
import { Activity, ArrowRight, Brain, Cpu, Megaphone, Search, Target } from 'lucide-react'
import { DashboardShell } from '../../components/dashboard-shell'
import { agents } from '../../lib/mock-data'
import { cn } from '../../lib/utils'

const iconByAgent = {
  research: Search,
  processing: Cpu,
  intelligence: Brain,
  decision: Target,
  campaign: Megaphone,
} as const

export default function AgentIndexPage() {
  return (
    <DashboardShell>
      <div className="p-6 md:p-10">
        <div className="mx-auto max-w-6xl space-y-8">
          <header className="space-y-2">
            <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">
              Team58 AI System
            </p>
            <h1 className="text-3xl font-semibold">Agent Network</h1>
            <p className="text-sm text-muted-foreground">
              Inspect each production agent through direct, deployment-safe routes.
            </p>
          </header>

          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {agents.map((agent) => {
              const Icon = iconByAgent[agent.id as keyof typeof iconByAgent] ?? Activity

              return (
                <Link
                  key={agent.id}
                  href={`/agent/${agent.id}`}
                  className="rounded-2xl border border-border bg-card p-6 transition hover:border-primary/40 hover:bg-card/90"
                >
                  <div className="mb-4 flex items-start justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                        <Icon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <h2 className="font-semibold text-foreground">{agent.name}</h2>
                        <p className="text-xs font-mono uppercase tracking-wide text-muted-foreground">
                          {agent.shortName}
                        </p>
                      </div>
                    </div>

                    <span
                      className={cn(
                        'rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide',
                        agent.status === 'active' && 'bg-neon-green/15 text-neon-green',
                        agent.status === 'processing' && 'bg-neon-cyan/15 text-neon-cyan',
                        agent.status === 'idle' && 'bg-muted text-muted-foreground'
                      )}
                    >
                      {agent.status}
                    </span>
                  </div>

                  <p className="mb-4 text-sm text-muted-foreground">{agent.description}</p>

                  <div className="grid grid-cols-3 gap-3 text-sm">
                    <div className="rounded-xl bg-secondary/40 p-3">
                      <p className="text-xs uppercase tracking-wide text-muted-foreground">
                        Confidence
                      </p>
                      <p className="mt-1 font-semibold text-foreground">{agent.confidence}%</p>
                    </div>
                    <div className="rounded-xl bg-secondary/40 p-3">
                      <p className="text-xs uppercase tracking-wide text-muted-foreground">
                        Throughput
                      </p>
                      <p className="mt-1 font-semibold text-foreground">
                        {agent.metrics.throughput}
                      </p>
                    </div>
                    <div className="rounded-xl bg-secondary/40 p-3">
                      <p className="text-xs uppercase tracking-wide text-muted-foreground">
                        Accuracy
                      </p>
                      <p className="mt-1 font-semibold text-foreground">{agent.metrics.accuracy}%</p>
                    </div>
                  </div>

                  <div className="mt-5 flex items-center justify-between text-sm text-primary">
                    <span>Open agent details</span>
                    <ArrowRight className="h-4 w-4" />
                  </div>
                </Link>
              )
            })}
          </section>
        </div>
      </div>
    </DashboardShell>
  )
}

