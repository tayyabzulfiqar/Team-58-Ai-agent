import { Home, PlusCircle, Search, Lightbulb, Target, Megaphone, Clock, Bookmark, LayoutTemplate } from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { useLocation } from "react-router-dom";

const agentItems = [
  { title: "Home", url: "/", icon: Home },
  { title: "New Analysis", url: "/new-analysis", icon: PlusCircle },
];

const agentTools = [
  { title: "Research Agent", url: "/research", icon: Search },
  { title: "Insights Agent", url: "/insights", icon: Lightbulb },
  { title: "Strategy Agent", url: "/strategy", icon: Target },
  { title: "Campaign Agent", url: "/campaign", icon: Megaphone },
];

const libraryItems = [
  { title: "History", url: "/history", icon: Clock },
  { title: "Saved Reports", url: "/saved", icon: Bookmark },
  { title: "Templates", url: "/templates", icon: LayoutTemplate },
];

export function AppSidebar() {
  const location = useLocation();

  const linkClass = (path: string) => {
    const active = location.pathname === path;
    return `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-[13px] font-medium transition-all duration-200 ${
      active
        ? "bg-primary/[0.08] text-primary font-semibold"
        : "text-muted-foreground hover:bg-accent hover:text-foreground"
    }`;
  };

  return (
    <aside className="w-[220px] shrink-0 bg-sidebar border-r border-sidebar-border flex flex-col h-screen sticky top-0">
      <div className="p-5 pb-8">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center font-bold text-primary-foreground text-[11px] shadow-elevated tracking-tight">
            58
          </div>
          <span className="font-bold text-foreground text-sm tracking-[-0.02em]">Team 58</span>
        </div>
      </div>

      <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
        {agentItems.map((item) => (
          <NavLink key={item.url} to={item.url} end className={linkClass(item.url)}>
            <item.icon className="h-[18px] w-[18px] shrink-0" />
            <span>{item.title}</span>
          </NavLink>
        ))}

        <div className="pt-7">
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground/50 px-3.5 mb-2.5">
            Agents
          </p>
          <div className="space-y-0.5">
            {agentTools.map((item) => (
              <NavLink key={item.url} to={item.url} end className={linkClass(item.url)}>
                <item.icon className="h-[18px] w-[18px] shrink-0" />
                <span>{item.title}</span>
              </NavLink>
            ))}
          </div>
        </div>

        <div className="pt-7">
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground/50 px-3.5 mb-2.5">
            Library
          </p>
          <div className="space-y-0.5">
            {libraryItems.map((item) => (
              <NavLink key={item.url} to={item.url} end className={linkClass(item.url)}>
                <item.icon className="h-[18px] w-[18px] shrink-0" />
                <span>{item.title}</span>
              </NavLink>
            ))}
          </div>
        </div>
      </nav>

      <div className="p-4 mx-3 mb-4 rounded-2xl bg-accent border border-border shadow-card">
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-[hsl(152_69%_45%)] shadow-[0_0_6px_hsl(152_69%_45%/0.4)] animate-pulse" />
          <div>
            <p className="font-semibold text-foreground text-[11px]">System Online</p>
            <p className="text-[10px] text-muted-foreground">All agents ready</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
