INPUT_CONTRACT_KEYS = ("query",)

ALLOWED_SIGNAL_CONFIDENCE = {"low", "medium", "high"}
ALLOWED_SIGNAL_STATUS = {"competing", "confirmed", "low_confidence"}
ALLOWED_SIGNAL_PRIORITY = {"low", "medium", "high"}
ALLOWED_CLUSTER_PRIORITY = {"high", "medium"}

CLUSTER_RULES = [
    {
        "name": "funnel optimization",
        "requires": ("lead generation", "conversion optimization"),
        "minimum_matches": 2,
    },
    {
        "name": "funnel issue",
        "requires": ("conversion optimization", "retention"),
        "minimum_matches": 2,
    },
    {
        "name": "organic growth",
        "requires": ("seo", "content marketing"),
        "minimum_matches": 2,
    },
    {
        "name": "paid growth",
        "requires": ("paid ads", "performance marketing"),
        "minimum_matches": 2,
    },
    {
        "name": "growth",
        "requires": ("lead generation", "seo", "paid ads"),
        "minimum_matches": 3,
    },
]


def contract_fallback() -> dict:
    return {
        "signals": [],
        "clusters": [],
        "strategy_options": [],
        "status": "safe_fallback",
    }


ENFORCED_GUARANTEES = [
    "Input must be an object with a non-empty string query.",
    "Signals must match the exact contract shape and enum bounds.",
    "Signal scores are bounded to 0-50 and duplicates are rejected.",
    "Relevance may change priority, not signal existence unless the signal is invalid.",
    "Competing signals cannot exceed medium confidence; low_confidence signals are always low confidence.",
    "Clusters must contain at least two existing signals and use a valid cluster priority.",
    "If a defined multi-signal relationship is fully present, the corresponding cluster must exist.",
    "strategy_options may only include high-priority signals that are not already clustered.",
    "strategy_conflicts must contain at least two existing signal options whenever present.",
    "Any contract failure returns the safe_fallback JSON instead of crashing.",
]
