import { DashboardLayout } from "@/components/DashboardLayout";
import { useLocation, useNavigate } from "react-router-dom";
import { FileText, ChevronRight, Clock } from "lucide-react";
import { useEffect, useState } from "react";

type ReportSummary = {
  report_id: string;
  title: string;
  confidence_score: number;
  created_at: string;
};

function getConfidenceColor(c: number) {
  if (c >= 85) return "text-success bg-success/10";
  if (c >= 75) return "text-primary bg-primary/10";
  return "text-warning bg-warning/10";
}

function formatDate(iso: string) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(d);
}

export default function HistoryPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const pageTitle = location.pathname === "/saved" ? "Saved Reports" : "Report History";

  useEffect(() => {
    const controller = new AbortController();
    const base = (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://127.0.0.1:8000";
    const path = location.pathname === "/saved" ? "/api/reports/saved" : "/api/reports";

    setLoading(true);
    setError(null);
    fetch(`${base}${path}`, { signal: controller.signal })
      .then(async (res) => {
        if (!res.ok) throw new Error(`Request failed (${res.status})`);
        const data = await res.json();
        if (!Array.isArray(data)) throw new Error("Invalid API response");
        return data as ReportSummary[];
      })
      .then((data) => setReports(data))
      .catch((e: unknown) => {
        if (e instanceof DOMException && e.name === "AbortError") return;
        setReports([]);
        setError(e instanceof Error ? e.message : "Failed to load reports");
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [location.pathname]);

  return (
    <DashboardLayout showRight={false}>
      <div className="p-8 space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <Clock className="h-6 w-6 text-primary" />
              <h1 className="text-[26px] font-bold text-foreground tracking-tight">{pageTitle}</h1>
            </div>
            <p className="text-sm text-muted-foreground ml-9">
              {loading ? "Loading..." : `${reports.length} report${reports.length === 1 ? "" : "s"}`}
            </p>
          </div>
        </div>
        <div className="space-y-3">
          {error ? (
            <div className="p-5 rounded-2xl bg-card border border-border text-sm text-muted-foreground">{error}</div>
          ) : null}

          {loading ? (
            <div className="p-5 rounded-2xl bg-card border border-border text-sm text-muted-foreground">Fetching reports...</div>
          ) : reports.length === 0 ? (
            <div className="p-5 rounded-2xl bg-card border border-border text-sm text-muted-foreground">
              No reports yet.
            </div>
          ) : (
            reports.map((r) => (
              <button
                key={r.report_id}
                onClick={() => navigate(`/report/${r.report_id}`)}
                className="w-full flex items-center gap-5 p-5 rounded-2xl bg-card border border-border shadow-[0_10px_30px_rgba(0,0,0,0.05)] hover:shadow-[0_16px_40px_rgba(0,0,0,0.08)] hover:-translate-y-0.5 hover:border-primary/20 transition-all duration-300 text-left group"
              >
                <div className="w-12 h-12 rounded-xl bg-primary/8 flex items-center justify-center shrink-0 group-hover:bg-primary/15 transition-colors">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-foreground text-[15px]">{r.title || "Report"}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{formatDate(r.created_at)}</p>
                </div>
                <span className={`text-sm font-bold px-3 py-1.5 rounded-lg ${getConfidenceColor(r.confidence_score)}`}>
                  {r.confidence_score}%
                </span>
                <ChevronRight className="h-5 w-5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-all duration-200" />
              </button>
            ))
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
