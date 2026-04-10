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

function asNonEmptyString(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((v) => (typeof v === "string" ? v.trim() : "")).filter((v) => v.length > 0);
}

// Note: This formatter must not invent, rewrite, or replace values.
export function formatReport(data: ReportData): string {
  const mainProblem = asNonEmptyString(data?.main_problem);
  const keyInsight = asNonEmptyString(data?.key_insight);

  const strategyPoints = asStringList(data?.strategy?.points);
  const strategyBlock = strategyPoints.map((p) => `• ${p}`).join("\n");

  const actionPlan = Array.isArray(data?.action_plan) ? data.action_plan : [];
  const steps = actionPlan
    .map((s) => {
      const title = asNonEmptyString(s?.title);
      const timeline = asNonEmptyString(s?.timeline);
      if (title && timeline) return `${title} (${timeline})`;
      return title || timeline;
    })
    .filter((v) => v.length > 0);
  const executionBlock = steps.map((s, i) => `${i + 1}. ${s}`).join("\n");

  const campaign = data?.campaign_plan || {};
  const message = asNonEmptyString(campaign?.message);
  const goal = asNonEmptyString(campaign?.goal);
  const channels = asStringList(campaign?.channels);
  const channelsText = channels.join(", ");

  const campaignParts = [
    message ? `Message: ${message}` : "",
    goal ? `Goal: ${goal}` : "",
    channelsText ? `Channels: ${channelsText}` : "",
  ].filter(Boolean);

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
    campaignParts.join("\n"),
    "",
  ].join("\n");
}

