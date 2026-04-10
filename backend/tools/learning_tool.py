from core.logging_utils import get_logger
from memory.store import successful_outcomes


logger = get_logger("team58.learning")

BASE_WEIGHTS = {
    "trend_strength": 0.4,
    "competition_gap": 0.3,
    "demand_signal": 0.3,
}


def learning_state() -> dict:
    strategies = ["Performance marketing", "Emotional marketing", "Brand awareness"]
    successful_counts = {strategy: len(successful_outcomes(strategy)) for strategy in strategies}
    total_successes = sum(successful_counts.values())

    state = {
        "weights": BASE_WEIGHTS,
        "successful_patterns": successful_counts,
        "total_successes": total_successes,
        "learning_active": total_successes > 0,
    }
    logger.info("learning:state total_successes=%s", total_successes)
    return state
