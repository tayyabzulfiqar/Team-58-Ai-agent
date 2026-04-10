import { DashboardLayout } from "@/components/DashboardLayout";
import { formatReport, type ReportData } from "@/lib/reportFormatter";
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

// ReportData type lives in `src/lib/reportFormatter.ts`

export default function ReportPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams();

  const API_BASE =
    (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://127.0.0.1:8000";

  const reportId = useMemo(() => {
    if (id) return id;
    const state = location.state as { reportId?: string } | null;
    return state?.reportId || null;
  }, [id, location.state]);

  const [report, setReport] = useState<StoredReport | null>(null);
  const [loading, setLoading] = useState(true);

  const [mode, setMode] = useState<"fast" | "ai">("fast");
  const [aiLoading, setAiLoading] = useState(false);
  const [formattedReport, setFormattedReport] = useState<string>("");

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setReport(null);
    setFormattedReport("");
    setAiLoading(false);

    if (!reportId) {
      fetch(`${API_BASE}/api/reports`, { signal: controller.signal })
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

    fetch(`${API_BASE}/api/reports/${reportId}`, { signal: controller.signal })
      .then(async (res) => {
        if (!res.ok) throw new Error(`Request failed (${res.status})`);
        return res.json();
      })
      .then((data) => {
        const stored = data as StoredReport;
        setReport(stored);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    return () => controller.abort();
  }, [API_BASE, navigate, reportId]);

  useEffect(() => {
    if (!report || report.error) return;
    const data = report.data || {};

    if (mode === "fast") {
      setAiLoading(false);
      setFormattedReport(formatReport(data));
      return;
    }

    const controller = new AbortController();
    let active = true;
    setAiLoading(true);

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
        if (typeof text === "string" && text.trim().length > 0) {
          if (active) setFormattedReport(text);
        } else {
          if (active) setFormattedReport(formatReport(data));
        }
      })
      .catch(() => {
        if (active) setFormattedReport(formatReport(data));
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

  return (
    <DashboardLayout showRight={false}>
      <div className="p-8 space-y-7">
        <div className="flex items-start justify-between gap-6">
          <div>
            <h1 className="text-[26px] font-bold text-foreground tracking-tight">{data.main_problem || report.title}</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Confidence: {data.confidence_score ?? report.confidence_score}%
            </p>
          </div>
        </div>

        <section className="bg-card rounded-2xl p-6 border border-border">
          <div className="flex gap-3 mb-4">
            <button
              onClick={() => setMode("fast")}
              className="px-3 py-2 rounded-md border border-border hover:bg-accent text-sm"
            >
              ⚡ Fast
            </button>
            <button
              onClick={() => setMode("ai")}
              className="px-3 py-2 rounded-md border border-border hover:bg-accent text-sm"
            >
              🤖 AI
            </button>
            <button
              onClick={handleDownload}
              className="px-3 py-2 rounded-md border border-border hover:bg-accent text-sm"
            >
              📄 PDF
            </button>
            <button
              onClick={handleShare}
              className="px-3 py-2 rounded-md border border-border hover:bg-accent text-sm"
            >
              🔗 Share
            </button>
          </div>

          <div className="flex items-center justify-between gap-4">
            <h2 className="text-sm font-bold text-foreground">Report</h2>
            {mode === "ai" && aiLoading ? (
              <span className="text-xs text-muted-foreground">Enhancing report with AI...</span>
            ) : null}
          </div>
          <div className="mt-4 text-sm text-foreground whitespace-pre-wrap leading-relaxed">
            {formattedReport || formatReport(data)}
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}
