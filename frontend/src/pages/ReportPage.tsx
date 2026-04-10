import { DashboardLayout } from "@/components/DashboardLayout";
import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

type ReportData = {
  main_problem?: string;
  key_insight?: string;
  strategy?: { title?: string; points?: string[] };
  whats_happening?: string[];
  root_causes?: string[];
  action_plan?: { step?: number; title?: string; description?: string; timeline?: string }[];
  campaign_plan?: { offer?: string; message?: string; channels?: string[]; goal?: string };
  confidence_score?: number;
};

type StoredReport = {
  report_id: string;
  created_at: string;
  title: string;
  confidence_score: number;
  saved?: boolean;
  data?: ReportData;
  error?: string;
};

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-card rounded-2xl p-5 shadow-premium border border-border">
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
  const list = Array.isArray(items) ? items.filter((x): x is string => typeof x === "string" && x.trim().length > 0) : [];
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

export default function ReportPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams();

  const API_BASE =
    (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://127.0.0.1:8000";

  const reportId = useMemo(() => {
    const state = location.state as { reportId?: string } | null;
    return state?.reportId || id || null;
  }, [id, location.state]);

  const [report, setReport] = useState<StoredReport | null>(null);
  const [loading, setLoading] = useState(true);

  const [mode, setMode] = useState<"fast" | "ai">("fast");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiText, setAiText] = useState<string>("");

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setReport(null);
    setAiLoading(false);
    setAiText("");

    if (!reportId) {
      fetch(`${API_BASE}/api/reports`, { signal: controller.signal })
        .then(async (res) => {
          if (!res.ok) throw new Error(`Request failed (${res.status})`);
          return res.json();
        })
        .then((list) => {
          const latestId = Array.isArray(list) ? (list[0]?.report_id as string | undefined) : undefined;
          if (latestId) navigate(`/report/${latestId}`, { replace: true });
          else setLoading(false);
        })
        .catch(() => setLoading(false));
      return () => controller.abort();
    }

    fetch(`${API_BASE}/api/reports/${reportId}`, { signal: controller.signal })
      .then(async (res) => {
        if (!res.ok) throw new Error(`Request failed (${res.status})`);
        return res.json();
      })
      .then((data) => {
        const stored = data as StoredReport;
        console.log("REAL BACKEND DATA:", stored);
        setReport(stored);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    return () => controller.abort();
  }, [API_BASE, navigate, reportId]);

  useEffect(() => {
    if (!report || report.error) return;
    if (mode !== "ai") {
      setAiLoading(false);
      setAiText("");
      return;
    }

    const data = report.data || {};
    const controller = new AbortController();
    let active = true;

    setAiLoading(true);
    setAiText("");

    fetch(`${API_BASE}/api/format-report`, {
      method: "POST",
      signal: controller.signal,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data }),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(`Request failed (${res.status})`);
        return res.json();
      })
      .then((payload) => {
        const text = payload?.formatted_text;
        if (active && typeof text === "string") setAiText(text);
      })
      .catch(() => {
        // Fallback: keep fast-mode cards (no fabricated content)
        if (active) setAiText("");
      })
      .finally(() => {
        if (active) setAiLoading(false);
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [API_BASE, mode, report]);

  const handleDownload = () => {
    if (!report?.report_id) return;
    window.open(`${API_BASE}/api/reports/${report.report_id}/pdf`);
  };

  const handleShare = async () => {
    if (!report?.report_id) return;
    const res = await fetch(`${API_BASE}/api/reports/${report.report_id}/share`, {
      method: "POST",
    });

    const data = await res.json();
    const fullUrl = window.location.origin + data.share_url;

    await navigator.clipboard.writeText(fullUrl);
    alert("Link copied!");
  };

  if (loading) {
    return (
      <DashboardLayout showRight={false}>
        <div className="p-8 text-sm text-muted-foreground">Loading report...</div>
      </DashboardLayout>
    );
  }

  if (!report || report.error) {
    return (
      <DashboardLayout showRight={false}>
        <div className="p-8 space-y-3">
          <div className="text-lg font-bold text-foreground">Report not found</div>
          <button onClick={() => navigate("/history")} className="text-sm font-medium text-primary hover:underline">
            Back to history
          </button>
        </div>
      </DashboardLayout>
    );
  }

  const data = report.data || {};
  const strategyPoints = data.strategy?.points || [];
  const actionPlan = data.action_plan || [];
  const campaign = data.campaign_plan || {};

  return (
    <DashboardLayout showRight={false}>
      <div className="p-8 space-y-6">
        <div>
          <h1 className="text-[26px] font-bold text-foreground tracking-tight">{data.main_problem || report.title}</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Confidence: {data.confidence_score ?? report.confidence_score}%
          </p>
        </div>

        <div className="flex gap-3 mb-2 flex-wrap">
          <button
            onClick={() => setMode("fast")}
            className={`px-3 py-2 rounded-md border text-sm ${
              mode === "fast" ? "border-primary bg-primary text-primary-foreground" : "border-border hover:bg-accent"
            }`}
          >
            ⚡ Fast
          </button>
          <button
            onClick={() => setMode("ai")}
            className={`px-3 py-2 rounded-md border text-sm ${
              mode === "ai" ? "border-primary bg-primary text-primary-foreground" : "border-border hover:bg-accent"
            }`}
          >
            🤖 AI
          </button>
          <button onClick={handleDownload} className="px-3 py-2 rounded-md border border-border hover:bg-accent text-sm">
            📄 PDF
          </button>
          <button onClick={handleShare} className="px-3 py-2 rounded-md border border-border hover:bg-accent text-sm">
            🔗 Share
          </button>
          {mode === "ai" && aiLoading ? (
            <span className="px-3 py-2 text-xs text-muted-foreground">Enhancing report with AI...</span>
          ) : null}
        </div>

        {mode === "ai" && aiText.trim() ? (
          <div className="bg-card rounded-2xl p-5 shadow-premium border border-border">
            <h3 className="text-sm font-bold text-foreground">AI Enhanced Report</h3>
            <div className="mt-3 text-sm text-foreground whitespace-pre-wrap leading-relaxed">{aiText}</div>
          </div>
        ) : null}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Main Problem">
            <TextValue value={data.main_problem} />
          </Card>

          <Card title="Key Insight">
            <TextValue value={data.key_insight} />
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
                    <div className="font-medium">{typeof step?.title === "string" ? step.title : "—"}</div>
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
                  {Array.isArray(campaign?.channels) && campaign.channels.length > 0
                    ? campaign.channels.join(", ")
                    : "—"}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Offer</div>
                <div className="text-foreground">{typeof campaign?.offer === "string" && campaign.offer.trim() ? campaign.offer : "—"}</div>
              </div>
            </div>
          </Card>

          <Card title="Confidence">
            <TextValue value={data.confidence_score ?? report.confidence_score} />
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}

