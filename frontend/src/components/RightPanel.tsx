import { ChevronRight, Sparkles, X } from "lucide-react";
import { useNavigate } from "react-router-dom";

const recentReports = [
  { title: "Low sales analysis", time: "Jun 2 ahx" },
  { title: "Marketing strategy", time: "Yesterday" },
  { title: "Customer retention", time: "Dec 1" },
  { title: "Pricing test", time: "Dec 3" },
];

export function RightPanel() {
  const navigate = useNavigate();

  return (
    <aside className="w-[240px] shrink-0 border-l border-border bg-card h-screen sticky top-0 overflow-y-auto hidden xl:block">
      <div className="p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-[10px] font-bold uppercase tracking-[0.14em] text-muted-foreground/60">Recent Reports</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate("/history")}
              className="text-[11px] text-primary font-medium hover:text-primary/80 transition-colors duration-200"
            >
              View all
            </button>
            <button className="text-muted-foreground/40 hover:text-muted-foreground transition-colors">
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
        <div className="space-y-0.5">
          {recentReports.map((r, i) => (
            <button
              key={i}
              onClick={() => navigate("/report")}
              className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-accent transition-all duration-200 group text-left"
            >
              <div>
                <p className="text-[13px] font-semibold text-foreground group-hover:text-primary transition-colors duration-200">
                  {r.title}
                </p>
                <p className="text-[11px] text-muted-foreground/50 mt-0.5">{r.time}</p>
              </div>
              <ChevronRight className="h-3.5 w-3.5 text-muted-foreground opacity-0 group-hover:opacity-60 transition-all duration-200" />
            </button>
          ))}
        </div>
      </div>

      <div className="px-5 pb-5">
        <div
          className="rounded-2xl p-6 shadow-premium hover:shadow-elevated hover:-translate-y-0.5 transition-all duration-300 relative overflow-hidden cursor-pointer"
          style={{ background: 'linear-gradient(135deg, hsl(263 70% 68%), hsl(263 70% 62%), hsl(280 60% 60%))' }}
          onClick={() => navigate("/templates")}
        >
          <div className="absolute top-0 right-0 w-24 h-24 bg-white/[0.08] rounded-full -translate-y-1/2 translate-x-1/2" />
          <Sparkles className="h-5 w-5 text-white/90 mb-3" />
          <h4 className="font-bold text-white text-[14px] mb-1.5">Templates available</h4>
          <p className="text-[11px] text-white/60 mb-5 leading-relaxed">
            Try a pre-made template for your next analysis.
          </p>
          <button className="bg-white text-[hsl(263_70%_58%)] text-[12px] font-semibold px-4 py-2.5 rounded-xl transition-all duration-200 hover:bg-white/90">
            Browse Templates
          </button>
        </div>
      </div>
    </aside>
  );
}
