import { DashboardLayout } from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { formatReport, type ReportData } from "@/lib/reportFormatter";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

type StoredReport = {
  report_id: string;
  created_at: string;
  title: string;
  confidence_score: number;
  saved?: boolean;
  data?: ReportData;
  error?: string;
};

export default function SharePage() {
  const { shareId } = useParams();
  const navigate = useNavigate();

  const apiBase =
    (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://127.0.0.1:8000";

  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState<StoredReport | null>(null);

  useEffect(() => {
    if (!shareId) {
      setLoading(false);
      return;
    }
    const controller = new AbortController();
    setLoading(true);
    setReport(null);

    fetch(`${apiBase}/api/share/${shareId}`, { signal: controller.signal })
      .then(async (res) => {
        if (!res.ok) throw new Error(`Request failed (${res.status})`);
        return res.json();
      })
      .then((data) => {
        setReport(data as StoredReport);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    return () => controller.abort();
  }, [apiBase, shareId]);

  if (loading) {
    return (
      <DashboardLayout showRight={false}>
        <div className="p-8 text-sm text-muted-foreground">Loading shared report...</div>
      </DashboardLayout>
    );
  }

  if (!report || report.error) {
    return (
      <DashboardLayout showRight={false}>
        <div className="p-8 space-y-3">
          <div className="text-lg font-bold text-foreground">Shared report not found</div>
          <Button variant="outline" onClick={() => navigate("/")}>
            Go home
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  const data = report.data || {};
  const formatted = formatReport(data);

  return (
    <DashboardLayout showRight={false}>
      <div className="p-8 space-y-7">
        <div className="flex items-start justify-between gap-6">
          <div>
            <h1 className="text-[26px] font-bold text-foreground tracking-tight">{data.main_problem || report.title}</h1>
            <p className="text-sm text-muted-foreground mt-1">Confidence: {data.confidence_score ?? report.confidence_score}%</p>
          </div>
          <Button variant="outline" onClick={() => navigate(`/report/${report.report_id}`)}>
            Open in app
          </Button>
        </div>

        <section className="bg-card rounded-2xl p-6 border border-border">
          <h2 className="text-sm font-bold text-foreground">Report</h2>
          <div className="mt-4 text-sm text-foreground whitespace-pre-wrap leading-relaxed">{formatted}</div>
        </section>
      </div>
    </DashboardLayout>
  );
}
