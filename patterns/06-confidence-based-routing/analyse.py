from collections import Counter

def analyse_confidence(results: list[SubagentResult]) -> dict:
    by_source: dict[str, Counter] = {}
    for r in results:
        for f in r.findings:
            by_source.setdefault(f.source_type, Counter())[f.confidence] += 1
    return {
        t: {
            "counts": dict(counts),
            "review_rate": round(1 - counts["high"] / max(sum(counts.values()), 1), 3),
            "total": sum(counts.values()),
        }
        for t, counts in by_source.items()
    }
