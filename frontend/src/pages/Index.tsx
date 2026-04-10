import { DashboardLayout } from "@/components/DashboardLayout";
import { useNavigate } from "react-router-dom";
import {
  Search,
  Lightbulb,
  Target,
  Megaphone,
  CheckCircle,
  TrendingUp,
  FileText,
  Users,
  Zap,
  ArrowRight,
  BarChart3,
  Clock,
} from "lucide-react";
import { useState } from "react";
import { ConfidenceCircle } from "@/components/ConfidenceCircle";

const suggestions = [
  "My sales are low and inconsistent",
  "I want to grow my customer base",
  "Improve customer retention",
];

const agents = [
  { icon: Search, title: "Research Agent", desc: "Market & competitor research", color: "bg-[hsl(217_91%_95%)] text-[hsl(217_91%_60%)]" },
  { icon: Lightbulb, title: "Insights Agent", desc: "Data analysis & key insights", color: "bg-[hsl(38_92%_95%)] text-[hsl(38_92%_50%)]" },
  { icon: Target, title: "Strategy Agent", desc: "Business strategy & planning", color: "bg-[hsl(350_70%_95%)] text-[hsl(350_70%_55%)]" },
  { icon: Megaphone, title: "Campaign Agent", desc: "Marketing & campaign plans", color: "bg-[hsl(263_70%_95%)] text-[hsl(263_70%_58%)]" },
];

const quickStats = [
  { label: "Reports Generated", value: "128", change: "+12%", icon: FileText, color: "text-primary" },
  { label: "Active Agents", value: "4/4", change: "Online", icon: Zap, color: "text-[hsl(152_69%_45%)]" },
  { label: "Avg. Confidence", value: "92%", change: "+3%", icon: TrendingUp, color: "text-[hsl(38_92%_50%)]" },
  { label: "Team Members", value: "8", change: "+2 new", icon: Users, color: "text-[hsl(263_70%_58%)]" },
];

const recentActivity = [
  { title: "Low sales analysis completed", time: "2 min ago", status: "completed" },
  { title: "Marketing strategy in progress", time: "15 min ago", status: "processing" },
  { title: "Customer retention report saved", time: "1 hour ago", status: "completed" },
  { title: "Pricing optimization started", time: "3 hours ago", status: "completed" },
];

export default function HomePage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const handleGenerate = () => {
    if (!query.trim()) return;
    navigate("/processing", { state: { query } });
  };

  const handleSuggestion = (label: string) => {
    navigate("/processing", { state: { query: label } });
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-5">
        {/* Quick Stats Row */}
        <div className="grid grid-cols-4 gap-4">
          {quickStats.map((stat) => (
            <div
              key={stat.label}
              className="bg-card rounded-2xl border border-border shadow-premium hover:shadow-elevated hover:-translate-y-0.5 transition-all duration-300 p-5 flex items-center gap-4"
            >
              <div className="w-11 h-11 rounded-xl bg-accent flex items-center justify-center shrink-0">
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </div>
              <div>
                <p className="text-[22px] font-bold text-foreground leading-tight">{stat.value}</p>
                <p className="text-[11px] text-muted-foreground mt-0.5">{stat.label}</p>
              </div>
              <span className="ml-auto text-[11px] font-semibold text-[hsl(152_69%_45%)] bg-[hsl(152_69%_45%/0.1)] px-2 py-1 rounded-lg">
                {stat.change}
              </span>
            </div>
          ))}
        </div>

        {/* Hero Section - Full Width */}
        <div className="relative rounded-[20px] border border-border p-10 overflow-hidden">
          <div className="absolute inset-0 gradient-hero" />
          <div className="absolute top-[-40px] right-[10%] w-64 h-64 rounded-full blur-[80px] animate-orb-drift pointer-events-none bg-[hsl(217_91%_60%/0.06)]" />
          <div className="absolute bottom-[-30px] left-[5%] w-56 h-56 rounded-full blur-[70px] animate-orb-drift pointer-events-none bg-[hsl(263_70%_68%/0.06)]" style={{ animationDelay: '4s' }} />
          <div className="absolute inset-0 opacity-[0.015] pointer-events-none" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 256 256\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noise\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'4\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noise)\'/%3E%3C/svg%3E")', backgroundRepeat: 'repeat' }} />

          <div className="relative grid grid-cols-[1fr_auto] gap-10 items-center">
            {/* Left: Content */}
            <div className="space-y-5">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="absolute -inset-3 rounded-2xl blur-[20px] animate-glow-breathe bg-[hsl(217_91%_60%/0.15)]" />
                  <div className="relative w-14 h-14 rounded-2xl gradient-primary flex items-center justify-center text-base font-black text-primary-foreground shadow-elevated animate-float tracking-tight">
                    58
                  </div>
                </div>
                <div>
                  <h1 className="text-[1.75rem] font-extrabold tracking-[-0.03em] text-[hsl(220_20%_10%)] leading-tight">
                    Let's solve your business challenge
                  </h1>
                  <p className="text-[hsl(220_9%_46%)] text-[13px] mt-1 leading-relaxed">
                    Get a complete analysis with insights, strategies, and action plans.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 rounded-2xl px-5 py-3 bg-card border border-border shadow-card focus-within:shadow-elevated focus-within:border-primary/30 transition-all duration-300">
                <Search className="h-[18px] w-[18px] text-muted-foreground shrink-0" />
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
                  placeholder="Describe your business challenge or goal..."
                  className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground/60 outline-none"
                />
                <button
                  onClick={handleGenerate}
                  className="bg-primary hover:bg-[hsl(217_91%_50%)] text-primary-foreground px-6 py-2.5 rounded-xl text-[13px] font-semibold flex items-center gap-2 transition-all duration-300 shrink-0 hover:-translate-y-px hover:shadow-glow active:translate-y-0"
                >
                  Generate Report
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>

              <div className="flex items-center gap-2.5 flex-wrap">
                {suggestions.map((s) => (
                  <button
                    key={s}
                    onClick={() => handleSuggestion(s)}
                    className="px-4 py-2 rounded-xl text-[12px] text-muted-foreground bg-card border border-border hover:border-primary/30 hover:text-foreground hover:-translate-y-0.5 hover:shadow-card transition-all duration-300"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {/* Right: System Status */}
            <div className="flex flex-col items-center gap-3 bg-card/60 backdrop-blur-sm rounded-2xl border border-border p-6 min-w-[180px]">
              <ConfidenceCircle score={100} />
              <div className="text-center mt-1">
                <h3 className="text-[13px] font-bold text-foreground">System Status</h3>
                <div className="flex items-center gap-1.5 justify-center mt-1">
                  <CheckCircle className="h-3.5 w-3.5 text-[hsl(152_69%_45%)]" />
                  <span className="text-[11px] text-muted-foreground font-medium">All Operational</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Agents + Activity Row */}
        <div className="grid grid-cols-[1fr_1fr_1fr] gap-5">
          {/* Agents Grid - spans 2 cols */}
          <div className="col-span-2 bg-card rounded-2xl border border-border shadow-premium p-6">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-[hsl(217_91%_95%)] flex items-center justify-center">
                  <Zap className="h-3.5 w-3.5 text-primary" />
                </div>
                <h3 className="text-[14px] font-bold text-foreground">AI Agents Overview</h3>
              </div>
              <span className="text-[11px] font-medium text-[hsl(152_69%_45%)] bg-[hsl(152_69%_45%/0.1)] px-2.5 py-1 rounded-lg">4 Active</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {agents.map((a) => (
                <div
                  key={a.title}
                  className="flex items-center gap-3.5 p-4 rounded-xl border border-border hover:border-primary/20 hover:shadow-card hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
                >
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${a.color}`}>
                    <a.icon className="h-4.5 w-4.5" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-[13px] font-semibold text-foreground">{a.title}</p>
                    <p className="text-[11px] text-muted-foreground truncate">{a.desc}</p>
                  </div>
                  <div className="ml-auto w-2 h-2 rounded-full bg-[hsl(152_69%_45%)] shrink-0 shadow-[0_0_6px_hsl(152_69%_45%/0.4)]" />
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-card rounded-2xl border border-border shadow-premium p-6">
            <div className="flex items-center gap-2.5 mb-5">
              <div className="w-8 h-8 rounded-xl bg-[hsl(38_92%_95%)] flex items-center justify-center">
                <Clock className="h-3.5 w-3.5 text-[hsl(38_92%_50%)]" />
              </div>
              <h3 className="text-[14px] font-bold text-foreground">Recent Activity</h3>
            </div>
            <div className="space-y-1">
              {recentActivity.map((item, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 p-3 rounded-xl hover:bg-accent transition-all duration-200 cursor-pointer"
                >
                  <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                    item.status === "completed" ? "bg-[hsl(152_69%_45%)]" : "bg-[hsl(38_92%_50%)] animate-pulse"
                  }`} />
                  <div className="min-w-0">
                    <p className="text-[12px] font-medium text-foreground leading-snug truncate">{item.title}</p>
                    <p className="text-[10px] text-muted-foreground mt-0.5">{item.time}</p>
                  </div>
                </div>
              ))}
            </div>
            <button
              onClick={() => navigate("/history")}
              className="mt-3 w-full text-center text-[12px] font-medium text-primary hover:text-primary/80 transition-colors flex items-center justify-center gap-1"
            >
              View all activity <ArrowRight className="h-3 w-3" />
            </button>
          </div>
        </div>

        {/* Bottom Row: Performance Overview */}
        <div className="grid grid-cols-3 gap-5">
          <div className="bg-card rounded-2xl border border-border shadow-premium p-6 hover:shadow-elevated hover:-translate-y-0.5 transition-all duration-300">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-xl bg-[hsl(217_91%_95%)] flex items-center justify-center">
                <BarChart3 className="h-3.5 w-3.5 text-primary" />
              </div>
              <h3 className="text-[13px] font-bold text-foreground">Analysis Quality</h3>
            </div>
            <div className="space-y-3">
              {[
                { label: "Accuracy", pct: 94 },
                { label: "Depth", pct: 88 },
                { label: "Actionability", pct: 91 },
              ].map((m) => (
                <div key={m.label}>
                  <div className="flex justify-between text-[11px] mb-1.5">
                    <span className="text-muted-foreground font-medium">{m.label}</span>
                    <span className="font-bold text-foreground">{m.pct}%</span>
                  </div>
                  <div className="h-2 bg-accent rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full gradient-primary transition-all duration-700"
                      style={{ width: `${m.pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-card rounded-2xl border border-border shadow-premium p-6 hover:shadow-elevated hover:-translate-y-0.5 transition-all duration-300">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-xl bg-[hsl(152_60%_94%)] flex items-center justify-center">
                <TrendingUp className="h-3.5 w-3.5 text-[hsl(152_69%_45%)]" />
              </div>
              <h3 className="text-[13px] font-bold text-foreground">Weekly Insights</h3>
            </div>
            <div className="space-y-3">
              <div className="p-3 rounded-xl bg-accent/50 border border-border">
                <p className="text-[12px] font-medium text-foreground">Top recommendation applied</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">Revenue increased by 18%</p>
              </div>
              <div className="p-3 rounded-xl bg-accent/50 border border-border">
                <p className="text-[12px] font-medium text-foreground">3 new strategies identified</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">Based on latest market data</p>
              </div>
            </div>
          </div>

          <div className="bg-card rounded-2xl border border-border shadow-premium p-6 hover:shadow-elevated hover:-translate-y-0.5 transition-all duration-300">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-xl bg-[hsl(263_70%_95%)] flex items-center justify-center">
                <Target className="h-3.5 w-3.5 text-[hsl(263_70%_58%)]" />
              </div>
              <h3 className="text-[13px] font-bold text-foreground">Quick Actions</h3>
            </div>
            <div className="space-y-2">
              {[
                { label: "New Analysis", action: "/new-analysis" },
                { label: "Browse Templates", action: "/templates" },
                { label: "View Reports", action: "/history" },
              ].map((item) => (
                <button
                  key={item.label}
                  onClick={() => navigate(item.action)}
                  className="w-full flex items-center justify-between p-3 rounded-xl border border-border hover:border-primary/20 hover:bg-accent text-left transition-all duration-200 group"
                >
                  <span className="text-[12px] font-medium text-foreground group-hover:text-primary transition-colors">{item.label}</span>
                  <ArrowRight className="h-3.5 w-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-all" />
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
