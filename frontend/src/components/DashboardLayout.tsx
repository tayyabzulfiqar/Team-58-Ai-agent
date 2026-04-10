import { ReactNode } from "react";
import { AppSidebar } from "./AppSidebar";
import { TopBar } from "./TopBar";
import { RightPanel } from "./RightPanel";

interface Props {
  children: ReactNode;
  showRight?: boolean;
}

export function DashboardLayout({ children, showRight = true }: Props) {
  return (
    <div className="flex min-h-screen w-full">
      <AppSidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <TopBar />
        <div className="flex flex-1">
          <main className="flex-1 overflow-y-auto">{children}</main>
          {showRight && <RightPanel />}
        </div>
      </div>
    </div>
  );
}
