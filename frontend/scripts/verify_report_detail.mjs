import { chromium } from "@playwright/test";

const historyUrl = "http://127.0.0.1:8080/history";

const browser = await chromium.launch();
const page = await browser.newPage();

const errors = [];
page.on("console", (msg) => {
  if (msg.type() === "error") errors.push(msg.text());
});
page.on("pageerror", (err) => errors.push(String(err)));

await page.goto(historyUrl, { waitUntil: "networkidle" });

const firstReport = page.locator("button").filter({ hasText: "%" }).first();
await firstReport.click();
await page.waitForURL(/\/report\/[^/]+$/, { timeout: 30_000 });
await page.waitForLoadState("networkidle");

const title = await page.locator("h1").first().innerText();
const keyInsightHeader = await page.locator("text=Key Insight").count();
const strategyHeader = await page.locator("text=Strategy").count();
const actionPlanHeader = await page.locator("text=Action Plan").count();

console.log("NAVIGATED_URL:", page.url());
console.log("TITLE:", title);
console.log("HAS_SECTIONS:", {
  keyInsight: keyInsightHeader > 0,
  strategy: strategyHeader > 0,
  actionPlan: actionPlanHeader > 0,
});
console.log("CONSOLE_ERRORS:", errors);

await browser.close();

