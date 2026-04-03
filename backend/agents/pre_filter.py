import hashlib
def _hash_content(item):
    content = item.get('content', '')
    return hashlib.md5(content.encode('utf-8')).hexdigest() if content else None

def remove_duplicates(items):
    seen = set()
    deduped = []
    for item in items:
        h = _hash_content(item)
        if h and h not in seen:
            seen.add(h)
            deduped.append(item)
    return deduped
from agents.scoring_utils import (
    clean_text,
    classify_content_type,
    detect_noise,
    extract_domain,
    is_non_html_url,
    is_spammy_path,
    normalize_url,
    split_sentences,
    word_count,
)


BLOCKED_CONTENT_TERMS = (
    "page not found",
    "404",
    "sign in",
    "log in",
    "subscribe to continue",
    "access denied",
)
HARD_FILTER_TERMS = (
    "login",
    "sign in",
    "privacy policy",
    "terms",
    "menu",
    "subscribe",
)
HARD_FILTER_PATHS = (
    "/login",
    "/signup",
    "/tag/",
    "/category/",
)


def hard_filter(item):
    if not isinstance(item, dict):
        return False, "invalid_item"

    url = normalize_url(item.get("url", ""))
    content = clean_text(item.get("content", ""))
    lowered = content.lower()

    if not url or not content:
        return False, "broken_page"
    if is_non_html_url(url):
        return False, "non_html"
    if is_spammy_path(url):
        return False, "spam_path"
    if len(content) < 200:
        return False, "thin_content"
    if any(term in lowered for term in HARD_FILTER_TERMS):
        return False, "system_page"
    if any(path in url.lower() for path in HARD_FILTER_PATHS):
        return False, "non_content_url"
    if any(term in lowered for term in BLOCKED_CONTENT_TERMS):
        return False, "broken_page"

    words = word_count(content)
    sentences = len(split_sentences(content))
    if words < 150 or sentences < 3:
        return False, "low_density"
    if detect_noise(content) >= 10:
        return False, "spam_path"

    return True, "ok"


def pre_filter_results(results: list) -> tuple[list, dict]:
    items = results if isinstance(results, list) else []
    # Remove duplicates first
    items = remove_duplicates(items)
    removed = {
        "invalid_item": 0,
        "non_html": 0,
        "spam_path": 0,
        "broken_page": 0,
        "thin_content": 0,
    }
    filtered = []

    for item in items:
        if not isinstance(item, dict):
            removed["invalid_item"] += 1
            continue

        is_valid, reason = hard_filter(item)
        if not is_valid:
            removed[reason] = removed.get(reason, 0) + 1
            continue

        url = normalize_url(item.get("url", ""))
        content = clean_text(item.get("content", ""))

        filtered.append(
            {
                "url": url,
                "domain": extract_domain(url),
                "content": content,
                "word_count": word_count(content),
                "content_type": classify_content_type(url, content),
            }
        )

    print(f"🧹 PRE-FILTER REMOVED: {sum(removed.values())}")
    print(f"🧾 PRE-FILTER REASONS: {removed}")
    print(f"✅ PRE-FILTER KEPT: {len(filtered)}")
    return filtered, removed
