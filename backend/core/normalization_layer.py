import re


PHRASE_REPLACEMENTS = (
    ("samajh nahi aa raha", "do not understand"),
    ("aa rahe", "coming"),
    ("aa raha", "coming"),
    ("aa rahi", "coming"),
    ("kar rahe", "doing"),
    ("chod dete", "leave"),
    ("rukte nahi", "do not stay"),
    ("wapas nahi aate", "do not return"),
    ("use nahi karte", "do not use"),
    ("uninstall kar dete", "uninstall"),
    ("paisa ja raha", "money is being spent"),
    ("fayda nahi", "no benefit"),
    ("chalay jate", "leave"),
    ("chale jate", "leave"),
)

WORD_REPLACEMENTS = {
    "nahi": "not",
    "nai": "not",
    "nahin": "not",
    "aa": "coming",
    "rha": "raha",
    "rhy": "rahe",
    "gayab": "disappear",
    "paisa": "money",
    "fayda": "benefit",
    "kya": "what",
    "ho": "is",
    "raha": "happening",
    "trafic": "traffic",
    "runing": "running",
    "convertion": "conversion",
    "converstion": "conversion",
    "sale": "sales",
    "purchse": "purchase",
    "puchase": "purchase",
    "visiter": "visitor",
    "signup": "sign up",
    "signups": "sign ups",
}

NOISE_WORDS = {
    "bro",
    "yaar",
    "yar",
    "bhai",
    "idk",
    "pls",
    "please",
}

ROMAN_URDU_TERMS = {
    "nahi",
    "nai",
    "aa",
    "raha",
    "rahe",
    "kar",
    "kya",
    "ho",
    "paisa",
    "fayda",
    "rukte",
    "chod",
    "jate",
    "wapas",
    "bilkul",
    "thora",
    "chal",
    "lag",
    "rahi",
    "hain",
    "hai",
    "hota",
    "hoti",
    "se",
    "pe",
    "ke",
    "mein",
}

ENGLISH_HINTS = {
    "traffic",
    "users",
    "sales",
    "sale",
    "conversion",
    "conversions",
    "revenue",
    "profit",
    "growth",
    "retention",
    "churn",
    "bounce",
    "website",
    "site",
    "app",
    "business",
    "click",
    "clicks",
    "purchase",
    "buying",
    "buy",
    "campaign",
    "ads",
    "ad",
    "seo",
    "ranking",
    "google",
    "ctr",
    "cpc",
    "roi",
    "cost",
    "lead",
    "leads",
    "quality",
    "signup",
    "signups",
    "engagement",
    "content",
    "landing",
    "page",
    "pricing",
    "issue",
    "low",
    "high",
    "slow",
    "stagnant",
    "dropped",
    "declined",
    "decreased",
    "reduced",
}

SHORT_ENGLISH_TOKENS = {"a", "i", "is", "are", "to", "on", "in", "of", "no", "not", "but", "or", "and"}

GRAMMAR_PATTERNS = (
    (r"\busers coming no buying\b", "users are coming but not buying"),
    (r"\btraffic coming no sales\b", "traffic is coming but no sales"),
    (r"\bpeople sign up then disappear\b", "people sign up and then disappear"),
    (r"\bads running money going no results\b", "ads are running and money is going but no results"),
)


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _clean_tokens(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9']+", text.lower())
    cleaned: list[str] = []
    for token in tokens:
        if token in NOISE_WORDS:
            continue
        replacement = WORD_REPLACEMENTS.get(token, token)
        cleaned.extend(replacement.split())
    return cleaned


def _is_english_like_token(token: str) -> bool:
    if not token:
        return False
    if token in ENGLISH_HINTS or token in SHORT_ENGLISH_TOKENS:
        return True
    if token in ROMAN_URDU_TERMS:
        return False
    if token in WORD_REPLACEMENTS:
        replacement = WORD_REPLACEMENTS[token]
        replacement_parts = re.findall(r"[a-z0-9']+", replacement.lower())
        return any(part in ENGLISH_HINTS or part in SHORT_ENGLISH_TOKENS for part in replacement_parts)
    if len(token) <= 2:
        return token in SHORT_ENGLISH_TOKENS
    if re.fullmatch(r"[a-z]+", token):
        return True
    return False


def _detect_language_profile(text: str) -> str:
    tokens = re.findall(r"[a-z0-9']+", text.lower())
    if not tokens:
        return "english"

    meaningful_tokens = [token for token in tokens if token not in NOISE_WORDS and len(token) > 1]
    if not meaningful_tokens:
        return "english"

    normalized_tokens: list[str] = []
    for token in meaningful_tokens:
        replacement = WORD_REPLACEMENTS.get(token, token)
        normalized_tokens.extend(re.findall(r"[a-z0-9']+", replacement.lower()))
    normalized_tokens = [token for token in normalized_tokens if token not in NOISE_WORDS and len(token) > 1]
    if not normalized_tokens:
        normalized_tokens = meaningful_tokens

    english_hits = sum(1 for token in normalized_tokens if _is_english_like_token(token))
    roman_hits = sum(1 for token in normalized_tokens if token in ROMAN_URDU_TERMS)
    denominator = max(1, len(normalized_tokens))
    english_ratio = english_hits / denominator
    roman_ratio = roman_hits / denominator

    if english_ratio > 0.8:
        return "english"

    if roman_ratio > 0.55 and english_ratio < 0.25:
        return "roman_urdu"
    if roman_ratio > 0.30 and english_ratio >= 0.25:
        return "hinglish"
    if english_ratio >= 0.45:
        return "english"
    if roman_ratio > 0.0 and english_ratio > 0.0:
        return "hinglish"
    return "english"


def normalize_input(text: str) -> dict:
    raw = _normalize_whitespace(str(text or "").lower())
    if not raw:
        return {"canonical_text": "", "language_profile": "english", "confidence": 0.0}

    language_profile = _detect_language_profile(raw)

    for source, target in PHRASE_REPLACEMENTS:
        raw = raw.replace(source, target)
    for pattern, replacement in GRAMMAR_PATTERNS:
        raw = re.sub(pattern, replacement, raw)

    cleaned_tokens = _clean_tokens(raw)
    if not cleaned_tokens:
        return {"canonical_text": "", "language_profile": language_profile, "confidence": 0.0}

    canonical_text = _normalize_whitespace(" ".join(cleaned_tokens))

    token_count = len(cleaned_tokens)
    unique_ratio = len(set(cleaned_tokens)) / token_count if token_count else 0.0
    has_business_shape = any(
        phrase in canonical_text
        for phrase in (
            "no sales",
            "not buying",
            "not using",
            "traffic",
            "users",
            "ads",
            "seo",
            "conversion",
            "retention",
            "churn",
            "growth",
            "rank",
            "google",
        )
    )
    base = 0.45 + min(0.35, unique_ratio * 0.35)
    language_bonus = 0.08 if language_profile in {"hinglish", "roman_urdu", "mixed"} else 0.0
    confidence = min(1.0, base + (0.2 if has_business_shape else 0.0) + language_bonus)
    return {
        "canonical_text": canonical_text,
        "language_profile": language_profile,
        "confidence": round(confidence, 3),
    }


def normalize_user_input(text: str) -> str:
    return normalize_input(text).get("canonical_text", "")
