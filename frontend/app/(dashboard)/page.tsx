'use client'

import { useEffect, useState } from 'react'

type ResearchLead = {
  title: string
  url: string
  snippet: string
  source: string
  query: string
}

type ProcessedLead = {
  name: string
  company: string
  website: string
  summary: string
  industry: string
  source: string
}

type AnalysisLead = {
  name: string
  company: string
  website: string
  score: number
  category: 'high' | 'medium' | 'low'
  summary: string
}

type CampaignLead = {
  name: string
  company: string
  website: string
  message: string
}

type RunSystemResponse = {
  status: string
  research: ResearchLead[]
  processed: ProcessedLead[]
  analysis: AnalysisLead[]
  campaigns: CampaignLead[]
}

const emptyState: RunSystemResponse = {
  status: 'success',
  research: [],
  processed: [],
  analysis: [],
  campaigns: [],
}

export default function DashboardPage() {
  const [data, setData] = useState<RunSystemResponse>(emptyState)
  const [loading, setLoading] = useState(false)

  const runSystem = async () => {
    setLoading(true)

    try {
      const response = await fetch('/api/run-system', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const result = (await response.json()) as Partial<RunSystemResponse>

      setData({
        status: result.status ?? 'success',
        research: Array.isArray(result.research) ? result.research : [],
        processed: Array.isArray(result.processed) ? result.processed : [],
        analysis: Array.isArray(result.analysis) ? result.analysis : [],
        campaigns: Array.isArray(result.campaigns) ? result.campaigns : [],
      })
    } catch {
      setData(emptyState)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void runSystem()
  }, [])

  return (
    <main className="min-h-screen bg-background text-foreground p-6 md:p-10">
      <div className="mx-auto max-w-7xl space-y-8">
        <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="space-y-2">
            <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">
              4-Agent Pipeline
            </p>
            <h1 className="text-3xl font-semibold">AI Lead System</h1>
            <p className="text-sm text-muted-foreground">
              Research Agent, Processing Agent, Analysis Agent, Campaign Design Agent
            </p>
          </div>

          <button
            onClick={runSystem}
            disabled={loading}
            className="rounded-lg bg-primary px-5 py-3 text-sm font-medium text-primary-foreground transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? 'Running AI agents...' : 'Run AI System'}
          </button>
        </header>

        {loading && (
          <section className="rounded-xl border border-border bg-card p-6">
            <p className="text-base font-medium">Running AI agents...</p>
          </section>
        )}

        <section className="grid gap-4 md:grid-cols-4">
          <div className="rounded-xl border border-border bg-card p-5">
            <p className="text-sm text-muted-foreground">Research count</p>
            <p className="mt-2 text-3xl font-semibold">{data.research.length}</p>
          </div>
          <div className="rounded-xl border border-border bg-card p-5">
            <p className="text-sm text-muted-foreground">Processed leads</p>
            <p className="mt-2 text-3xl font-semibold">{data.processed.length}</p>
          </div>
          <div className="rounded-xl border border-border bg-card p-5">
            <p className="text-sm text-muted-foreground">Analysis results</p>
            <p className="mt-2 text-3xl font-semibold">{data.analysis.length}</p>
          </div>
          <div className="rounded-xl border border-border bg-card p-5">
            <p className="text-sm text-muted-foreground">Campaign messages</p>
            <p className="mt-2 text-3xl font-semibold">{data.campaigns.length}</p>
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <div className="rounded-xl border border-border bg-card p-6">
            <h2 className="text-lg font-semibold">Research</h2>
            <div className="mt-4 space-y-4">
              {data.research.length === 0 && (
                <p className="text-sm text-muted-foreground">No research results.</p>
              )}
              {data.research.map((item) => (
                <article key={item.url} className="rounded-lg border border-border/70 p-4">
                  <p className="font-medium">{item.title}</p>
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-1 block text-sm text-primary underline underline-offset-4"
                  >
                    {item.url}
                  </a>
                  <p className="mt-2 text-sm text-muted-foreground">{item.snippet || 'No snippet available.'}</p>
                </article>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-6">
            <h2 className="text-lg font-semibold">Processed leads</h2>
            <div className="mt-4 space-y-4">
              {data.processed.length === 0 && (
                <p className="text-sm text-muted-foreground">No processed leads.</p>
              )}
              {data.processed.map((lead) => (
                <article key={lead.website} className="rounded-lg border border-border/70 p-4">
                  <p className="font-medium">{lead.name}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{lead.company}</p>
                  <p className="mt-2 text-sm">{lead.summary || 'No summary available.'}</p>
                </article>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-6">
            <h2 className="text-lg font-semibold">Analysis scores</h2>
            <div className="mt-4 space-y-4">
              {data.analysis.length === 0 && (
                <p className="text-sm text-muted-foreground">No analysis results.</p>
              )}
              {data.analysis.map((lead) => (
                <article key={lead.website} className="rounded-lg border border-border/70 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="font-medium">{lead.name}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{lead.company}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-semibold">{lead.score}</p>
                      <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                        {lead.category}
                      </p>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-6">
            <h2 className="text-lg font-semibold">Campaign messages</h2>
            <div className="mt-4 space-y-4">
              {data.campaigns.length === 0 && (
                <p className="text-sm text-muted-foreground">No campaign messages.</p>
              )}
              {data.campaigns.map((campaign) => (
                <article key={campaign.website} className="rounded-lg border border-border/70 p-4">
                  <p className="font-medium">{campaign.company}</p>
                  <p className="mt-2 text-sm">{campaign.message}</p>
                </article>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}
