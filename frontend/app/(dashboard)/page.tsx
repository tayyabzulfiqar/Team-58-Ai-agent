'use client'

import { useEffect, useState } from 'react'
import { API_BASE_URL } from '@/src/config/api'

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
export default function DashboardPage() {
  const [data, setData] = useState<RunSystemResponse>(emptyState)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [product, setProduct] = useState('')
  const [audience, setAudience] = useState('')
  const [campaignResult, setCampaignResult] = useState<any>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<any>(null)

  // Optionally keep the original pipeline button
  const runSystem = async () => {
    setLoading(true)
    setError(null)
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
      setError('Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  // Campaign form submit handler
  const handleCampaignSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setCampaignResult(null)
    setAnalysisResult(null)
    try {
      const res = await fetch(`${API_BASE_URL}/run-campaign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product, audience })
      })
      if (!res.ok) throw new Error('API error')
      const data = await res.json()
      if (data.status !== 'success') throw new Error(data.message || 'API error')
      setCampaignResult(data.data)
    } catch (err) {
      setError('Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  // Analyze button handler
  const handleAnalyze = async () => {
    if (!campaignResult) return
    setAnalyzing(true)
    setError(null)
    setAnalysisResult(null)
    try {
      const res = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ campaign_data: campaignResult })
      })
      if (!res.ok) throw new Error('API error')
      const data = await res.json()
      if (data.status !== 'success') throw new Error(data.message || 'API error')
      setAnalysisResult(data.data)
    } catch (err) {
      setError('Something went wrong')
    } finally {
      setAnalyzing(false)
    }
  }
        campaigns: Array.isArray(result.campaigns) ? result.campaigns : [],
  return (
    <main className="min-h-screen bg-background text-foreground p-6 md:p-10">
      <div className="mx-auto max-w-3xl space-y-8">
        <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="space-y-2">
            <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">
              Campaign Generator
            </p>
            <h1 className="text-3xl font-semibold">AI Campaign System</h1>
            <p className="text-sm text-muted-foreground">
              Instantly generate and analyze campaign ideas
            </p>
          </div>
        </header>

        <form onSubmit={handleCampaignSubmit} className="rounded-xl border border-border bg-card p-6 flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Product/Service</label>
            <input
              className="w-full rounded border px-3 py-2 text-base"
              value={product}
              onChange={e => setProduct(e.target.value)}
              required
              minLength={3}
              placeholder="e.g. AI Marketing Platform"
              disabled={loading}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Target Audience</label>
            <input
              className="w-full rounded border px-3 py-2 text-base"
              value={audience}
              onChange={e => setAudience(e.target.value)}
              required
              minLength={3}
              placeholder="e.g. Small Business Owners"
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            className="rounded-lg bg-primary px-5 py-3 text-sm font-medium text-primary-foreground transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Generate Campaign'}
          </button>
        </form>

        {error && (
          <div className="rounded-xl border border-red-500 bg-red-100 p-4 text-red-700">
            {error}
          </div>
        )}

        {campaignResult && (
          <section className="rounded-xl border border-border bg-card p-6 mt-4">
            <h2 className="text-lg font-semibold mb-2">Campaign Result</h2>
            <div className="space-y-2">
              <div><span className="font-medium">Idea:</span> {campaignResult.campaign_idea}</div>
              <div><span className="font-medium">Headline:</span> {campaignResult.headline}</div>
              <div><span className="font-medium">Ad Copy:</span> {campaignResult.ad_copy}</div>
              <div><span className="font-medium">CTA:</span> {campaignResult.cta}</div>
            </div>
            <button
              onClick={handleAnalyze}
              className="mt-4 rounded-lg bg-secondary px-5 py-2 text-sm font-medium text-secondary-foreground transition hover:bg-secondary/90 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={analyzing}
            >
              {analyzing ? 'Analyzing...' : 'Analyze Campaign'}
            </button>
          </section>
        )}

        {analysisResult && (
          <section className="rounded-xl border border-border bg-card p-6 mt-4">
            <h2 className="text-lg font-semibold mb-2">Analysis & Recommendations</h2>
            <pre className="whitespace-pre-wrap text-sm">{JSON.stringify(analysisResult, null, 2)}</pre>
          </section>
        )}
      </div>
    </main>
  )
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
