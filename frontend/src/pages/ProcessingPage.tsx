import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Search, Lightbulb, Target, Megaphone, Check, Loader2 } from "lucide-react";

const agentSteps = [
  { icon: Search, title: "Research Agent", status: "Collecting data...", color: "text-info" },
  { icon: Lightbulb, title: "Insights Agent", status: "Analyzing patterns...", color: "text-warning" },
  { icon: Target, title: "Strategy Agent", status: "Building strategy...", color: "text-primary" },
  { icon: Megaphone, title: "Campaign Agent", status: "Generating execution...", color: "text-success" },
];

export default function ProcessingPage() {
  const location = useLocation();
  const query = (location.state as { query?: string })?.query || "Business analysis";
  const [activeStep, setActiveStep] = useState(0);

  // ✅ FIXED STEP + REDIRECT LOGIC
  useEffect(() => {
    let step = 0;

    const interval = setInterval(() => {
      step++;
      setActiveStep(step);

      if (step === agentSteps.length) {
        clearInterval(interval);

        setTimeout(() => {
          window.location.href = "/report";
        }, 1500);
      }
    }, 1200);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px]" />

      <div className="max-w-lg w-full mx-auto p-8 space-y-8 relative z-10">
        <div className="text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl gradient-primary flex items-center justify-center mx-auto font-bold text-primary-foreground text-lg shadow-[0_10px_30px_rgba(59,130,246,0.3)]">
            58
          </div>
          <h1 className="text-2xl font-bold text-foreground tracking-tight">
            Processing Your Analysis
          </h1>
          <p className="text-sm text-muted-foreground">"{query}"</p>
        </div>

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
                    done ? "bg-primary/