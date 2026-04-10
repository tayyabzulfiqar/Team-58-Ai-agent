import { DashboardLayout } from "@/components/DashboardLayout";
import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

type StoredReport = {
  report_id: string;
  created_at: string;
  title: string;
  confidence_score: number;
  saved?: boolean;
  data?: ReportData;
  error?: string;
};

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

export default function ReportPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams();

  const reportId = useMemo(() => {
    if (id) return id;
    const state = location.state as { reportId?: string } | null;
    return state?.reportId || null;
  }, [id, location.state]);

  const [report, setReport] = useState<StoredReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const base = (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://127.0.0.1:8000";
    const controller = new AbortController();

    setLoading(true);

    if (!reportId) {
      fetch(`${base}/api/reports`, { signal: controller.signal })
        .then(async (res) => {
          if (!res.ok) throw new Error(`Request failed (${res.status})`);
          const data = await res.json();
          if (!Array.isArray(data) || data.length === 0 || !data[0]?.report_id) throw new Error("No reports yet");
          return data[0].report_id as string;
        })
        .then((latestId) => navigate(`/report/${latestId}`, { replace: true }))
        .catch(() => setLoading(false));
      return () => controller.abort();
    }

    fetch(`${base}/api/reports/${reportId}`, { signal: controller.signal })
      .then((res) => res.json())
      .then((data) => {
        setReport(data as StoredReport);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    return () => controller.abort();
  }, [navigate, reportId]);

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
          <button
            onClick={() => navigate("/history")}
            className="text-sm font-medium text-primary hover:underline"
          >
            Back to history
          </button>
        </div>
      </DashboardLayout>
    );
  }

  const data = report.data || {};

  return (
    <DashboardLayout showRight={false}>
      <div className="p-8 space-y-7">
        <div>
          <h1 className="text-[26px] font-bold text-foreground tracking-tight">{data.main_problem || report.title}</h1>
          <p className="text-sm text-muted-foreground mt-1">Confidence: {data.confidence_score ?? report.confidence_score}%</p>
        </div>

        <section className="bg-card rounded-2xl p-6 border border-border">
          <h2 className="text-sm font-bold text-foreground">Key Insight</h2>
          <p className="text-sm text-muted-foreground mt-2">{data.key_insight || "—"}</p>
        </section>

        <section className="grid grid-cols-2 gap-5">
          <div className="bg-card rounded-2xl p-6 border border-border">
            <h2 className="text-sm font-bold text-foreground">Strategy</h2>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground list-disc pl-5">
              {(data.strategy?.points || []).map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </div>
          <div className="bg-card rounded-2xl p-6 border border-border">
            <h2 className="text-sm font-bold text-foreground">What’s Happening</h2>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground list-disc pl-5">
              {(data.whats_happening || []).map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </div>
        </section>

        <section className="grid grid-cols-2 gap-5">
          <div className="bg-card rounded-2xl p-6 border border-border">
            <h2 className="text-sm font-bold text-foreground">Root Causes</h2>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground list-disc pl-5">
              {(data.root_causes || []).map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
          <div className="bg-card rounded-2xl p-6 border border-border">
            <h2 className="text-sm font-bold text-foreground">Campaign Plan</h2>
            <p className="text-sm text-muted-foreground mt-2">{data.campaign_plan?.message || "—"}</p>
            <p className="text-xs text-muted-foreground mt-3">{data.campaign_plan?.goal || ""}</p>
          </div>
        </section>

        <section className="bg-card rounded-2xl p-6 border border-border">
          <h2 className="text-sm font-bold text-foreground">Action Plan</h2>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground list-disc pl-5">
            {(data.action_plan || []).map((a, i) => (
              <li key={i}>
                {(a.title || "Step")} — {a.timeline || ""}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </DashboardLayout>
  );
}

