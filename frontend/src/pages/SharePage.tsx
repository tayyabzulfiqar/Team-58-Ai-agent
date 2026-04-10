import { DashboardLayout } from "@/components/DashboardLayout";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

type ReportData = {
  main_problem?: string;
  key_insight?: string;
  whats_happening?: string[];
  root_causes?: string[];
  reasoning?: { analysis?: string; why_this_problem?: string; impact_explanation?: string };
  scoring?: { severity?: number; opportunity?: number; confidence?: number };
  strategy?: { title?: string; points?: string[] };
  action_plan?: { step?: number; title?: string; timeline?: string; impact_score?: number; description?: string }[];
  campaign_plan?: { offer?: string; message?: string; channels?: string[]; goal?: string };
  confidence_score?: number;
};

type StoredReport = {
  report_id: string;
  created_at: string;
  title: string;
  confidence_score: number;
  status?: "processing" | "ready" | "error" | string;
  saved?: boolean;
  data?: ReportData;
  error?: string;
};

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-card rounded-2xl p-6 border border-border shadow-md hover:shadow-lg transition-shadow">
      <h3 className="text-sm font-bold text-foreground">{title}</h3>
      <div className="mt-3 text-sm text-muted-foreground">{children}</div>
    </div>
  );
}

function TextValue({ value }: { value: unknown }) {
  const v = typeof value === "string" ? value.trim() : "";
  return <span className="text-foreground">{v || "—"}</span>;
}

function ListValue({ items }: { items: unknown }) {
  const list = Array.isArray(items)
    ? items.filter((x): x is string => typeof x === "string" && x.trim().length > 0)
    : [];
  if (list.length === 0) return <span className="text-foreground">—</span>;
  return (
    <ul className="list-disc pl-5 space-y-1">
      {list.map((item, idx) => (
        <li key={idx} className="text-foreground">
          {item}
        </li>
      ))}
    </ul>
  );
}

const progressSteps = [
  "Researching market...",
  "Analyzing behavior...",
  "Building strategy...",
  "Generating report...",
];

function toBulletItems(value: unknown): string[] {
  if (typeof value !== "string") return [];
  const text = value.trim();
  if (!text) return [];
  const lines = text
    .split(/\n+/)
    .map((l) => l.trim())
    .filter(Boolean);
  if (lines.length > 1) return lines;
  return text
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export default function SharePage() {
  const { shareId } = useParams();
  const navigate = useNavigate();

  const API_BASE =
    (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://127.0.0.1:8000";

  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState<StoredReport | null>(null);
  const [progressStepIndex, setProgressStepIndex] = useState(0);

  useEffect(() => {
    if (!shareId) {
      setLoading(false);
      return;
    }
    const controller = new AbortController();
    let active = true;
    let pollTimer: number | null = null;
    const startedAt = Date.now();
    const maxWaitMs = 3 * 60 * 1000;

    setLoading(true);
    setReport(null);
    setProgressStepIndex(0);

    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/share/${shareId}`, { signal: controller.signal });
        if (!res.ok) throw new Error(`Request failed (${res.status})`);
        const data = (await res.json()) as StoredReport;
        if (!active) return;
        console.log("REAL BACKEND DATA:", data);
        setReport(data);
        if (data?.status === "processing" && Date.now() - startedAt < maxWaitMs) {
          setLoading(true);
          pollTimer = window.setTimeout(poll, 1500);
        } else {
          setLoading(false);
        }
      } catch {
        if (!active) return;
        setLoading(false);
      }
    };

    poll();

    return () => {
      active = false;
      if (pollTimer) window.clearTimeout(pollTimer);
      controller.abort();
    };
  }, [API_BASE, shareId]);

  useEffect(() => {
    const showOverlay = loading || report?.status === "processing";
    if (!showOverlay) return;
    const interval = window.setInterval(() => setProgressStepIndex((s) => s + 1), 1000);
    return () => window.clearInterval(interval);
  }, [loading, report?.status]);

  if (!loading && (!report || report.error || report.status === "error")) {
    return (
      <DashboardLayout showRight={false}>
        <div className="p-8 space-y-3">
          <div className="text-lg font-bold text-foreground">Shared report not found</div>
          <button onClick={() => navigate("/")} className="text-sm font-medium text-primary hover:underline">
            Go home
          </button>
        </div>
      </DashboardLayout>
    );
  }

  const data = report?.data || {};
  const strategyPoints = data.strategy?.points || [];
  const actionPlan = data.action_plan || [];
  const campaign = data.campaign_plan || {};
  const reasoning = data.reasoning || {};
  const scoring = data.scoring || {};
  const currentOverlayStep = progressSteps[progressStepIndex % progressSteps.length];
  const confidenceValue =
    typeof data.confidence_score === "number"
      ? data.confidence_score
      : typeof report?.confidence_score === "number"
        ? report?.confidence_score
        : null;

  return (
    <DashboardLayout showRight={false}>
      <div className="p-8 space-y-6">
        {loading || report?.status === "processing" ? (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-6 z-50">
            <div className="w-full max-w-md bg-card rounded-2xl border border-border shadow-xl p-6">
              <div className="text-center">
                <div className="w-14 h-14 rounded-2xl gradient-primary flex items-center justify-center mx-auto font-bold text-primary-foreground text-lg">
                  58
                </div>
                <h2 className="mt-4 text-xl font-bold text-foreground tracking-tight">
                  AI agents are analyzing this report...
                </h2>
                <p className="mt-2 text-xs text-muted-foreground">{currentOverlayStep}</p>
              </div>
              <div className="mt-6 space-y-3">
                <div className="h-2 bg-accent rounded-full overflow-hidden">
                  <div
                    className="h-full gradient-primary transition-all duration-700"
                    style={{
                      width: `${((progressStepIndex % progressSteps.length) + 1) * (100 / progressSteps.length)}%`,
                    }}
                  />
                </div>
                <div className="text-xs text-muted-foreground">Loading shared dashboard as soon as results are ready.</div>
              </div>
            </div>
          </div>
        ) : null}

        <div className="flex items-start justify-between gap-6">
          <div>
            <h1 className="text-[26px] font-bold text-foreground tracking-tight">
              {data.main_problem || report?.title || "Shared report"}
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Confidence: <span className="text-foreground">{confidenceValue === null ? "—" : `${confidenceValue}%`}</span>
            </p>
          </div>
          <button
            onClick={() => report?.report_id && navigate(`/report/${report.report_id}`)}
            className="px-3 py-2 rounded-md border border-border hover:bg-accent text-sm"
          >
            Open in app
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Main Problem">
            <TextValue value={data.main_problem} />
          </Card>

          <Card title="Key Insight">
            <TextValue value={data.key_insight} />
          </Card>

          <Card title="Reasoning">
            <div className="space-y-4">
              {[
                { label: "Analysis", value: reasoning.analysis },
                { label: "Why this problem", value: reasoning.why_this_problem },
                { label: "Impact if ignored", value: reasoning.impact_explanation },
              ].map((row) => {
                const bullets = toBulletItems(row.value);
                return (
                  <div key={row.label}>
                    <div className="text-xs text-muted-foreground">{row.label}</div>
                    {bullets.length > 0 ? (
                      <ul className="mt-1 list-disc pl-5 space-y-1">
                        {bullets.map((b, idx) => (
                          <li key={idx} className="text-foreground">
                            {b}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <div className="text-foreground">—</div>
                    )}
                  </div>
                );
              })}
            </div>
          </Card>

          <Card title="Scoring">
            <div className="space-y-2 text-foreground">
              <div>Severity: {typeof scoring.severity === "number" ? `${scoring.severity}%` : "—"}</div>
              <div>Opportunity: {typeof scoring.opportunity === "number" ? `${scoring.opportunity}%` : "—"}</div>
              <div>
                Confidence:{" "}
                {typeof scoring.confidence === "number"
                  ? `${scoring.confidence}%`
                  : typeof data.confidence_score === "number"
                    ? `${data.confidence_score}%`
                    : "—"}
              </div>
            </div>
          </Card>

          <Card title="Strategy">
            <ListValue items={strategyPoints} />
          </Card>

          <Card title="What's Happening">
            <ListValue items={data.whats_happening} />
          </Card>

          <Card title="Root Causes">
            <ListValue items={data.root_causes} />
          </Card>

          <Card title="Action Plan">
            {Array.isArray(actionPlan) && actionPlan.length > 0 ? (
              <ol className="list-decimal pl-5 space-y-2">
                {actionPlan.map((step, idx) => (
                  <li key={idx} className="text-foreground">
                    <div className="font-medium">
                      {typeof step?.title === "string" && step.title.trim() ? step.title : "—"}
                      {typeof step?.impact_score === "number" ? (
                        <span className="text-xs text-muted-foreground ml-2">(Impact: {step.impact_score}%)</span>
                      ) : null}
                    </div>
                    <div className="text-xs text-muted-foreground mt-0.5">
                      {typeof step?.timeline === "string" ? step.timeline : ""}
                    </div>
                    {typeof step?.description === "string" && step.description.trim() ? (
                      <div className="text-xs text-muted-foreground mt-1">{step.description}</div>
                    ) : null}
                  </li>
                ))}
              </ol>
            ) : (
              <span className="text-foreground">—</span>
            )}
          </Card>

          <Card title="Campaign Plan">
            <div className="space-y-2">
              <div>
                <div className="text-xs text-muted-foreground">Message</div>
                <div className="text-foreground">{typeof campaign?.message === "string" && campaign.message.trim() ? campaign.message : "—"}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Goal</div>
                <div className="text-foreground">{typeof campaign?.goal === "string" && campaign.goal.trim() ? campaign.goal : "—"}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Channels</div>
                <div className="text-foreground">
                  {Array.isArray(campaign?.channels) && campaign.channels.length > 0 ? campaign.channels.join(", ") : "—"}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Offer</div>
                <div className="text-foreground">{typeof campaign?.offer === "string" && campaign.offer.trim() ? campaign.offer : "—"}</div>
              </div>
            </div>
          </Card>

          <Card title="Confidence (Legacy)">
            <TextValue value={data.confidence_score ?? report?.confidence_score} />
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
