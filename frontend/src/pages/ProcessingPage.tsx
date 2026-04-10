import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const progressSteps = [
  "Researching market...",
  "Analyzing behavior...",
  "Building strategy...",
  "Generating report...",
];

export default function ProcessingPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const state = location.state as { query?: string } | null;
  const query = typeof state?.query === "string" ? state.query.trim() : "";

  const [error, setError] = useState<string | null>(null);
  const [stepIndex, setStepIndex] = useState(0);
  const [reportId, setReportId] = useState<string | null>(null);

  const API_BASE =
    (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://127.0.0.1:8000";

  const currentStep = useMemo(() => progressSteps[stepIndex % progressSteps.length], [stepIndex]);

  useEffect(() => {
    if (!query) {
      setError("Missing query. Please go back and enter your business problem.");
      return;
    }

    const controller = new AbortController();
    setError(null);
    setReportId(null);
    setStepIndex(0);

    const stepTimer = window.setInterval(() => setStepIndex((s) => s + 1), 1000);

    fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      signal: controller.signal,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(`Request failed (${res.status})`);
        return res.json();
      })
      .then((payload) => {
        const id = payload?.report_id as string | undefined;
        if (!id) throw new Error("Backend did not return report_id");
        setReportId(id);

        // Demo mode: feel fast. Navigate quickly, then let the report page poll until it's ready.
        window.setTimeout(() => navigate("/report", { state: { reportId: id } }), 2500);
      })
      .catch(() => setError("Failed to start analysis. Please try again."))
      .finally(() => {
        // keep step animation running while on this page; it will stop on unmount after navigation
      });

    return () => {
      controller.abort();
      window.clearInterval(stepTimer);
    };
  }, [API_BASE, navigate, query]);

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-6">
      <div className="w-full max-w-md bg-card rounded-2xl border border-border shadow-xl p-6">
        <div className="text-center">
          <div className="w-14 h-14 rounded-2xl gradient-primary flex items-center justify-center mx-auto font-bold text-primary-foreground text-lg">
            58
          </div>
          <h1 className="mt-4 text-xl font-bold text-foreground tracking-tight">AI agents are analyzing your business...</h1>
          <p className="mt-2 text-xs text-muted-foreground">{query ? `"${query}"` : ""}</p>
        </div>

        {error ? (
          <div className="mt-5 rounded-xl border border-border bg-background/50 p-4">
            <p className="text-sm font-semibold text-foreground">Something went wrong</p>
            <p className="text-xs text-muted-foreground mt-2">{error}</p>
            <button onClick={() => navigate("/")} className="mt-4 text-sm font-medium text-primary hover:underline">
              Back to home
            </button>
          </div>
        ) : (
          <div className="mt-6 space-y-3">
            <div className="text-sm text-foreground font-medium">{currentStep}</div>
            <div className="h-2 bg-accent rounded-full overflow-hidden">
              <div
                className="h-full gradient-primary transition-all duration-700"
                style={{ width: `${((stepIndex % progressSteps.length) + 1) * (100 / progressSteps.length)}%` }}
              />
            </div>
            <div className="text-xs text-muted-foreground">
              {reportId ? "Report created. Opening dashboard..." : "Starting analysis..."}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
