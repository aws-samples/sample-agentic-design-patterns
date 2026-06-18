def detect_conflicts(findings: list[Finding]) -> list[ConflictRecord]:
    topic_groups: dict[str, list[Finding]] = {}
    for finding in findings:
        topic_key = " ".join(finding.claim.lower().split()[:5])
        topic_groups.setdefault(topic_key, []).append(finding)

    conflicts = []
    for topic, group in topic_groups.items():
        if len(group) < 2:
            continue
        sources = {f.source_url for f in group if f.source_url is not None}
        if len(sources) < 2:
            continue        # same source — not a real conflict
        if all(f.confidence > 0.5 for f in group):
            conflicts.append(ConflictRecord(
                topic=topic,
                conflicting_claims=[f.model_dump() for f in group],
                resolution="unresolved",
            ))
    return conflicts

def reorder_for_synthesis(findings: list[Finding]) -> list[Finding]:
    """Place highest-importance findings at the beginning and end."""
    ranked = sorted(findings, key=lambda f: f.confidence, reverse=True)
    half = len(ranked) // 2
    front, back = ranked[:half], ranked[half:]
    return front + list(reversed(back))
