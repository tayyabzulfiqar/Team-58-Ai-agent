'use client'

import { FormEvent, useState } from 'react'

type DecisionMeta = {
  selected_strategy?: string
  alternatives?: string[]
  reason?: string
  confidence?: number
  status?: string
}

type Campaign = {
  strategy?: string
  headline?: string
  hook?: string
  cta?: string
}

type RunSystemResponse = {
  best_campaign?: Campaign
  all_campaigns?: Campaign[]
  optimization_score?: number
  decision_meta?: DecisionMeta
}

const initialResponse: RunSystemResponse | null = null

export default function DashboardPage() {
  const [input, setInput] = useState('lead generation funnel optimization')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<RunSystemResponse | null>(initialResponse)

  const runSystem = async (event: FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/run-system', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input }),
      })

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }

      const data = (await response.json()) as RunSystemResponse
      setResult(data)
    } catch (err) {
      setResult(null)
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-background p-6 text-foreground md:p-10">
      <div className="mx-auto max-w-4xl space-y-8">
        <header className="space-y-2">
          <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">
            Team58 AI System
          </p>
          <h1 className="text-3xl font-semibold">Campaign Intelligence Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Run the full multi-agent pipeline and inspect the selected campaign strategy.
          </p>
        </header>

        <form
          onSubmit={runSystem}
          className="space-y-4 rounded-xl border border-border bg-card p-6"
        >
          <label className="block space-y-2">
            <span className="text-sm font-medium">Business Input</span>
            <input
              className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm outline-none"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="e.g. new startup brand launch"
              disabled={loading}
            />
          </label>

          <button
            type="submit"
            className="rounded-lg bg-primary px-5 py-3 text-sm font-medium text-primary-foreground transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loading || !input.trim()}
          >
            {loading ? 'Running system...' : 'Run System'}
          </button>
        </form>

        {error && (
          <section className="rounded-xl border border-red-500 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </section>
        )}

        {result && (
          <section className="grid gap-6 md:grid-cols-2">
            <article className="space-y-3 rounded-xl border border-border bg-card p-6">
              <h2 className="text-lg font-semibold">Best Campaign</h2>
              <p><span className="font-medium">Strategy:</span> {result.best_campaign?.strategy ?? 'N/A'}</p>
              <p><span className="font-medium">Headline:</span> {result.best_campaign?.headline ?? 'N/A'}</p>
              <p><span className="font-medium">Hook:</span> {result.best_campaign?.hook ?? 'N/A'}</p>
              <p><span className="font-medium">CTA:</span> {result.best_campaign?.cta ?? 'N/A'}</p>
              <p><span className="font-medium">Optimization Score:</span> {result.optimization_score ?? 'N/A'}</p>
            </article>

            <article className="space-y-3 rounded-xl border border-border bg-card p-6">
              <h2 className="text-lg font-semibold">Decision Meta</h2>
              <p><span className="font-medium">Selected Strategy:</span> {result.decision_meta?.selected_strategy ?? 'N/A'}</p>
              <p><span className="font-medium">Reason:</span> {result.decision_meta?.reason ?? 'N/A'}</p>
              <p><span className="font-medium">Confidence:</span> {result.decision_meta?.confidence ?? 'N/A'}</p>
              <p><span className="font-medium">Alternatives:</span> {result.decision_meta?.alternatives?.join(', ') ?? 'N/A'}</p>
              <p><span className="font-medium">Status:</span> {result.decision_meta?.status ?? 'N/A'}</p>
            </article>

            <article className="rounded-xl border border-border bg-card p-6 md:col-span-2">
              <h2 className="mb-4 text-lg font-semibold">All Campaign Options</h2>
              <div className="grid gap-4 md:grid-cols-3">
                {(result.all_campaigns ?? []).map((campaign) => (
                  <div key={campaign.strategy} className="rounded-lg border border-border p-4">
                    <p className="font-medium">{campaign.strategy}</p>
                    <p className="mt-2 text-sm">{campaign.headline}</p>
                    <p className="mt-2 text-sm text-muted-foreground">{campaign.hook}</p>
                  </div>
                ))}
              </div>
            </article>
          </section>
        )}
      </div>
    </main>
  )
}
