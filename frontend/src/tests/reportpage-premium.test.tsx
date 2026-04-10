import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import ReportPage from "@/pages/ReportPage";

describe("ReportPage premium controls", () => {
  it("renders fast by default and can switch to AI mode + share", async () => {
    const mockReport = {
      report_id: "r-123",
      created_at: "2026-04-10T00:00:00Z",
      title: "conversion optimization",
      confidence_score: 80,
      data: {
        main_problem: "conversion optimization",
        key_insight: "Users drop at checkout",
        strategy: { points: ["Improve checkout UX", "Add trust signals"] },
        action_plan: [
          { step: 1, title: "Fix checkout", timeline: "3 days" },
          { step: 2, title: "Improve UX", timeline: "5 days" },
        ],
        campaign_plan: { message: "Better UX = more sales", goal: "Increase conversions", channels: ["facebook"] },
        confidence_score: 80,
      },
    };

    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/reports/r-123")) {
        return new Response(JSON.stringify(mockReport), { status: 200, headers: { "Content-Type": "application/json" } });
      }
      if (url.includes("/api/format-report") && init?.method === "POST") {
        await new Promise((r) => setTimeout(r, 20));
        return new Response(JSON.stringify({ formatted_text: "AI REPORT" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      if (url.includes("/api/reports/r-123/share") && init?.method === "POST") {
        return new Response(JSON.stringify({ share_url: "/share/s-1" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      return new Response("Not found", { status: 404 });
    });

    vi.stubGlobal("fetch", fetchMock);
    Object.defineProperty(navigator, "clipboard", { value: { writeText: vi.fn(async () => {}) }, configurable: true });
    vi.stubGlobal("alert", vi.fn());

    render(
      <MemoryRouter initialEntries={["/report/r-123"]}>
        <Routes>
          <Route path="/report/:id" element={<ReportPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByRole("heading", { name: /conversion optimization/i })).toBeInTheDocument();
    expect(screen.getByText("Main Problem")).toBeInTheDocument();
    expect(screen.getByText("⚡ Fast")).toBeInTheDocument();

    fireEvent.click(screen.getByText("🤖 AI"));
    expect(await screen.findByText("AI REPORT")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "🔗 Share" }));
    await waitFor(() => {
      expect(fetchMock.mock.calls.some(([u]) => String(u).includes("/api/reports/r-123/share"))).toBe(true);
    });
    expect((globalThis as any).alert).toHaveBeenCalledWith("Link copied!");
  });
});
