from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List

from .models import EvaluationContext, RiskFinding


def log_results(
    ctx: EvaluationContext,
    findings: List[RiskFinding],
    log_path: str = "logs/risks.jsonl",
) -> None:
    """
    Append a JSON line with context + findings to logs/risks.jsonl.
    Creates the logs/ folder if it doesn't exist.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "prompt": ctx.prompt,
        "response": ctx.response,
        "latency_ms": ctx.latency_ms,
        "model_name": ctx.model_name,
        "user_id": ctx.user_id,
        "source": ctx.source,
        "extra": ctx.extra,
        "findings": [f.model_dump() for f in findings],
    }

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
