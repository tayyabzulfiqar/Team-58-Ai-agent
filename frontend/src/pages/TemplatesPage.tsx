import { DashboardLayout } from "@/components/DashboardLayout";
import { useNavigate } from "react-router-dom";
import { TrendingDown, TrendingUp, RefreshCw, DollarSign, Sparkles } from "lucide-react";

const templates = [
  { title: "Low Sales Analysis", desc: "Analyze why sales are low and get actionable strategies to boost revenue", icon: TrendingDown, query: "My sales are low and inconsistent", color: "text-destructive", bg: "bg-destructive/10" },
  { title: "Growth Strategy", desc: "Find new growth opportunities and scale your business effectively", icon: TrendingUp, query: "I want to grow my customer base rapidly", color: "text-success", bg: "bg-success/10" },
  { title: "Customer Retention", desc: "Improve customer retention, loyalty, and repeat purchases", icon: RefreshCw, query: "My customers don't come back regularly", color: "text-warning", bg: "bg-warning/10" },
  { title: "Pricing Optimization", desc: "Optimize your pricing strategy for maximum profit margins", icon: DollarSign, query: "I need to optimize my pricing strategy", color: "text-primary", bg: "bg-primary/10" },
];

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
            <p className="text-sm text-muted-foreground ml-9">Start with a pre-built analysis template to save time</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-6">
          {templates.map((t) => (
            <button
              key={t.title}
              onClick={() => navigate("/processing", { state: { query: t.query } })}
              className="bg-card rounded-2xl p-8 border border-border shadow-[0_10px_30px_rgba(0,0,0,0.05)] hover:shadow-[0_16px_40px_rgba(0,0,0,0.08)] hover:-translate-y-1 hover:border-primary/20 transition-all duration-300 text-left group"
            >
              <div className={`w-12 h-12 rounded-xl ${t.bg} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}>
                <t.icon className={`h-6 w-6 ${t.color}`} />
              </div>
              <h3 className="font-bold text-foreground text-lg mb-2">{t.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{t.desc}</p>
            </button>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
