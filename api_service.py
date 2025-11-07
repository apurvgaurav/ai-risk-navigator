from __future__ import annotations

from typing import List, Optional, Dict

from fastapi import FastAPI
from pydantic import BaseModel

from risk_engine import default_engine, EvaluationContext, RiskFinding

app = FastAPI(
    title="AI Risk Navigator API",
    description=(
        "Deterministic, policy-driven LLM risk evaluation service. "
        "Wraps the rule-based risk engine used by the Streamlit dashboard."
    ),
    version="0.1.0",
)

engine = default_engine()


# ---------- Request / Response Schemas ---------- #

class EvaluationRequest(BaseModel):
    prompt: str
    response: str
    latency_ms: Optional[float] = None
    model_name: Optional[str] = None
    user_id: Optional[str] = None
    source: Optional[str] = None
    extra: Optional[Dict] = None


class EvaluationResponse(BaseModel):
    prompt: str
    response: str
    latency_ms: Optional[float] = None
    model_name: Optional[str] = None
    user_id: Optional[str] = None
    source: Optional[str] = None
    findings: List[Dict]


# ---------- Endpoints ---------- #

@app.get("/health", summary="Health check")
def health():
    return {"status": "ok", "engine_rules": len(engine.rules)}


@app.post(
    "/evaluate",
    response_model=EvaluationResponse,
    summary="Evaluate LLM interaction for risks",
)
def evaluate(req: EvaluationRequest):
    ctx = EvaluationContext(
        prompt=req.prompt,
        response=req.response,
        latency_ms=req.latency_ms,
        model_name=req.model_name,
        user_id=req.user_id,
        source=req.source or "api",
        extra=req.extra or {},
    )

    findings: List[RiskFinding] = engine.evaluate(ctx)

    return EvaluationResponse(
        prompt=ctx.prompt,
        response=ctx.response,
        latency_ms=ctx.latency_ms,
        model_name=ctx.model_name,
        user_id=ctx.user_id,
        source=ctx.source,
        findings=[f.model_dump() for f in findings],
    )
