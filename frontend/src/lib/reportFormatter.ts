export type ReportData = {
  main_problem?: string;
  key_insight?: string;
  strategy?: { title?: string; points?: string[] };
  whats_happening?: string[];
  root_causes?: string[];
  action_plan?: { step?: number; title?: string; description?: string; timeline?: string }[];
  campaign_plan?: { offer?: string; message?: string; channels?: string[]; goal?: string };
  confidence_score?: number;
};

function toCleanSentence(value: unknown, fallback: string): string {
  const raw = typeof value === "string" ? value.trim() : "";
  const text = raw.length > 0 ? raw : fallback;
  const withCapital = text.length > 0 ? text[0].toUpperCase() + text.slice(1) : fallback;
  return /[.!?]$/.test(withCapital) ? withCapital : `${withCapital}.`;
}

function uniqueNonEmpty(items: unknown): string[] {
  if (!Array.isArray(items)) return [];
  const seen = new Set<string>();
  const out: string[] = [];
  for (const item of items) {
    if (typeof item !== "string") continue;
    const trimmed = item.trim();
    if (!trimmed) continue;
    const key = trimmed.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(trimmed);
  }
  return out;
}

function stripWeekPrefix(text: string): string {
  return text.replace(/^\s*weeks?\s*\d+(?:\s*-\s*\d+)?\s*:\s*/i, "").trim();
}

function toTitleCase(word: string): string {
  if (!word) return word;
  return word[0].toUpperCase() + word.slice(1).toLowerCase();
}

function capitalizeFirst(text: string): string {
  const t = text.trim();
  if (!t) return t;
  return t[0].toUpperCase() + t.slice(1);
}

export function formatReport(data: ReportData): string {
  const mainProblem = toCleanSentence(data?.main_problem, "No main problem provided");
  const keyInsight = toCleanSentence(data?.key_insight, "No key insight provided");

  const strategyPoints = uniqueNonEmpty(data?.strategy?.points);
  const strategyBlock =
    strategyPoints.length > 0
      ? strategyPoints.map((p) => `• ${capitalizeFirst(stripWeekPrefix(p) || p)}`).join("\n")
      : "• No strategy points provided";

  const planItems = Array.isArray(data?.action_plan) ? data.action_plan : [];
  const steps = planItems
    .map((item) => {
      const title = typeof item?.title === "string" ? capitalizeFirst(stripWeekPrefix(item.title.trim())) : "";
      const timeline = typeof item?.timeline === "string" ? item.timeline.trim() : "";
      const combined =
        title || timeline
          ? `${title}${title && timeline ? ` (${timeline})` : timeline ? `(${timeline})` : ""}`
          : "";
      return combined.trim();
    })
    .filter((s) => s.length > 0);

  const executionBlock =
    steps.length > 0 ? steps.map((s, i) => `${i + 1}. ${s}`).join("\n") : "1. No execution steps provided";

  const message = typeof data?.campaign_plan?.message === "string" ? data.campaign_plan.message.trim() : "";
  const goal = typeof data?.campaign_plan?.goal === "string" ? data.campaign_plan.goal.trim() : "";
  const channels = Array.isArray(data?.campaign_plan?.channels)
    ? data.campaign_plan.channels
        .filter((c): c is string => typeof c === "string" && c.trim().length > 0)
        .map((c) => c.trim())
    : [];

  const channelsText = channels.length > 0 ? channels.map((c) => toTitleCase(c)).join(", ") : "";
  const campaignParts = [
    message ? `Message: ${toCleanSentence(message, "").replace(/\.$/, "")}.` : "",
    goal ? `Goal: ${toCleanSentence(goal, "").replace(/\.$/, "")}.` : "",
    channelsText ? `Channels: ${toCleanSentence(channelsText, "").replace(/\.$/, "")}.` : "",
  ].filter((p) => p.length > 0);
  const campaignBlock =
    campaignParts.length > 0
      ? campaignParts.join(" ")
      : "Message: Not provided. Goal: Not provided. Channels: Not provided.";

  return [
    "Main Problem:",
    mainProblem,
    "",
    "Key Insight:",
    keyInsight,
    "",
    "Strategy:",
    strategyBlock,
    "",
    "Execution Plan:",
    executionBlock,
    "",
    "Campaign Plan:",
    campaignBlock,
    "",
  ].join("\n");
}

