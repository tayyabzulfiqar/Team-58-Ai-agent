import json
import requests
import time
from datetime import datetime
from pathlib import Path
import os

# === RETRY DECORATOR (must be before any usage) ===
def retry(max_attempts=1, backoff=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = backoff
            for attempt in range(1, max_attempts+1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"{func.__name__} failed (attempt {attempt}): {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
                        delay *= 2
            return []
        return wrapper
    return decorator

# === API KEYS (SYSTEM INJECTION) ===
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")


# === HEALTH CHECK FLAGS ===
SERPER_HEALTHY = False
QWEN_HEALTHY = False
SAFE_MODE = False

def log_phase(msg):
    print(f"\n{'='*12} {msg} {'='*12}\n")
# === HEALTH CHECKS ===
def health_check_serper():
    global SERPER_HEALTHY
    log_phase("STEP 1 — API HEALTH CHECK: SERPER")
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": "AI business news"}
    try:
        resp = requests.post("https://google.serper.dev/search", headers=headers, json=payload, timeout=10)
        if resp.status_code == 200 and resp.json().get("organic"):
            SERPER_HEALTHY = True
            log("[SERPER] HEALTHY")
        else:
            log(f"[SERPER] FAIL: {resp.status_code} {resp.text}")
            # Retry once
            resp = requests.post("https://google.serper.dev/search", headers=headers, json=payload, timeout=10)
            if resp.status_code == 200 and resp.json().get("organic"):
                SERPER_HEALTHY = True
                log("[SERPER] HEALTHY (after retry)")
            else:
                log(f"[SERPER] FAILED after retry: {resp.status_code} {resp.text}")
    except Exception as e:
        log(f"[SERPER] EXCEPTION: {e}")
        # Retry once
        try:
            resp = requests.get("https://serpapi.com/search.json", headers=headers, params=params, timeout=10)
            if resp.status_code == 200 and resp.json().get("news_results"):
                SERPER_HEALTHY = True
                log("[SERPER] HEALTHY (after retry)")
            else:
                log(f"[SERPER] FAILED after retry: {resp.status_code} {resp.text}")
        except Exception as e2:
            log(f"[SERPER] EXCEPTION (retry): {e2}")

def health_check_qwen():
    global QWEN_HEALTHY, SAFE_MODE
    log_phase("STEP 1 — API HEALTH CHECK: QWEN")

# === SERPER SOURCE ===
@retry(max_attempts=1, backoff=1)
def fetch_serper():
    # BYPASS HEALTH CHECK: Always run Serper
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": "AI business news"}
    try:
        resp = requests.post("https://google.serper.dev/search", headers=headers, json=payload, timeout=10)
        if resp.status_code != 200:
            log(f"[SERPER] FAIL: {resp.status_code}")
            return []
        data = resp.json()
        results = []
        for item in data.get("organic", []):
            title = item.get("title") or ""
            content = item.get("snippet") or item.get("link") or ""
            timestamp = item.get("date") or str(datetime.now())
            results.append({
                "title": title,
                "content": content,
                "source": "serper",
                "timestamp": timestamp
            })
        log(f"[SERPER] {len(results)} records fetched")
        return results
    except Exception as e:
        log(f"[SERPER] EXCEPTION: {e}")
        return []

# === SYSTEM GUARD IMPORTS ===
import hashlib

# === SYSTEM CONSTANTS ===
RAW_PATH = os.path.abspath("backend/data/raw/raw_data.json")
DEBUG_PATH = os.path.abspath("backend/data/debug/raw_data_debug.json")

# === CONFIG ===
DEBUG_MODE = False  # Set to False for production
OUTPUT_PATH = RAW_PATH if not DEBUG_MODE else DEBUG_PATH
SEED_PATH = os.path.abspath("backend/data/seed/seed_data.json")

# === LOGGING ===
def log(msg):
    print(msg)


# === RETRY DECORATOR ===
def retry(max_attempts=1, backoff=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = backoff
            for attempt in range(1, max_attempts+1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    log(f"{func.__name__} failed (attempt {attempt}): {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
                        delay *= 2
            return []
        return wrapper
    return decorator

# === DATA VALIDATION ===
def validate_data(records):
    valid = []
    dropped = 0
    for r in records:
        if not isinstance(r, dict):
            dropped += 1
            log("[GUARD] INVALID RECORD - not a dict")
            continue
        missing = []
        for field in ("title", "content", "source", "timestamp"):
            if not r.get(field):
                missing.append(field)
        if missing:
            dropped += 1
            log(f"[GUARD] INVALID SCHEMA - missing {missing}")
            continue
        valid.append(r)
    log(f"[AGENT] VALIDATION COMPLETE - {len(valid)} valid, {dropped} dropped")
    return valid

# === SOURCE SCORING ===
SOURCE_SCORES = {
    "searx": 0.7,
    "firecrawl": 0.5,
    "seed": 1.0,
    "reddit": 0.8,
    "hackernews": 0.9
}

# === QUEUE SYSTEM ===
class SourceQueue:
    def __init__(self):
        self.tasks = []
        self.logs = []
        self.results = []
    def add(self, func, name):
        self.tasks.append((func, name))
    def run(self):
        for func, name in self.tasks:
            log(f"START: {name}")
            data = func()
            count = len(data)
            if count > 0:
                log(f"[SUCCESS] {name} – {count} records")
            else:
                log(f"[FAIL] {name} – 0 records")
            self.logs.append((name, count))
            self.results.extend(data)
        return self.results

# === SOURCES ===
@retry(max_attempts=1, backoff=1)
def fetch_searx():
    url = "https://searx.be/search?q=AI+business+ideas+OR+startup+trends+OR+SaaS+opportunities&format=json"
    headers = {"User-Agent": "Mozilla/5.0 (Team58AI/1.0)"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 403:
            log("SearXNG HTTP 403: Marking SearX as FAILED and skipping for this run.")
            return []
        if resp.status_code != 200:
            log(f"SearXNG HTTP {resp.status_code}: Skipping SearX for this run.")
            return []
        data = resp.json()
        results = []
        for item in data.get("results", []):
            text = item.get("title") or item.get("content")
            if text:
                results.append({
                    "text": text,
                    "source": "searx",
                    "collected_at": str(datetime.now()),
                    "trust_score": SOURCE_SCORES["searx"],
                    "status": "raw",
                    "tags": ["searx"],
                    "processed": False
                })
        return results
    except Exception as e:
        log(f"SearXNG error: {e}. Marking SearX as FAILED and skipping for this run.")
        return []

@retry(max_attempts=1, backoff=1)
def fetch_firecrawl():
    path = Path("data/raw/firecrawl_data.json")
    if not path.exists():
        log("Firecrawl data file not found. Skipping Firecrawl.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    results = []
    if isinstance(data, list):
        for item in data:
            text = item.get("text") or item.get("title")
            if text:
                results.append({
                    "text": text,
                    "source": "firecrawl",
                    "collected_at": str(datetime.now()),
                    "trust_score": SOURCE_SCORES["firecrawl"],
                    "status": "raw",
                    "tags": ["firecrawl"],
                    "processed": False
                })
    elif isinstance(data, dict):
        markdown = data.get("data", {}).get("markdown")
        if markdown:
            for line in markdown.split("\n"):
                line = line.strip()
                if line and not line.startswith("|") and not line.startswith("---"):
                    results.append({
                        "text": line,
                        "source": "firecrawl",
                        "collected_at": str(datetime.now()),
                        "trust_score": SOURCE_SCORES["firecrawl"],
                        "status": "raw",
                        "tags": ["firecrawl"],
                        "processed": False
                    })
    if not results:
        log("Firecrawl returned empty data. Skipping Firecrawl for this run.")
    return results

@retry(max_attempts=1, backoff=1)
def fetch_seed():
    path = Path(SEED_PATH)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    results = []
    for item in data:
        text = item.get("text")
        if text:
            results.append({
                **item,
                "trust_score": SOURCE_SCORES["seed"],
                "collected_at": item.get("collected_at") or str(datetime.now()),
                "source": "seed"
            })
    return results

@retry(max_attempts=1, backoff=1)
def fetch_reddit():
    try:
        from reddit_collector import fetch_reddit as _fetch
        data = _fetch()
    except Exception as e:
        log(f"Reddit fetch error: {e}")
        return []
    results = []
    for item in data:
        text = item.get("text")
        if text:
            record = dict(item)
            record["trust_score"] = SOURCE_SCORES["reddit"]
            record["collected_at"] = item.get("collected_at") or str(datetime.now())
            record["source"] = "reddit"
            results.append(record)
    return results

@retry(max_attempts=1, backoff=1)
def fetch_hn():
    HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
    HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
    HN_LIMIT = 25
    try:
        response = requests.get(HN_TOP_URL, timeout=10)
        response.raise_for_status()
        story_ids = response.json()[:HN_LIMIT]
        results = []
        for sid in story_ids:
            item = requests.get(HN_ITEM_URL.format(sid), timeout=10).json()
            if item and item.get("title"):
                record = {
                    "text": item["title"],
                    "source": "hackernews",
                    "collected_at": str(datetime.now()),
                    "trust_score": SOURCE_SCORES["hackernews"],
                    "status": "raw",
                    "tags": ["hn"],
                    "processed": False
                }
                results.append(record)
        return results
    except Exception as e:
        log(f"HN Error: {e}")
        return []

# === MAIN RUN ===
def run():
    log_phase("STEP 1 — API HEALTH CHECK")
    health_check_serper()
    health_check_qwen()

    log_phase("STEP 2 — DATA COLLECTION LOOP")
    all_data = []
    for attempt in range(2):
        queue = SourceQueue()
        queue.add(fetch_hn, "HackerNews")
        queue.add(fetch_reddit, "Reddit")
        queue.add(fetch_serper, "Serper")
        queue.add(fetch_firecrawl, "Firecrawl")
        queue.add(fetch_searx, "SearXNG")
        batch = queue.run()
        all_data.extend(batch)
        log(f"[TRACE] After fetch (attempt {attempt+1}): {len(all_data)} records")
        if len(all_data) >= 20:
            break
        log("[TRACE] < 20 records, re-running collection loop")
    if len(all_data) < 20:
        log("[SYSTEM] FAILSAFE ACTIVATED - Restoring from seed data")
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            all_data = json.load(f)

    # --- Transform and normalize all records ---
    transformed = []
    for r in all_data:
        src = r.get("source", "unknown").lower()
        out = {}
        # Map Reddit
        if src == "reddit":
            out["title"] = r.get("title") or r.get("text") or r.get("content") or ""
            out["content"] = r.get("selftext") or r.get("content") or r.get("text") or ""
            ts = r.get("created_utc") or r.get("timestamp") or r.get("collected_at")
            if ts:
                try:
                    out["timestamp"] = str(datetime.utcfromtimestamp(float(ts))) if str(ts).isdigit() else str(ts)
                except Exception:
                    out["timestamp"] = str(ts)
            else:
                out["timestamp"] = str(datetime.now())
            out["source"] = "reddit"
        # Map HackerNews
        elif src == "hackernews":
            out["title"] = r.get("title") or r.get("text") or r.get("content") or ""
            out["content"] = r.get("url") or r.get("text") or r.get("content") or ""
            out["timestamp"] = r.get("timestamp") or r.get("collected_at") or str(datetime.now())
            out["source"] = "hackernews"
        # Map Serper
        elif src == "serper":
            out["title"] = r.get("title") or ""
            out["content"] = r.get("content") or ""
            out["timestamp"] = r.get("timestamp") or str(datetime.now())
            out["source"] = "serper"
        # Map Firecrawl
        elif src == "firecrawl":
            out["title"] = r.get("title") or r.get("text") or r.get("content") or ""
            out["content"] = r.get("content") or r.get("text") or ""
            out["timestamp"] = r.get("timestamp") or r.get("collected_at") or str(datetime.now())
            out["source"] = "firecrawl"
        # Map SearX
        elif src == "searx":
            out["title"] = r.get("title") or r.get("text") or r.get("content") or ""
            out["content"] = r.get("content") or r.get("text") or ""
            out["timestamp"] = r.get("timestamp") or r.get("collected_at") or str(datetime.now())
            out["source"] = "searx"
        # Fallback/other
        else:
            out["title"] = r.get("title") or r.get("text") or r.get("content") or ""
            out["content"] = r.get("content") or r.get("text") or ""
            out["timestamp"] = r.get("timestamp") or r.get("collected_at") or str(datetime.now())
            out["source"] = src
        transformed.append(out)
    log(f"[TRACE] After transform: {len(transformed)} records")

    # --- Filter: only drop truly empty records ---
    filtered = []
    dropped = 0
    for r in transformed:
        if not (r["title"].strip() or r["content"].strip()):
            dropped += 1
            continue
        filtered.append(r)
    log(f"[TRACE] After filter: {len(filtered)} kept, {dropped} dropped")

    # --- Deduplicate ---
    seen = set()
    deduped = []
    for r in filtered:
        key = (r["title"].strip().lower(), r["content"].strip().lower(), r["source"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)
    log(f"[TRACE] After deduplication: {len(deduped)} records")

    # --- Validation (schema compliance, but do not drop, just fix) ---
    for r in deduped:
        for field in ("title", "content", "source", "timestamp"):
            if field not in r or not r[field]:
                r[field] = "MISSING"
    log(f"[TRACE] After validation: {len(deduped)} records")

    # --- Final real data count ---
    real_data = [r for r in deduped if r["source"] in ("reddit", "hackernews")]
    log(f"[TRACE] Real data count: {len(real_data)}")

    # --- Fallback only if no real data ---
    if len(real_data) == 0:
        log("[SYSTEM] FAILSAFE ACTIVATED - Restoring from seed data")
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            deduped = json.load(f)
        for r in deduped:
            for field in ("title", "content", "source", "timestamp"):
                if field not in r or not r[field]:
                    r[field] = "MISSING"
        log(f"[TRACE] After fallback: {len(deduped)} records")

    # WRITE GUARD
    if not (isinstance(deduped, list) and len(deduped) > 0 and all(isinstance(r, dict) for r in deduped)):
        log("[GUARD] BLOCKED EMPTY WRITE")
        return
    # WRITE
    path = Path(OUTPUT_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    # READ-BACK VERIFICATION
    with open(path, "r", encoding="utf-8") as f:
        read_back = json.load(f)
    if not (isinstance(read_back, list) and len(read_back) == len(deduped)):
        log("[CRITICAL] WRITE MISMATCH - STOPPING PIPELINE")
        exit(1)
    # FILE INTEGRITY
    sha = hashlib.sha256(json.dumps(deduped, sort_keys=True).encode()).hexdigest()
    log(f"[AGENT] WRITE SUCCESS - {len(deduped)} records | SHA256: {sha}")

if __name__ == "__main__":
    run()
