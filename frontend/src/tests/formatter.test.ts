import { describe, expect, it } from "vitest";
import { formatReport } from "@/lib/reportFormatter";

describe("formatReport", () => {
  it("formats a readable report instantly", () => {
    const mockData = {
      main_problem: "conversion optimization",
      key_insight: "Users drop at checkout",
      strategy: { points: ["Improve checkout UX", "Add trust signals"] },
      whats_happening: ["High drop-offs"],
      root_causes: ["Friction in checkout"],
      action_plan: [
        { step: 1, title: "Fix checkout", timeline: "3 days" },
        { step: 2, title: "Improve UX", timeline: "5 days" },
      ],
      campaign_plan: {
        message: "Better UX = more sales",
        goal: "Increase conversions",
        channels: ["facebook"],
      },
      confidence_score: 80,
    };

    // Required by task: show formatted output in test logs
    console.log(formatReport(mockData));

    const output = formatReport(mockData);

    expect(output).toContain("Main Problem:");
    expect(output).toContain("Strategy:");
    expect(output).toContain("Execution Plan:");
    expect(output.trim().length).toBeGreaterThan(0);

    expect(output).toContain("Conversion optimization.");
    expect(output).toContain("Users drop at checkout.");
    expect(output).toContain("• Improve checkout UX");
    expect(output).toContain("1. Fix checkout (3 days)");
    expect(output).toContain("Channels:");
  });
});
