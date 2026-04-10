THRESHOLDS = {
    "signal_base": 0.45,
    "domain_base": 0.40,
}


def compute_thresholds(
    normalization_confidence: float,
    validation_type: str,
    segment_count: int,
) -> dict:
    domain_threshold = float(THRESHOLDS["domain_base"])
    signal_threshold = float(THRESHOLDS["signal_base"])

    if normalization_confidence < 0.6:
        domain_threshold *= 0.88
        signal_threshold *= 0.88
    elif normalization_confidence > 0.8:
        domain_threshold *= 1.08
        signal_threshold *= 1.08

    if validation_type == "valid_weak":
        domain_threshold *= 0.95
        signal_threshold *= 0.95

    if segment_count >= 3:
        signal_threshold *= 0.92

    domain_threshold = max(0.20, min(0.90, round(domain_threshold, 3)))
    signal_threshold = max(0.20, min(0.90, round(signal_threshold, 3)))

    return {
        "domain": domain_threshold,
        "signal": signal_threshold,
    }
