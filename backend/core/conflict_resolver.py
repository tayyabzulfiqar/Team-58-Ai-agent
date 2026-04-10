def resolve_signal_conflicts(pattern_signals: dict, semantic_signals: dict) -> dict:
    final_signals = []
    conflicts = []
    resolution_strategy = "no_conflicts"

    all_names = sorted(set(pattern_signals.keys()) | set(semantic_signals.keys()))
    for name in all_names:
        pattern_item = pattern_signals.get(name)
        semantic_item = semantic_signals.get(name)

        if pattern_item and not semantic_item:
            final_signals.append(
                {
                    "name": name,
                    "confidence": pattern_item["confidence"],
                    "score": pattern_item.get("score", pattern_item["confidence"] * 100),
                    "evidence": list(pattern_item.get("evidence", [])),
                    "source": "pattern",
                }
            )
            continue

        if semantic_item and not pattern_item:
            final_signals.append(
                {
                    "name": name,
                    "confidence": semantic_item["confidence"],
                    "score": semantic_item.get("score", semantic_item["confidence"] * 100),
                    "evidence": list(semantic_item.get("evidence", [])),
                    "source": "semantic",
                }
            )
            continue

        pattern_confidence = float(pattern_item["confidence"])
        semantic_confidence = float(semantic_item["confidence"])
        merged_evidence = sorted(set(pattern_item.get("evidence", []) + semantic_item.get("evidence", [])))

        if semantic_confidence > pattern_confidence:
            chosen = {
                "name": name,
                "confidence": semantic_confidence,
                "score": semantic_item.get("score", semantic_confidence * 100),
                "evidence": merged_evidence,
                "source": "semantic",
            }
            strategy = "prefer_semantic"
        elif pattern_confidence > 0.75:
            chosen = {
                "name": name,
                "confidence": pattern_confidence,
                "score": pattern_item.get("score", pattern_confidence * 100),
                "evidence": merged_evidence,
                "source": "pattern",
            }
            strategy = "override_with_pattern"
        else:
            blended_confidence = round((pattern_confidence + semantic_confidence) / 2.0, 3)
            chosen = {
                "name": name,
                "confidence": blended_confidence,
                "score": round((pattern_item.get("score", 0.0) + semantic_item.get("score", 0.0)) / 2.0, 2),
                "evidence": merged_evidence,
                "source": "blended",
            }
            strategy = "keep_both"

        conflicts.append(
            {
                "signal": name,
                "pattern_confidence": round(pattern_confidence, 3),
                "semantic_confidence": round(semantic_confidence, 3),
                "resolved_with": strategy,
            }
        )
        final_signals.append(chosen)

    if conflicts:
        strategies = {item["resolved_with"] for item in conflicts}
        if len(strategies) == 1:
            resolution_strategy = list(strategies)[0]
        else:
            resolution_strategy = "mixed"

    final_signals.sort(key=lambda item: (-item["confidence"], -item["score"], item["name"]))
    return {
        "final_signals": final_signals,
        "conflicts": conflicts,
        "resolution_strategy": resolution_strategy,
    }
