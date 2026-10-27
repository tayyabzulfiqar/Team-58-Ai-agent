# Team-58: AI Research Report Agent

Give it a business question. It searches the web, collects evidence, and uses an LLM to write a consulting-style report you can save, download as a PDF or share by link.

Built as a freelance project for IAM Entertainment (Dubai) in March and April 2026, and deployed on Railway. The deployment is no longer running.

## How it works

1. **Search and collect:** Serper (Google search), Firecrawl (page scraping) and Reddit.
2. **Clean and structure:** normalise, score and de-duplicate the findings.
3. **Reason:** the Qwen LLM (Alibaba DashScope API) writes insights, scores opportunities and drafts the report.
4. **Deliver:** saved reports, PDF export (ReportLab) and share links, shown in a React frontend.

## Stack

| Layer | Tech |
| --- | --- |
| Backend | Python, FastAPI, httpx, ReportLab |
| AI | Qwen LLM via DashScope API |
| Data sources | Serper, Firecrawl, Reddit |
| Frontend | React, TypeScript, Vite, Tailwind |
| Deployment | Railway |

## Main API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/run-system` | Run the full research pipeline |
| GET | `/api/reports` | List reports |
| GET | `/api/reports/{id}/pdf` | Download a report as PDF |
| POST | `/api/reports/{id}/share` | Create a share link |

## Run locally

```bash
cd backend
pip install -r requirements.txt
export QWEN_API_KEY=... DASHSCOPE_API_KEY=... SERPER_API_KEY=... FIRECRAWL_API_KEY=...
uvicorn main:app --reload
```

```bash
cd frontend && npm install && npm run dev
```
