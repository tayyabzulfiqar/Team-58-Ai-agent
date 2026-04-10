import { Search, Bell, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

export function TopBar() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const handleGenerate = () => {
    if (!query.trim()) return;
    navigate("/processing", { state: { query } });
  };

  return (
    <header className="h-[56px] border-b border-border flex items-center gap-4 px-6 bg-card sticky top-0 z-20">
      <div className="flex items-center flex-1 gap-3 max-w-lg bg-accent border border-border rounded-xl px-4 py-2 transition-all duration-200 focus-within:border-primary/30 focus-within:shadow-elevated">
        <Search className="h-4 w-4 text-muted-foreground shrink-0" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
          placeholder="Describe what you want to analyze"
          className="flex-1 bg-transparent text-[13px] text-foreground placeholder:text-muted-foreground/60 outline-none"
        />
      </div>

      <button
        onClick={handleGenerate}
        className="bg-primary hover:bg-[hsl(217_91%_50%)] text-primary-foreground px-5 py-2 rounded-xl text-[13px] font-semibold flex items-center gap-2 transition-all duration-200 shadow-card hover:shadow-elevated hover:-translate-y-px active:translate-y-0"
      >
        <Sparkles className="h-3.5 w-3.5" />
        Generate Report
      </button>

      <div className="flex items-center gap-2 ml-1">
        <button className="relative p-2.5 rounded-xl hover:bg-accent transition-all duration-200">
          <Bell className="h-4 w-4 text-muted-foreground" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-destructive ring-2 ring-card" />
        </button>
        <button className="w-8 h-8 rounded-xl gradient-primary flex items-center justify-center text-primary-foreground text-[11px] font-bold shadow-card">
          A
        </button>
      </div>
    </header>
  );
}
