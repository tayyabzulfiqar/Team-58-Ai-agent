from agents.scoring_utils import extract_words
from models.score_schema import IntentAnalysis


TRANSACTIONAL_TERMS = {
    "buy", "hire", "service", "services", "agency", "consulting", "consultant",
    "training", "course", "pricing", "price", "quote", "demo", "sales",
}
INFORMATIONAL_TERMS = {
    "what", "how", "guide", "best", "top", "tips", "compare", "comparison",
    "examples", "learn", "overview",
}
NAVIGATIONAL_TERMS = {
    "login", "signin", "sign", "dashboard", "website", "official", "homepage",
    "contact", "support",
}
URGENT_TERMS = {"now", "today", "urgent", "fast", "quick", "immediately"}


def normalize_query(query: str) -> str:
    return " ".join((query or "").strip().lower().split())


def analyze_intent(query: str) -> IntentAnalysis:
    normalized_query = normalize_query(query)
    words = set(extract_words(normalized_query))

    transactional_score = len(words & TRANSACTIONAL_TERMS)
    informational_score = len(words & INFORMATIONAL_TERMS)
    navigational_score = len(words & NAVIGATIONAL_TERMS)

    if navigational_score > max(transactional_score, informational_score):
        intent_type = "navigational"
    elif transactional_score >= informational_score:
        intent_type = "transactional"
    else:
        intent_type = "informational"

    if intent_type == "transactional":
        buyer_stage = "decision" if words & {"buy", "hire", "pricing", "quote", "demo"} else "consideration"
    elif intent_type == "informational":
        buyer_stage = "awareness"
    else:
        buyer_stage = "consideration"

    urgency = 2
    if intent_type == "transactional":
        urgency = 4
    elif intent_type == "navigational":
        urgency = 3

    if words & URGENT_TERMS:
        urgency = min(5, urgency + 1)

    return {
        "intent_type": intent_type,
        "buyer_stage": buyer_stage,
        "urgency": urgency,
    }
