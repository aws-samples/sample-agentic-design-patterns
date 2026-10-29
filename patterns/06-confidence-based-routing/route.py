from dataclasses import dataclass

AUTO_ACCEPT: set[str] = {"high"}

@dataclass
class RoutingDecision:
    finding: Finding
    requires_review: bool
    reason: str | None = None

def route_finding(finding: Finding) -> RoutingDecision:
    if finding.confidence not in AUTO_ACCEPT:
        return RoutingDecision(
            finding,
            requires_review=True,
            reason=f"confidence '{finding.confidence}' not in auto-accept set",
        )
    return RoutingDecision(finding, requires_review=False)

def route_result(result: SubagentResult) -> tuple[list[RoutingDecision], list[RoutingDecision]]:
    auto, review = [], []
    for finding in result.findings:
        d = route_finding(finding)
        (review if d.requires_review else auto).append(d)
    return auto, review
