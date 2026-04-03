def clamp01(x):
    try:
        return max(0.0, min(float(x), 1.0))
    except Exception:
        return 0.0
import html
import re
from urllib.parse import urlsplit, urlunsplit


SCRIPT_STYLE_RE = re.compile(r"(?is)<(script|style)\b.*?>.*?</\1>")
TAG_RE = re.compile(r"(?is)<[^>]+>")
MULTISPACE_RE = re.compile(r"\s+")
WORD_RE = re.compile(r"\b[a-zA-Z][a-zA-Z'-]*\b")
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_RE = re.compile(r"(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)\d{3}[\s.-]?\d{4}")
FORM_RE = re.compile(r"\b(contact us|get in touch|book a demo|schedule a call|request a quote|talk to sales)\b", re.IGNORECASE)
LOCATION_RE = re.compile(
    r"\b(new york|california|texas|florida|london|dubai|uae|united states|usa|uk|canada|australia|remote)\b",
    re.IGNORECASE,
)
TITLE_SPLIT_RE = re.compile(r"\s*[|\-–:]\s*")
CTA_PATTERNS = [
    r"\bcontact\s+us\b",
    r"\bbook\s+(?:a|your)\s+(?:call|demo|meeting)\b",
    r"\bschedule\s+(?:a|your)\s+(?:call|demo|consultation)\b",
    r"\brequest\s+(?:a\s+)?quote\b",
    r"\bget\s+started\b",
    r"\bcall\s+now\b",
    r"\bemail\s+us\b",
    r"\bapply\s+now\b",
    r"\bstart\s+today\b",
    r"\btalk\s+to\s+sales\b",
]
NOISE_PATTERNS = [
    r"\blog[\s-]*in\b",
    r"\bsign[\s-]*in\b",
    r"\bsign[\s-]*up\b",
    r"\bprivacy\s+policy\b",
    r"\bterms(?:\s+of\s+(?:service|use))?\b",
    r"\bcookie(?:\s+policy)?\b",
    r"\bmenu\b",
    r"\bnavigation\b",
    r"\bsubscribe\b",
    r"\bunsubscribe\b",
    r"\bnewsletter\b",
    r"\b404\b",
    r"\bpage\s+not\s+found\b",
    r"\berror\b",
]
SPAM_PATH_PATTERNS = (
    "/tag/",
    "/tags/",
    "/category/",
    "/categories/",
    "/author/",
    "/search",
    "/wp-login",
    "/login",
    "/signup",
    "/sign-up",
)
NON_HTML_SUFFIXES = (
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".webp",
    ".zip",
)

CTA_REGEXES = [re.compile(pattern, re.IGNORECASE) for pattern in CTA_PATTERNS]
NOISE_REGEXES = [re.compile(pattern, re.IGNORECASE) for pattern in NOISE_PATTERNS]


def clean_text(raw_text) -> str:
    if not isinstance(raw_text, str):
        return ""

    text = html.unescape(raw_text)
    text = SCRIPT_STYLE_RE.sub(" ", text)
    text = TAG_RE.sub(" ", text)
    text = text.replace("\r", "\n")

    lines = []
    seen = set()
    for raw_line in text.split("\n"):
        line = MULTISPACE_RE.sub(" ", raw_line).strip()
        if not line:
            continue
        lowered = line.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        lines.append(line)

    return MULTISPACE_RE.sub(" ", "\n".join(lines)).strip()


def extract_words(text: str) -> list[str]:
    if not text:
        return []
    return WORD_RE.findall(text.lower())


def word_count(text: str) -> int:
    return len(extract_words(text))


def split_sentences(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def keyword_match_score(query: str, content: str) -> float:
    query_terms = [word for word in extract_words(query) if len(word) > 2]
    if not query_terms:
        return 0.0

    content_words = set(extract_words(content))
    matched = sum(1 for word in set(query_terms) if word in content_words)
    return matched / max(len(set(query_terms)), 1)


def detect_cta(content: str) -> int:
    lowered = content.lower()
    return sum(len(pattern.findall(lowered)) for pattern in CTA_REGEXES)


def detect_contact_info(content: str) -> int:
    return len(EMAIL_RE.findall(content)) + len(PHONE_RE.findall(content))


def extract_contact_info(content: str) -> dict:
    emails = EMAIL_RE.findall(content)
    phones = PHONE_RE.findall(content)
    return {
        "email": emails[0] if emails else "",
        "phone": phones[0] if phones else "",
        "form": bool(FORM_RE.search(content or "")),
    }


def detect_noise(content: str) -> int:
    lowered = content.lower()
    return sum(len(pattern.findall(lowered)) for pattern in NOISE_REGEXES)


def compute_intent_score(text):
    lowered = (text or "").lower()
    strong_hits = sum(
        keyword in lowered
        for keyword in ["get quote", "buy now", "apply now", "start policy", "instant quote", "request a quote", "book a demo"]
    )
    medium_hits = sum(
        keyword in lowered
        for keyword in ["insurance services", "coverage plans", "policy options", "sales training", "consulting", "service", "contact us"]
    )
    weak_hits = sum(keyword in lowered for keyword in ["what is", "guide", "benefits of", "learn"])

    if strong_hits >= 1:
        return 0.95
    if medium_hits >= 3:
        return 0.85
    if medium_hits >= 1:
        return 0.75
    if weak_hits >= 1:
        return 0.45
    return 0.55


def compute_actionability(html, text):
    lowered_html = (html or "").lower()
    lowered_text = (text or "").lower()
    score = 0.0

    if "<form" in lowered_html:
        score += 0.4
    if any(keyword in lowered_text for keyword in ["get quote", "call now", "apply", "buy", "start", "contact us", "book a demo", "request a quote"]):
        score += 0.3
    if "tel:" in lowered_html or "mailto:" in lowered_html or EMAIL_RE.search(text or "") or PHONE_RE.search(text or ""):
        score += 0.2
    if any(keyword in lowered_text for keyword in ["service", "services", "training", "consulting", "solutions", "program", "coaching"]):
        score += 0.25
    if len(text or "") < 3000:
        score += 0.1

    return min(score, 1.0)


def compute_content_score(text):
    lowered = (text or "").lower()
    hits = sum(1 for keyword in ["insurance", "policy", "premium", "coverage", "claim", "quote", "agent", "plan"] if keyword in lowered)
    score = hits / 8
    text_length = len(extract_words(text or ""))
    if text_length >= 400:
        score += 0.15
    if text_length >= 800:
        score += 0.15
    if text_length >= 1200:
        score += 0.1
    return min(score, 1.0)


def compute_trust_score(text):
    lowered = (text or "").lower()
    hits = sum(1 for keyword in ["trusted by", "reviews", "testimonials", "since", "years", "clients", "rating"] if keyword in lowered)
    bonus_hits = sum(
        1
        for keyword in ["certified", "accredited", "case study", "results", "award", "experience"]
        if keyword in lowered
    )
    score = (hits / 6) + (bonus_hits * 0.18)
    if bonus_hits >= 2:
        score += 0.1
    return min(score, 1.0)


def detect_page_type(html, text):
    lowered_html = (html or "").lower()
    lowered_text = (text or "").lower()

    if "<form" in lowered_html and "quote" in lowered_text:
        return "lead_capture"
    if "compare" in lowered_text or "multiple providers" in lowered_text:
        return "aggregator"
    if "blog" in lowered_text or "guide" in lowered_text:
        return "blog"
    if "services" in lowered_text or "coverage" in lowered_text:
        return "service_page"
    return "other"


def compute_final_score(html, text):
    intent = clamp01(compute_intent_score(text))
    actionability = clamp01(compute_actionability(html, text))
    content = clamp01(compute_content_score(text))
    trust = clamp01(compute_trust_score(text))

    final_score = (
        intent * 0.35 +
        actionability * 0.30 +
        content * 0.20 +
        trust * 0.15
    )
    final_score = clamp01(final_score)

    return {
        "score": round(final_score, 4),
        "intent": round(intent, 2),
        "actionability": round(actionability, 2),
        "content": round(content, 2),
        "trust": round(trust, 2),
    }


def normalize_url(url: str) -> str:
    if not isinstance(url, str):
        return ""

    split = urlsplit(url.strip())
    scheme = split.scheme.lower() or "https"
    netloc = split.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = split.path.rstrip("/") or "/"
    return urlunsplit((scheme, netloc, path, split.query, ""))


def extract_domain(url: str) -> str:
    normalized = normalize_url(url)
    return urlsplit(normalized).netloc


def is_non_html_url(url: str) -> bool:
    return normalize_url(url).lower().endswith(NON_HTML_SUFFIXES)


def is_spammy_path(url: str) -> bool:
    normalized = normalize_url(url).lower()
    return any(pattern in normalized for pattern in SPAM_PATH_PATTERNS)


def compute_unique_word_ratio(text: str) -> float:
    words = extract_words(text)
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def detect_keyword_stuffing(query: str, content: str) -> float:
    query_terms = [word for word in extract_words(query) if len(word) > 2]
    words = extract_words(content)
    if not query_terms or not words:
        return 0.0

    total_hits = sum(words.count(term) for term in set(query_terms))
    return total_hits / len(words)


def classify_content_type(url: str, content: str) -> str:
    normalized_url = normalize_url(url).lower()
    lowered = content.lower()

    if any(token in normalized_url for token in ("/blog/", "/guide", "/article", "/learn/", "/resources/")):
        return "blog"
    if any(token in normalized_url for token in ("/tool", "/software", "/platform", "/directory", "/list", "/top-")):
        return "directory"
    if detect_cta(content) >= 2 and any(term in lowered for term in ("service", "training", "consulting", "solutions")):
        return "landing_page"
    if any(term in lowered for term in ("service", "training", "consulting", "solutions", "agency")):
        return "service_page"
    return "resource"


def extract_company_name(url: str, content: str) -> str:
    text = clean_text(content)
    first_line = text.split(". ")[0].strip() if text else ""
    if first_line:
        title = TITLE_SPLIT_RE.split(first_line)[0].strip()
        title_words = title.split()
        invalid_title = any(token in title for token in ("http", "![", "](", "://"))
        if not invalid_title and 1 <= len(title_words) <= 8 and any(word[:1].isupper() for word in title_words):
            return title

    domain = extract_domain(url)
    if not domain:
        return ""
    parts = domain.split(".")
    generic_subdomains = {"www", "go", "app", "blog", "info", "staging"}
    company_part = parts[0]
    if len(parts) >= 3 and parts[0] in generic_subdomains:
        company_part = parts[-2]
    company = company_part.replace("-", " ").replace("_", " ").strip()
    return " ".join(part.capitalize() for part in company.split())


def extract_service_type(content: str) -> str:
    lowered = clean_text(content).lower()
    service_map = (
        ("insurance sales training", "insurance sales training"),
        ("sales training", "sales training"),
        ("consulting", "consulting"),
        ("coaching", "coaching"),
        ("agency", "agency services"),
        ("solutions", "business solutions"),
        ("course", "course"),
        ("program", "training program"),
    )
    for keyword, label in service_map:
        if keyword in lowered:
            return label
    return "general service"


def extract_target_market(content: str) -> str:
    lowered = clean_text(content).lower()
    market_map = (
        ("insurance", "insurance"),
        ("b2b", "b2b"),
        ("enterprise", "enterprise"),
        ("agencies", "agencies"),
        ("teams", "sales teams"),
        ("brokers", "brokers"),
    )
    for keyword, label in market_map:
        if keyword in lowered:
            return label
    return "general market"


def extract_location(content: str) -> str:
    match = LOCATION_RE.search(content or "")
    return match.group(1) if match else ""


def extract_entity_profile(url: str, content: str) -> dict:
    contact_info = extract_contact_info(content)
    return {
        "company_name": extract_company_name(url, content),
        "service_type": extract_service_type(content),
        "target_market": extract_target_market(content),
        "location": extract_location(content),
        "contact_info": contact_info,
    }


def compute_actionability_score(content: str, breakdown: dict, entity: dict) -> float:
    contact_info = entity.get("contact_info", {})
    has_email = bool(contact_info.get("email"))
    has_phone = bool(contact_info.get("phone"))
    has_form = bool(contact_info.get("form"))
    cta_hits = detect_cta(content)
    service_strength = 1.0 if breakdown.get("service_relevance", 0) >= 4 else 0.5 if breakdown.get("service_relevance", 0) >= 2 else 0.0
    geo_strength = 0.2 if entity.get("location") else 0.0

    contact_strength = 0.0
    if has_email or has_phone:
        contact_strength += 0.45
    if has_form:
        contact_strength += 0.25

    cta_strength = min(cta_hits / 3, 1.0) * 0.25
    score = contact_strength + cta_strength + (service_strength * 0.25) + geo_strength
    if not (has_email or has_phone or has_form):
        score = min(score, 0.35)

    return round(max(0.0, min(score, 1.0)), 2)
