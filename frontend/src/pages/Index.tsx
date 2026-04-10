import { DashboardLayout } from "@/components/DashboardLayout";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, FileText, Bookmark, Search } from "lucide-react";

type ReportSummary = {
  report_id: string;
  title?: string;
  confidence_score?: number;
  created_at?: string;
};

const suggestions = [
  "Luxury gym in Dubai struggling with retention",
  "B2B SaaS trial-to-paid conversion is low",
  "E-commerce store has high checkout drop-off",
];

function formatTimestamp(ts: string | undefined): string {
  if (!ts) return "";
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return ts;
  return d.toLocaleString();
}

export default function HomePage() {
  const navigate = useNavigate();
  const API_BASE =
    (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://127.0.0.1:8000";

  const [query, setQuery] = useState("");
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [savedReports, setSavedReports] = useState<ReportSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);

    Promise.all([
      fetch(`${API_BASE}/api/reports`, { signal: controller.signal }).then((r) => (r.ok ? r.json() : [])),
      fetch(`${API_BASE}/api/reports/saved`, { signal: controller.signal }).then((r) => (r.ok ? r.json() : [])),
    ])
      .then(([all, saved]) => {
        setReports(Array.isArray(all) ? (all as ReportSummary[]) : []);
        setSavedReports(Array.isArray(saved) ? (saved as ReportSummary[]) : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    return () => controller.abort();
  }, [API_BASE]);

  const latest = useMemo(() => (reports.length > 0 ? reports[0] : null), [reports]);

  const handleGenerate = (q?: string) => {
    const value = (typeof q === "string" ? q : query).trim();
    if (!value) return;
    navigate("/processing", { state: { query: value } });
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div className="flex items-start justify-between gap-6 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold text-foreground tracking-tight">Business Intelligence Reports</h1>
            <p className="text-sm text-muted-foreground mt-1">Generate a report from a real backend analysis.</p>
          </div>
          <button
            onClick={() => navigate("/history")}
            className="px-3 py-2 rounded-md border border-border hover:bg-accent text-sm"
          >
            View history
          </button>
        </div>

        <div className="bg-card rounded-2xl border border-border shadow-premium p-5">
          <div className="flex items-center gap-3">
            <Search className="h-4 w-4 text-muted-foreground shrink-0" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
              placeholder="Describe your business challenge or goal..."
              className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground/60 outline-none"
            />
            <button
              onClick={() => handleGenerate()}
              className="px-3 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90"
            >
              Generate <ArrowRight className="inline-block h-3.5 w-3.5 ml-1" />
            </button>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => handleGenerate(s)}
                className="px-3 py-1.5 rounded-full border border-border hover:bg-accent text-xs text-foreground"
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-card rounded-2xl border border-border shadow-premium p-5 flex items-center gap-4">
            <div className="w-11 h-11 rounded-xl bg-accent flex items-center justify-center shrink-0">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div>
              <div className="text-xl font-bold text-foreground">{loading ? "—" : reports.length}</div>
              <div className="text-xs text-muted-foreground">Reports generated</div>
            </div>
          </div>

          <div className="bg-card rounded-2xl border border-border shadow-premium p-5 flex items-center gap-4">
            <div className="w-11 h-11 rounded-xl bg-accent flex items-center justify-center shrink-0">
              <Bookmark className="h-5 w-5 text-primary" />
            </div>
            <div>
              <div className="text-xl font-bold text-foreground">{loading ? "—" : savedReports.length}</div>
              <div className="text-xs text-muted-foreground">Saved reports</div>
            </div>
          </div>

          <div className="bg-card rounded-2xl border border-border shadow-premium p-5">
            <div className="text-xs text-muted-foreground">Latest report</div>
            <div className="mt-1 text-sm font-semibold text-foreground">{latest?.title || "—"}</div>
            <div className="mt-1 text-xs text-muted-foreground">
              {latest?.created_at ? formatTimestamp(latest.created_at) : ""}
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              Confidence:{" "}
              <span className="text-foreground">
                {typeof latest?.confidence_score === "number" ? `${latest.confidence_score}%` : "—"}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-card rounded-2xl border border-border shadow-premium p-6">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-sm font-bold text-foreground">Recent reports</h2>
            <button onClick={() => navigate("/history")} className="text-xs text-primary hover:underline">
              View all
            </button>
          </div>

          {loading ? (
            <div className="mt-4 text-sm text-muted-foreground">Loading…</div>
          ) : reports.length === 0 ? (
            <div className="mt-4 text-sm text-muted-foreground">No reports yet. Generate your first analysis above.</div>
          ) : (
            <div className="mt-4 space-y-2">
              {reports.slice(0, 6).map((r) => (
                <button
                  key={r.report_id}
                  onClick={() => navigate(`/report/${r.report_id}`)}
                  className="w-full text-left flex items-center justify-between gap-3 p-3 rounded-xl border border-border hover:bg-accent transition-colors"
                >
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-foreground truncate">{r.title || r.report_id}</div>
                    <div className="text-xs text-muted-foreground">{formatTimestamp(r.created_at)}</div>
                  </div>
                  <div className="text-xs text-muted-foreground shrink-0">
                    {typeof r.confidence_score === "number" ? `${r.confidence_score}%` : "—"}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}

