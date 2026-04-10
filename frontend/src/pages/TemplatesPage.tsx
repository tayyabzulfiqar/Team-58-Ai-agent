import { DashboardLayout } from "@/components/DashboardLayout";
import { useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";

export default function TemplatesPage() {
  const navigate = useNavigate();

  return (
    <DashboardLayout showRight={false}>
      <div className="p-8 space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <Sparkles className="h-6 w-6 text-primary" />
              <h1 className="text-[26px] font-bold text-foreground tracking-tight">Templates</h1>
            </div>
            <p className="text-sm text-muted-foreground ml-9">
              Templates are disabled in premium mode to ensure every report is generated from real, unique input.
            </p>
          </div>
        </div>
        <div className="bg-card rounded-2xl p-8 border border-border shadow-premium">
          <p className="text-sm text-muted-foreground">
            To generate a report, go back to the home page and enter a specific business context (industry, location,
            audience, and the metric you're struggling with).
          </p>
          <button
            onClick={() => navigate("/")}
            className="mt-5 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90"
          >
            Start a new analysis
          </button>
        </div>
      </div>
    </DashboardLayout>
  );
}
