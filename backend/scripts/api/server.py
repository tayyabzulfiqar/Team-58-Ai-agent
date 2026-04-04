import html
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote, unquote, urlparse



import requests
import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
from pydantic import BaseModel


# --- Pydantic Models ---
class CampaignRequest(BaseModel):
    business: str
    goal: str

class ResearchRequest(BaseModel):
    topic: str
    depth: Optional[int] = 1

class DataRequest(BaseModel):
    dataset: str
    filters: Optional[dict] = None

# Add project root to Python path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

# --- FastAPI App Initialization ---
app = FastAPI(title="AI Multi-Agent API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Agent Endpoints ---


# --- LLM Tools ---
def call_llm(prompt: str) -> str:
    QWEN_API_KEY = os.getenv("QWEN_API_KEY")
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {QWEN_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen/qwen-2.5-7b-instruct",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception:
        return "LLM error"

# --- Agent Logic ---
def run_campaign_agent(data: dict) -> dict:
    business = data.get("business") or data.get("input", {}).get("business", "")
    goal = data.get("goal") or data.get("input", {}).get("goal", "")
    prompt = (
        f"Create a detailed marketing strategy for {business} to achieve {goal}. "
        "Include channels, budget suggestion, and targeting."
    )
    result = call_llm(prompt)
    return {
        "agent": "campaign",
        "input": {"business": business, "goal": goal},
        "strategy": result
    }

def run_research_agent(data: dict) -> dict:
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    topic = data.get("topic") or data.get("input", {}).get("topic", "") or data.get("query", "")
    summary = []
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": SERPER_API_KEY,
                "Content-Type": "application/json"
            },
            json={"q": topic},
            timeout=20
        )
        response.raise_for_status()
        data_json = response.json()
        organic = data_json.get("organic", [])
        for r in organic[:3]:
            summary.append({
                "title": r.get("title", ""),
                "link": r.get("link", ""),
                "snippet": r.get("snippet", "")
            })
    except Exception:
        summary = []
    return {
        "agent": "research",
        "topic": topic,
        "results": summary
    }

def run_data_agent(data: dict) -> dict:
    dataset = data.get("dataset") or data.get("input", {}).get("dataset", "")
    filters = data.get("filters") or data.get("input", {}).get("filters", {})
    query = f"Dataset: {dataset}, Filters: {filters}"
    prompt = f"Analyze the following query and provide insights: {query}. Include trends, risks, and opportunities."
    result = call_llm(prompt)
    return {
        "agent": "data",
        "query": query,
        "analysis": result
    }

@app.post("/campaign-agent")
async def campaign_agent(request: CampaignRequest):
    return run_campaign_agent(request.dict())

@app.post("/research-agent")
async def research_agent(request: ResearchRequest):
    return run_research_agent(request.dict())

@app.post("/data-agent")
async def data_agent(request: DataRequest):
    return run_data_agent(request.dict())

# --- Master Agent Orchestration ---
def is_complex_query(query: str) -> bool:
    # Heuristic: if query contains multiple agent keywords, treat as complex
    keywords = ["marketing", "ads", "growth", "research", "trend", "news", "data", "analysis", "numbers"]
    count = sum(1 for k in keywords if k in query.lower())
    return count > 1 or any(x in query.lower() for x in [" and ", " then ", ","])

def master_agent_logic(query: str) -> dict:
    decision = []
    output = None
    partials = {}
    try:
        q = query.lower()
        # Chaining for complex queries
        if is_complex_query(query):
            # Step 1: Research
            research_result = run_research_agent({"query": query})
            decision.append("research-agent")
            partials["research"] = research_result
            # Step 2: Campaign (use research summary as input)
            research_summary = "; ".join([r.get("title", "") for r in research_result.get("results", [])])
            campaign_input = {
                "business": research_summary or query,
                "goal": query
            }
            campaign_result = run_campaign_agent(campaign_input)
            decision.append("campaign-agent")
            partials["campaign"] = campaign_result
            # Step 3: Data (summarize previous outputs)
            data_input = {
                "dataset": research_summary or query,
                "filters": {"context": campaign_result.get("strategy", "")}
            }
            data_result = run_data_agent(data_input)
            decision.append("data-agent")
            partials["data"] = data_result
            output = {
                "research": research_result,
                "campaign": campaign_result,
                "data": data_result
            }
        else:
            # Simple decision
            if any(x in q for x in ["marketing", "ads", "growth"]):
                result = run_campaign_agent({"business": query, "goal": query})
                decision.append("campaign-agent")
                output = result
            elif any(x in q for x in ["research", "trend", "news"]):
                result = run_research_agent({"query": query})
                decision.append("research-agent")
                output = result
            elif any(x in q for x in ["data", "analysis", "numbers"]):
                result = run_data_agent({"dataset": query, "filters": {}})
                decision.append("data-agent")
                output = result
            else:
                result = run_research_agent({"query": query})
                decision.append("research-agent")
                output = result
    except Exception as exc:
        output = {"error": str(exc), **partials}
    return {
        "agent": "master",
        "input": query,
        "decision": decision,
        "output": output
    }

@app.post("/master-agent")
async def master_agent(request: dict = Body(...)):
    query = request.get("query", "")
    return master_agent_logic(query)



FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
FIRECRAWL_API_URL = os.getenv("FIRECRAWL_API_URL", "https://api.firecrawl.dev/v1/search").strip()
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192").strip() or "llama3-70b-8192"
DEFAULT_QUERY = os.getenv("RUN_SYSTEM_QUERY", "insurance leads").strip() or "insurance leads"
REQUEST_TIMEOUT = 25
MIN_RESULTS = 5
MAX_RESULTS = 8
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)


def _log(message: str) -> None:
    print(f"[multi-agent] {message}")


def _safe_json(response: requests.Response) -> Dict[str, Any]:
    try:
        payload = response.json()
        return payload if isinstance(payload, dict) else {}
    except Exception as exc:
        _log(f"json-parse-failed error={exc}")
        return {}


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = re.sub(r"<script.*?>.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def _normalize_url(url: Any) -> str:
    clean_url = _clean_text(url)
    clean_url = unquote(clean_url)
    if clean_url.startswith("//"):
        clean_url = f"https:{clean_url}"
    if clean_url.startswith("/url?q="):
        clean_url = clean_url.split("/url?q=", 1)[1].split("&", 1)[0]
    if clean_url.startswith("url?q="):
        clean_url = clean_url.split("url?q=", 1)[1].split("&", 1)[0]
    return clean_url.strip()


def _extract_company_name(url: str, title: str = "") -> str:
    hostname = urlparse(url).netloc.lower().replace("www.", "")
    if hostname:
        company = hostname.split(".")[0].replace("-", " ").replace("_", " ").strip()
        if company:
            return company.title()
    clean_title = re.split(r"[-|:]", title)[0].strip()
    return clean_title or "Unknown"


def _fallback_results(query: str) -> List[Dict[str, Any]]:
    return [
        {
            "title": "Acme Insurance Brokers",
            "url": "https://acme-insurance.example.com",
            "snippet": f"Insurance brokerage lead generated for query: {query}",
            "source": "fallback",
        },
        {
            "title": "Northstar Coverage Group",
            "url": "https://northstar-coverage.example.com",
            "snippet": "Commercial coverage and policy advisory services.",
            "source": "fallback",
        },
        {
            "title": "Summit Policy Advisors",
            "url": "https://summit-policy.example.com",
            "snippet": "Policy consulting and claims support for business clients.",
            "source": "fallback",
        },
        {
            "title": "Prime Quote Solutions",
            "url": "https://prime-quote.example.com",
            "snippet": "Quote optimization and lead response workflows for insurance teams.",
            "source": "fallback",
        },
        {
            "title": "Harbor Risk & Claims",
            "url": "https://harbor-risk.example.com",
            "snippet": "Claims management and broker support services.",
            "source": "fallback",
        },
    ]


def _dedupe_results(items: List[Dict[str, Any]], limit: int = MAX_RESULTS) -> List[Dict[str, Any]]:
    deduped: List[Dict[str, Any]] = []
    seen = set()

    for item in items:
        url = _normalize_url(item.get("url"))
        title = _clean_text(item.get("title"))
        snippet = _clean_text(item.get("snippet"))

        if not _is_valid_url(url):
            continue

        key = url.lower()
        if key in seen:
            continue

        seen.add(key)
        deduped.append(
            {
                "title": title or _extract_company_name(url, title),
                "url": url,
                "snippet": snippet,
                "source": _clean_text(item.get("source")) or "unknown",
            }
        )
        if len(deduped) >= limit:
            break

    if len(deduped) >= MIN_RESULTS:
        return deduped

    for fallback in _fallback_results(DEFAULT_QUERY):
        url = _normalize_url(fallback["url"])
        if url.lower() in seen:
            continue
        seen.add(url.lower())
        deduped.append(fallback)
        if len(deduped) >= min(limit, MIN_RESULTS):
            break

    return deduped[:limit]


def _safe_request(method: str, url: str, **kwargs) -> Optional[requests.Response]:
    try:
        response = requests.request(method, url, timeout=REQUEST_TIMEOUT, **kwargs)
        _log(f"request method={method} url={url} status={response.status_code}")
        response.raise_for_status()
        return response
    except Exception as exc:
        _log(f"request-failed method={method} url={url} error={exc}")
        return None


def _search_firecrawl(query: str) -> List[Dict[str, Any]]:
    if not FIRECRAWL_API_KEY:
        _log("firecrawl-missing-api-key")
        return []

    response = _safe_request(
        "POST",
        FIRECRAWL_API_URL,
        headers={
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        },
        json={"query": query, "limit": MAX_RESULTS},
    )
    if response is None:
        return []

    payload = _safe_json(response)
    data = payload.get("data")
    if not isinstance(data, list):
        _log("firecrawl-invalid-payload")
        return []

    results: List[Dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        results.append(
            {
                "title": item.get("title") or metadata.get("title") or "",
                "url": item.get("url") or item.get("sourceURL") or "",
                "snippet": item.get("description")
                or item.get("snippet")
                or item.get("content")
                or item.get("markdown")
                or "",
                "source": "Firecrawl",
            }
        )
    return _dedupe_results(results)


def _search_duckduckgo(query: str) -> List[Dict[str, Any]]:
    response = _safe_request(
        "GET",
        f"https://duckduckgo.com/html/?q={quote(query)}",
        headers={"User-Agent": USER_AGENT},
    )
    if response is None:
        return []

    html_text = response.text
    matches = re.findall(
        r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    results: List[Dict[str, Any]] = []
    for url, title in matches:
        results.append(
            {
                "title": _clean_text(title),
                "url": _normalize_url(url),
                "snippet": "",
                "source": "DuckDuckGo",
            }
        )
    return _dedupe_results(results)


def _search_google(query: str) -> List[Dict[str, Any]]:
    response = _safe_request(
        "GET",
        f"https://www.google.com/search?q={quote(query)}",
        headers={"User-Agent": USER_AGENT},
    )
    if response is None:
        return []

    html_text = response.text
    matches = re.findall(r'<a href="/url\?q=(https?://[^"&]+)[^"]*"', html_text, flags=re.IGNORECASE)

    results: List[Dict[str, Any]] = []
    for url in matches:
        normalized = _normalize_url(url)
        if "google.com" in normalized.lower():
            continue
        results.append(
            {
                "title": _extract_company_name(normalized),
                "url": normalized,
                "snippet": "",
                "source": "Google",
            }
        )
    return _dedupe_results(results)


def _multi_source_search(query: str) -> List[Dict[str, Any]]:
    layers = (
        ("Firecrawl", _search_firecrawl),
        ("DuckDuckGo", _search_duckduckgo),
        ("Google", _search_google),
    )

    for layer_name, search_fn in layers:
        try:
            results = search_fn(query)
            if len(results) >= MIN_RESULTS:
                _log(f"search-layer-used layer={layer_name} count={len(results)}")
                return results[:MAX_RESULTS]
            if results:
                _log(f"search-layer-partial layer={layer_name} count={len(results)}")
                return _dedupe_results(results)
        except Exception as exc:
            _log(f"search-layer-failed layer={layer_name} error={exc}")

    fallback = _dedupe_results(_fallback_results(query))
    _log(f"search-layer-used layer=fallback count={len(fallback)}")
    return fallback


def _process_research(research: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    processed: List[Dict[str, Any]] = []

    for item in research:
        try:
            title = _clean_text(item.get("title"))
            website = _normalize_url(item.get("url"))
            summary = _clean_text(item.get("snippet"))

            if not _is_valid_url(website):
                continue

            company = _extract_company_name(website, title)
            name = title or company

            processed.append(
                {
                    "name": name,
                    "company": company,
                    "website": website,
                    "summary": summary or f"{company} offers insurance-related services.",
                    "industry": "Insurance",
                }
            )
        except Exception as exc:
            _log(f"processing-failed error={exc}")

    if processed:
        return processed

    return [
        {
            "name": item["title"],
            "company": _extract_company_name(item["url"], item["title"]),
            "website": item["url"],
            "summary": item["snippet"],
            "industry": "Insurance",
        }
        for item in _fallback_results(DEFAULT_QUERY)
    ]


def _score_lead(lead: Dict[str, Any]) -> Dict[str, Any]:
    text = (
        f"{lead.get('name', '')} "
        f"{lead.get('company', '')} "
        f"{lead.get('summary', '')} "
        f"{lead.get('website', '')}"
    ).lower()

    high_terms = ["insurance", "quote", "policy", "broker", "coverage"]
    medium_terms = ["services", "contact", "business", "claims"]

    score = 35
    score += sum(10 for term in high_terms if term in text)
    score += sum(5 for term in medium_terms if term in text)

    if lead.get("website"):
        score += 10
    if len(_clean_text(lead.get("summary"))) > 60:
        score += 10

    score = max(0, min(score, 100))

    if score >= 75:
        category = "high"
    elif score >= 50:
        category = "medium"
    else:
        category = "low"

    return {
        "name": lead.get("name", ""),
        "company": lead.get("company", ""),
        "website": lead.get("website", ""),
        "summary": lead.get("summary", ""),
        "score": score,
        "category": category,
    }


def _analyze_leads(processed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    try:
        analyzed = [_score_lead(lead) for lead in processed]
        analyzed.sort(key=lambda item: item.get("score", 0), reverse=True)
        return analyzed
    except Exception as exc:
        _log(f"analysis-failed error={exc}")
        fallback_processed = _process_research(_fallback_results(DEFAULT_QUERY))
        analyzed = [_score_lead(lead) for lead in fallback_processed]
        analyzed.sort(key=lambda item: item.get("score", 0), reverse=True)
        return analyzed


def _fallback_campaign(lead: Dict[str, Any]) -> str:
    company = _clean_text(lead.get("company")) or "your team"
    return (
        f"Hi {company}, we help insurance businesses turn inbound interest into qualified conversations. "
        "I would love to share a simple outreach workflow tailored to your team."
    )


def _generate_campaign_message(lead: Dict[str, Any]) -> str:
    if not GROQ_API_KEY:
        _log("groq-missing-api-key using-fallback-message")
        return _fallback_campaign(lead)

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Write a short personalized outreach message under 80 words.",
            },
            {
                "role": "user",
                "content": (
                    f"Lead name: {_clean_text(lead.get('name'))}\n"
                    f"Company: {_clean_text(lead.get('company'))}\n"
                    f"Website: {_clean_text(lead.get('website'))}\n"
                    f"Summary: {_clean_text(lead.get('summary'))}\n"
                    f"Score: {lead.get('score')}\n"
                    f"Category: {_clean_text(lead.get('category'))}\n"
                ),
            },
        ],
        "temperature": 0.4,
        "max_tokens": 120,
    }

    response = _safe_request(
        "POST",
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    if response is None:
        return _fallback_campaign(lead)

    content = _safe_json(response).get("choices", [{}])[0].get("message", {}).get("content", "")
    message = _clean_text(content)
    if not message:
        _log("groq-empty-response using-fallback-message")
        return _fallback_campaign(lead)
    return message


def _build_campaigns(analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    campaigns: List[Dict[str, Any]] = []

    for lead in analysis:
        try:
            campaigns.append(
                {
                    "name": lead.get("name", ""),
                    "company": lead.get("company", ""),
                    "website": lead.get("website", ""),
                    "message": _generate_campaign_message(lead),
                }
            )
        except Exception as exc:
            _log(f"campaign-build-failed company={lead.get('company', '')} error={exc}")
            campaigns.append(
                {
                    "name": lead.get("name", ""),
                    "company": lead.get("company", ""),
                    "website": lead.get("website", ""),
                    "message": _fallback_campaign(lead),
                }
            )

    if campaigns:
        return campaigns

    fallback_analysis = _analyze_leads(_process_research(_fallback_results(DEFAULT_QUERY)))
    return [
        {
            "name": lead["name"],
            "company": lead["company"],
            "website": lead["website"],
            "message": _fallback_campaign(lead),
        }
        for lead in fallback_analysis
    ]


def _build_safe_response(query: str) -> Dict[str, Any]:
    research = _multi_source_search(query)
    processed = _process_research(research)
    analysis = _analyze_leads(processed)
    campaigns = _build_campaigns(analysis)

    safe_response = {
        "status": "success",
        "research": research if research else _dedupe_results(_fallback_results(query)),
        "processed": processed if processed else _process_research(_fallback_results(query)),
        "analysis": analysis if analysis else _analyze_leads(_process_research(_fallback_results(query))),
        "campaigns": campaigns if campaigns else _build_campaigns(_analyze_leads(_process_research(_fallback_results(query)))),
    }

    return safe_response


@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/agents")
async def agents():
    return {
        "agents": [
            {"name": "research_agent", "role": "Firecrawl + multi-source search"},
            {"name": "processing_agent", "role": "clean and structure leads"},
            {"name": "analysis_agent", "role": "score and classify leads"},
            {"name": "campaign_design_agent", "role": "generate outreach with Groq"},
        ]
    }


@app.post("/run-system")
async def run_system():
    try:
        return _build_safe_response(DEFAULT_QUERY)
    except Exception as exc:
        _log(f"run-system-failed error={exc}")
        fallback = _fallback_results(DEFAULT_QUERY)
        return {
            "status": "success",
            "research": fallback,
            "processed": _process_research(fallback),
            "analysis": _analyze_leads(_process_research(fallback)),
            "campaigns": _build_campaigns(_analyze_leads(_process_research(fallback))),
        }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
