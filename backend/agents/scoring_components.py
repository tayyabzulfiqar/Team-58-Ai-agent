from agents.scoring_utils import (
    clean_text,
    detect_contact_info,
    detect_cta,
    detect_noise,
    detect_keyword_stuffing,
    extract_words,
    keyword_match_score,
    normalize_url,
    split_sentences,
)


SERVICE_TERMS = (
    "training", "consulting", "consultant", "solutions", "agency", "service",
    "services", "coaching", "program", "programs", "workshop", "course",
)
COMMERCIAL_TERMS = (
    "pricing", "quote", "demo", "book a call", "schedule a call", "get started",
    "contact us", "buy", "purchase", "plan", "plans", "talk to sales",
)
AUTHORITY_TERMS = (
    "testimonial", "testimonials", "case study", "case studies", "clients",
    "trusted by", "certified", "certification", "accredited", "award",
    "awards", "results", "success story", "success stories",
)
EDUCATIONAL_TERMS = (
    "guide", "learn", "curriculum", "framework", "approach", "best practices",
    "strategy", "insights", "resources", "training material",
)


def _count_hits(content: str, terms: tuple[str, ...]) -> int:
    lowered = content.lower()
    return sum(lowered.count(term) for term in terms)


def score_service_relevance(content, query):
    text = clean_text(content)
    hits = _count_hits(text, SERVICE_TERMS)
    query_ratio = keyword_match_score(query, text)

    if hits >= 8 or (hits >= 5 and query_ratio >= 0.7):
        return 5, "Strong service-language coverage with direct offer signals."
    if hits >= 5 or query_ratio >= 0.6:
        return 4, "High service relevance and strong service terminology."
    if hits >= 3 or query_ratio >= 0.45:
        return 3, "Moderate service relevance with useful offer signals."
    if hits >= 1 or query_ratio >= 0.25:
        return 2, "Some service-related language is present."
    if query_ratio > 0:
        return 1, "Weak service relevance with limited evidence."
    return 0, "No meaningful service-oriented signals detected."


def score_intent_match(content, query):
    text = clean_text(content)
    ratio = keyword_match_score(query, text)
    exact_phrase = query.lower() in text.lower()

    if exact_phrase or ratio >= 0.85:
        return 5, "Content strongly matches the user query and intent."
    if ratio >= 0.65:
        return 4, "Content matches most of the query intent."
    if ratio >= 0.5:
        return 3, "Content has a solid but partial intent match."
    if ratio >= 0.3:
        return 2, "Content partially matches the query intent."
    if ratio > 0:
        return 1, "Content only weakly aligns with the query."
    return 0, "Content does not align with the user query."


def score_content_depth(content):
    text = clean_text(content)
    words = extract_words(text)
    sentences = split_sentences(text)
    meaningful_sentences = sum(1 for sentence in sentences if len(extract_words(sentence)) >= 10)

    if len(words) >= 1400 and meaningful_sentences >= 16:
        return 5, "Extensive long-form content with strong depth."
    if len(words) >= 1000 and meaningful_sentences >= 12:
        return 4, "Strong depth with substantial supporting detail."
    if len(words) >= 700 and meaningful_sentences >= 8:
        return 3, "Good content depth with several meaningful sections."
    if len(words) >= 450 and meaningful_sentences >= 6:
        return 2, "Moderate depth with usable detail."
    if len(words) >= 300:
        return 1, "Borderline depth with limited supporting detail."
    return 0, "Thin page with insufficient substance."


def score_authority(url, content):
    text = clean_text(content)
    hits = _count_hits(text, AUTHORITY_TERMS)
    educational_hits = _count_hits(text, EDUCATIONAL_TERMS)
    normalized_url = normalize_url(url).lower()
    domain_bonus = 0

    if normalized_url.endswith(".org/") or ".edu/" in normalized_url or ".gov/" in normalized_url:
        domain_bonus += 1
    if "case-study" in normalized_url or "testimonials" in normalized_url:
        domain_bonus += 1

    total = hits + educational_hits + domain_bonus
    if total >= 7:
        return 4, "Strong authority signals with proof points and educational depth."
    if total >= 4:
        return 3, "Good authority signals with trust markers."
    if total >= 2:
        return 2, "Some authority indicators are present."
    if total >= 1:
        return 1, "Limited authority evidence detected."
    return 0, "No meaningful authority signals found."


def score_contact(content):
    text = clean_text(content)
    cta_hits = detect_cta(text)
    contact_hits = detect_contact_info(text)
    total = cta_hits + contact_hits

    if total >= 4:
        return 3, "Clear contact paths with CTA and direct contact details."
    if total >= 2:
        return 2, "Useful contact signals are present."
    if total >= 1:
        return 1, "A limited contact path is available."
    return 0, "No direct contact information or CTA detected."


def score_commercial_intent(content):
    text = clean_text(content)
    hits = _count_hits(text, COMMERCIAL_TERMS)

    if hits >= 6:
        return 3, "Strong commercial intent with transactional conversion cues."
    if hits >= 3:
        return 2, "Moderate commercial intent with buyer-oriented language."
    if hits >= 1:
        return 1, "Light commercial intent is present."
    return 0, "No clear commercial intent detected."


def score_url_quality(url, query):
    normalized_url = normalize_url(url).lower()
    query_words = [word for word in extract_words(query) if len(word) > 2]
    matches = sum(1 for word in set(query_words) if word in normalized_url)

    if any(token in normalized_url for token in ("privacy", "terms", "login", "signin", "tag", "category")):
        return 0, "URL suggests a low-value utility or archive page."
    if matches >= 2 and normalized_url.count("/") <= 5:
        return 2, "URL path is clean and highly aligned with the query."
    if matches >= 1 or normalized_url.count("/") <= 6:
        return 1, "URL is reasonably clean with partial query alignment."
    return 0, "URL provides weak quality or relevance signals."


def score_noise_penalty(content):
    text = clean_text(content)
    words = extract_words(text)
    noise_hits = detect_noise(text)
    stuffing_ratio = detect_keyword_stuffing(" ".join(words[:8]), text) if words else 0.0

    penalty = 0
    if len(words) < 350:
        penalty -= 1
    if noise_hits >= 6:
        penalty -= 2
    elif noise_hits >= 3:
        penalty -= 1
    if stuffing_ratio >= 0.08:
        penalty -= 1

    penalty = max(-3, penalty)
    if penalty == 0:
        return 0, "Low noise profile with no major penalties."
    if penalty == -1:
        return -1, "Minor noise or thin-page traits reduced confidence."
    if penalty == -2:
        return -2, "Noticeable noise or weak content quality reduced value."
    return -3, "Heavy noise or spam-like traits strongly reduced value."
