import { chromium } from "playwright";

const apiBase = process.env.API_BASE || "http://127.0.0.1:8000";
const webBase = process.env.WEB_BASE || "http://localhost:8080";

const uniqueQuery = `Luxury gym in Dubai struggling with retention (${Date.now()})`;
const analyzed = await (
  await fetch(`${apiBase}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: uniqueQuery }),
  })
).json();
const reportId = analyzed?.report_id;
if (!reportId) {
  console.error("Backend did not return report_id");
  process.exit(1);
}

const browser = await chromium.launch();
const page = await browser.newPage();
const consoleErrors = [];
page.on("console", (msg) => {
  if (msg.type() === "error") consoleErrors.push(msg.text());
});
page.on("dialog", async (dialog) => {
  await dialog.dismiss();
});

const start = Date.now();
await page.goto(`${webBase}/report/${reportId}`, { waitUntil: "domcontentloaded", timeout: 60000 });
await page.waitForSelector("text=Main Problem", { timeout: 20000 });
const firstRenderMs = Date.now() - start;

const hasEnhancingFast = ((await page.textContent("body")) || "").includes("Enhancing report with AI");

const aiRespPromise = page.waitForResponse(
  (r) => r.url().includes("/api/format-report") && r.request().method() === "POST",
  { timeout: 20000 },
);
await page.getByText("🤖 AI").click();
const aiResp = await aiRespPromise;
const aiOk = aiResp.ok();

const shareRespPromise = page.waitForResponse(
  (r) => /\/api\/reports\/[^/]+\/share$/.test(r.url()) && r.request().method() === "POST",
  { timeout: 20000 },
);
await page.getByRole("button", { name: "🔗 Share" }).click();
const shareResp = await shareRespPromise;
const shareOk = shareResp.ok();
const shareJson = await shareResp.json();
const shareUrl = shareJson?.share_url;

const sharePage = await browser.newPage();
await sharePage.goto(`${webBase}${shareUrl}`, { waitUntil: "domcontentloaded", timeout: 60000 });
await sharePage.waitForSelector("text=Main Problem", { timeout: 20000 });

const pdfRes = await fetch(`${apiBase}/api/reports/${reportId}/pdf`);
const pdfBuf = Buffer.from(await pdfRes.arrayBuffer());
const pdfOk =
  pdfRes.ok &&
  pdfRes.headers.get("content-type") === "application/pdf" &&
  pdfBuf.subarray(0, 4).toString() === "%PDF";

console.log(
  JSON.stringify({
    reportId,
    firstRenderMs,
    hasEnhancingFast,
    aiOk,
    shareOk,
    pdfOk,
    consoleErrorsCount: consoleErrors.length,
  }),
);

await browser.close();

if (consoleErrors.length || !aiOk || !shareOk || !pdfOk || hasEnhancingFast) process.exit(1);
