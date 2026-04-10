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

export default function SharePage() {
  const { shareId } = useParams();
  const navigate = useNavigate();

  const API_BASE =
    (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://127.0.0.1:8000";

  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState<StoredReport | null>(null);

  useEffect(() => {
    if (!shareId) {
      setLoading(false);
      return;
    }
    const controller = new AbortController();
    setLoading(true);
    setReport(null);

    fetch(`${API_BASE}/api/share/${shareId}`, { signal: controller.signal })
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
  }, [API_BASE, shareId]);

  if (loading) {
    return (
      <DashboardLayout showRight={false}>
        <div className="p-8 text-sm text-muted-foreground">Loading shared report...</div>
      </DashboardLayout>
    );
  }

  if (!report || report.error) {
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

  const data = report.data || {};
  const strategyPoints = data.strategy?.points || [];
  const actionPlan = data.action_plan || [];
  const campaign = data.campaign_plan || {};
  const reasoning = data.reasoning || {};
  const scoring = data.scoring || {};

  return (
    <DashboardLayout showRight={false}>
      <div className="p-8 space-y-6">
        <div className="flex items-start justify-between gap-6">
          <div>
            <h1 className="text-[26px] font-bold text-foreground tracking-tight">{data.main_problem || report.title}</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Confidence: {data.confidence_score ?? report.confidence_score}%
            </p>
          </div>
          <button
            onClick={() => navigate(`/report/${report.report_id}`)}
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
            <div className="space-y-3">
              <div>
                <div className="text-xs text-muted-foreground">Analysis</div>
                <div className="text-foreground">
                  {typeof reasoning.analysis === "string" && reasoning.analysis.trim() ? reasoning.analysis : "—"}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Why this problem</div>
                <div className="text-foreground">
                  {typeof reasoning.why_this_problem === "string" && reasoning.why_this_problem.trim()
                    ? reasoning.why_this_problem
                    : "—"}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Impact if ignored</div>
                <div className="text-foreground">
                  {typeof reasoning.impact_explanation === "string" && reasoning.impact_explanation.trim()
                    ? reasoning.impact_explanation
                    : "—"}
                </div>
              </div>
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
            <TextValue value={data.confidence_score ?? report.confidence_score} />
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}

