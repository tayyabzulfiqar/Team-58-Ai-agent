import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Search, Lightbulb, Target, Megaphone, Check, Loader2 } from "lucide-react";

const agentSteps = [
  { icon: Search, title: "Research Agent", status: "Collecting data...", color: "text-info" },
  { icon: Lightbulb, title: "Insights Agent", status: "Analyzing patterns...", color: "text-warning" },
  { icon: Target, title: "Strategy Agent", status: "Building strategy...", color: "text-primary" },
  { icon: Megaphone, title: "Campaign Agent", status: "Generating execution...", color: "text-success" },
];

export default function ProcessingPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const state = location.state as { query?: string } | null;
  const query = typeof state?.query === "string" ? state.query.trim() : "";

  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query) {
      setError("Missing query. Please go back and enter your business problem.");
      return;
    }

    const base =
      (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://127.0.0.1:8000";

    let step = 0;
    const interval = setInterval(() => {
      step++;
      setActiveStep(step);

      if (step >= agentSteps.length) {
        clearInterval(interval);

        fetch(`${base}/api/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query }),
        })
          .then(async (res) => {
            if (!res.ok) throw new Error(`Request failed (${res.status})`);
            return res.json();
          })
          .then((data) => {
            const reportId = data?.report_id as string | undefined;
            if (!reportId) throw new Error("Backend did not return report_id");
            navigate("/report", { state: { reportId } });
          })
          .catch(() => setError("Failed to generate report. Please try again."));
      }
    }, 1200);

    return () => clearInterval(interval);
  }, [navigate, query]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px]" />

      <div className="max-w-lg w-full mx-auto p-8 space-y-8 relative z-10">
        <div className="text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl gradient-primary flex items-center justify-center mx-auto font-bold text-primary-foreground text-lg shadow-[0_10px_30px_rgba(59,130,246,0.3)]">
            58
          </div>

          <h1 className="text-2xl font-bold text-foreground tracking-tight">Processing Your Analysis</h1>
          <p className="text-sm text-muted-foreground">{query ? `"${query}"` : ""}</p>
        </div>

        {error ? (
          <div className="bg-card rounded-2xl border border-border p-5">
            <p className="text-sm font-semibold text-foreground">Something went wrong</p>
            <p className="text-xs text-muted-foreground mt-2">{error}</p>
            <button onClick={() => navigate("/")} className="mt-4 text-sm font-medium text-primary hover:underline">
              Back to home
            </button>
          </div>
        ) : null}

        <div className="space-y-4">
          {agentSteps.map((step, i) => {
            const done = i < activeStep;
            const current = i === activeStep;

            return (
              <div
                key={i}
                className={`flex items-center gap-4 p-5 rounded-2xl border transition-all duration-500 ${
                  done
                    ? "bg-card border-primary/20 shadow-[0_10px_30px_rgba(0,0,0,0.05)]"
                    : current
                      ? "bg-card border-primary/30 shadow-[0_10px_30px_rgba(59,130,246,0.1)] animate-pulse-glow"
                      : "bg-card/50 border-border opacity-40"
                }`}
              >
                <div
                  className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${
                    done ? "bg-primary/15" : current ? "bg-primary/10" : "bg-accent"
                  }`}
                >
                  {done ? (
                    <Check className="h-5 w-5 text-primary" />
                  ) : current ? (
                    <Loader2 className={`h-5 w-5 ${step.color} animate-spin`} />
                  ) : (
                    <step.icon className="h-5 w-5 text-muted-foreground" />
                  )}
                </div>

                <div>
                  <p className="text-sm font-semibold text-foreground">{step.title}</p>
                  <p className="text-xs text-muted-foreground">{done ? "Complete" : current ? step.status : "Waiting..."}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

