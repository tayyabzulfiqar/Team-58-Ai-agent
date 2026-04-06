'use client'

import { FormEvent, useState } from 'react'
import { runSystem } from '@/lib/api'
import { type RunSystemResponse } from '@/lib/system-run'
import { useSystemRun } from './system-run-provider'

export function DashboardHome() {
  const [input, setInput] = useState('lead generation funnel optimization')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<RunSystemResponse | null>(null)
  const { setLatestRunFromResponse } = useSystemRun()

  const handleRun = async (event: FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const payload = (await runSystem({ query: input })) as RunSystemResponse & {
        error?: string
      }

      console.log('API RESPONSE:', payload)

      if (payload?.error) {
        throw new Error(payload.error)
      }

      setResult(payload)
      setLatestRunFromResponse(payload)
    } catch (err) {
      setResult(null)
      setLatestRunFromResponse({ data: null })
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const runData = result?.data

  return (
    <div className="p-6 md:p-10">
      <div className="mx-auto max-w-4xl space-y-8">
        <header className="space-y-2">
          <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">
            Team 58 AI System
          </p>
          <h1 className="text-3xl font-semibold">Campaign Intelligence Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Run the full multi-agent pipeline and inspect the selected campaign
            strategy.
          </p>
        </header>

        <form
          onSubmit={handleRun}
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

        {runData && (
          <section className="grid gap-6 md:grid-cols-2">
            <article className="space-y-3 rounded-xl border border-border bg-card p-6">
              <h2 className="text-lg font-semibold">Best Campaign</h2>
              <p>
                <span className="font-medium">Insight:</span>{' '}
                {runData.insight ?? 'N/A'}
              </p>
              <p>
                <span className="font-medium">Strategy:</span>{' '}
                {runData.best_campaign?.strategy ?? 'N/A'}
              </p>
              <p>
                <span className="font-medium">Headline:</span>{' '}
                {runData.best_campaign?.headline ?? 'N/A'}
              </p>
              <p>
                <span className="font-medium">Hook:</span>{' '}
                {runData.best_campaign?.hook ?? 'N/A'}
              </p>
              <p>
                <span className="font-medium">CTA:</span>{' '}
                {runData.best_campaign?.cta ?? 'N/A'}
              </p>
              <p>
                <span className="font-medium">Optimization Score:</span>{' '}
                {runData.optimization_score ?? 'N/A'}
              </p>
            </article>

            <article className="space-y-3 rounded-xl border border-border bg-card p-6">
              <h2 className="text-lg font-semibold">Decision Meta</h2>
              <p>
                <span className="font-medium">Summary:</span>{' '}
                {runData.summary ?? result?.message ?? 'N/A'}
              </p>
              <p>
                <span className="font-medium">Selected Strategy:</span>{' '}
                {runData.decision_meta?.selected_strategy ?? 'N/A'}
              </p>
              <p>
                <span className="font-medium">Reason:</span>{' '}
                {runData.decision_meta?.reason ?? 'N/A'}
              </p>
              <p>
                <span className="font-medium">Confidence:</span>{' '}
                {runData.decision_meta?.confidence ?? 'N/A'}
              </p>
              <p>
                <span className="font-medium">Alternatives:</span>{' '}
                {runData.decision_meta?.alternatives?.join(', ') ?? 'N/A'}
              </p>
              <p>
                <span className="font-medium">Status:</span>{' '}
                {runData.decision_meta?.status ?? 'N/A'}
              </p>
              {runData.simulated && (
                <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700">
                  Backend simulation mode is active. {runData.error ?? 'A live fallback was used.'}
                </p>
              )}
            </article>

            <article className="rounded-xl border border-border bg-card p-6 md:col-span-2">
              <h2 className="mb-4 text-lg font-semibold">All Campaign Options</h2>
              <div className="grid gap-4 md:grid-cols-3">
                {(runData.all_campaigns ?? []).map((campaign, index) => (
                  <div
                    key={`${campaign.strategy ?? 'campaign'}-${index}`}
                    className="rounded-lg border border-border p-4"
                  >
                    <p className="font-medium">{campaign.strategy}</p>
                    <p className="mt-2 text-sm">{campaign.headline}</p>
                    <p className="mt-2 text-sm text-muted-foreground">
                      {campaign.hook}
                    </p>
                  </div>
                ))}
              </div>
            </article>
          </section>
        )}
      </div>
    </div>
  )
}
