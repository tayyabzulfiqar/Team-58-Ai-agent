import { chromium } from "@playwright/test";

const url = "http://127.0.0.1:8080/history";

const browser = await chromium.launch();
const page = await browser.newPage();

const logs = [];
const errors = [];

page.on("console", (msg) => {
  const text = msg.text();
  logs.push({ type: msg.type(), text });
  if (msg.type() === "error") errors.push(text);
});
page.on("pageerror", (err) => errors.push(String(err)));

await page.goto(url, { waitUntil: "networkidle" });

const hasEmptyState = await page.locator("text=No reports yet.").count();
const reportButtons = await page.locator("button").count();

console.log("UI URL:", url);
console.log("UI hasEmptyState:", hasEmptyState > 0);
console.log("UI buttonCount:", reportButtons);
console.log("CONSOLE LOGS:", JSON.stringify(logs, null, 2));
console.log("CONSOLE ERRORS:", JSON.stringify(errors, null, 2));

await browser.close();
