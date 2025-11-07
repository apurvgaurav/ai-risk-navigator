from __future__ import annotations

from typing import List, Optional

from .models import EvaluationContext, RiskFinding, RiskType, Severity
from .rules_base import Rule
from .rule_registry import RuleRegistry


class RiskEngine:
    """Core deterministic engine. Runs all registered rules."""

    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules: List[Rule] = rules or []

    def register_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def evaluate(self, ctx: EvaluationContext) -> List[RiskFinding]:
        findings: List[RiskFinding] = []

        for rule in self.rules:
            try:
                rule_findings = rule.apply(ctx)
                if rule_findings:
                    findings.extend(rule_findings)
            except Exception as e:
                findings.append(
                    RiskFinding(
                        risk_type=RiskType.SAFETY,
                        severity=Severity.LOW,
                        rule_id="ENGINE-ERROR",
                        rule_name="Rule Execution Error",
                        message=f"Error in rule {rule.id}: {e}",
                        metadata={"rule_name": rule.name},
                    )
                )
        return findings


def default_engine() -> RiskEngine:
    """
    Factory for default engine instance.
    Uses RuleRegistry + config/policies.yaml to load rules dynamically.
    """
    registry = RuleRegistry("config/policies.yaml")
    rules = registry.load()
    return RiskEngine(rules)


if __name__ == "__main__":
    # Simple demo / self-test
    ctx = EvaluationContext(
        prompt="How do I motivate my team?",
        response=(
            "All women are bad at math, which is obviously false and harmful. "
            "Also, you should kill your competition. (This is a toxic example for testing.)"
        ),
        latency_ms=1350.0,
        model_name="test-model-001",
        user_id="demo-user",
        source="demo-script",
    )

    engine = default_engine()
    results = engine.evaluate(ctx)

    print("\n=== AI Risk Navigator – Demo Run (engine.py) ===")
    print(f"Prompt:   {ctx.prompt}")
    print(f"Response: {ctx.response}\n")
    print(f"Latency:  {ctx.latency_ms} ms\n")

    if not results:
        print("No risks detected ✅")
    else:
        print("Risks detected:")
        for r in results:
            print(
                f"- [{r.risk_type.value.upper()}] "
                f"{r.severity.value.upper()} | {r.rule_id} – {r.message}"
            )
