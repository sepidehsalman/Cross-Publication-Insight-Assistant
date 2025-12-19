from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from app.main import app as langgraph_app, GraphState  # ✅ FIXED

api = FastAPI(title="Cross-Publication Insight Assistant")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------


class AnalyzeRequest(BaseModel):
    repos: List[str]
    query: str | None = ""


class AnalyzeResponse(BaseModel):
    aggregate: Dict[str, Any]
    comparison: Dict[str, Any]
    summary: str
    verified: bool


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def fetch_repo_stub(repo_url: str) -> Dict[str, Any]:
    """
    Minimal stub.
    Replace with GitHub API later.
    """
    name = repo_url.rstrip("/").split("/")[-1]
    return {"name": name, "readme": f"Repository fetched from {repo_url}", "tags": []}


# ---------------------------------------------------------------------
# API Endpoint
# ---------------------------------------------------------------------


@api.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest):
    if not payload.repos:
        raise HTTPException(status_code=400, detail="No repositories provided")

    repos = [fetch_repo_stub(url) for url in payload.repos]

    result = langgraph_app.invoke(GraphState(repos=repos, query=payload.query or ""))

    outputs = {
        "aggregate": result.get("aggregated_trends", {}),
        "comparison": result.get("comparison", {}),
        "summary": result.get("summary", ""),
        "verified": result.get("verified", False),
    }
    non_empty = [v for v in outputs.values() if v]
    if len(non_empty) < 2:
        raise HTTPException(
            status_code=500, detail="Failed to generate sufficient insights"
        )

    return outputs
