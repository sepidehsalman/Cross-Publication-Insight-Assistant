import os
from typing import List, Dict, Any
from dataclasses import dataclass, field
from collections import Counter

from dotenv import load_dotenv
from google import genai
from langgraph.graph import StateGraph, END
from langchain.tools import tool

load_dotenv()

# ---------------------------------------------------------------------
# Gemini Setup
# ---------------------------------------------------------------------

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# ---------------------------------------------------------------------
# Shared State
# ---------------------------------------------------------------------


@dataclass
class GraphState:
    repos: List[Dict[str, Any]]
    query: str
    project_signals: List[Dict[str, Any]] = field(default_factory=list)
    aggregated_trends: Dict[str, Any] = field(default_factory=dict)
    comparison: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    verified: bool = False


# ---------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------


@tool
def repo_reader(repo: Dict[str, Any]) -> str:
    """
    Read a GitHub repository's README and metadata as plain text.
    """
    return f"""
    Repository: {repo["name"]}
    README:
    {repo.get("readme", "")}
    Tags: {", ".join(repo.get("tags", []))}
    """


@tool
def keyword_extractor(text: str) -> List[str]:
    """
    Extract relevant framework and methodology keywords from text.
    """
    keywords = [
        "langgraph",
        "crewai",
        "langchain",
        "vector database",
        "rag",
        "evaluation",
    ]
    text = text.lower()
    return [k for k in keywords if k in text]


# ---------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------


def project_analyzer(state: GraphState) -> GraphState:
    results = []
    for repo in state.repos:
        content = repo_reader.invoke({"repo": repo})
        keywords = keyword_extractor.invoke({"text": content})
        results.append(
            {"name": repo["name"], "keywords": keywords, "tags": repo.get("tags", [])}
        )
    state.project_signals = results
    return state


def trend_aggregator(state: GraphState) -> GraphState:
    counter = Counter()
    for proj in state.project_signals:
        counter.update(proj["keywords"])

    total = max(len(state.project_signals), 1)

    state.aggregated_trends = {
        k: {"count": v, "percentage": round((v / total) * 100, 2)}
        for k, v in counter.items()
    }
    return state


def comparator(state: GraphState) -> GraphState:
    crewai = [p for p in state.project_signals if "crewai" in p["keywords"]]
    langchain = [p for p in state.project_signals if "langchain" in p["keywords"]]

    state.comparison = {
        "CrewAI_projects": len(crewai),
        "LangChain_projects": len(langchain),
        "difference": len(crewai) - len(langchain),
    }
    return state


def summarizer(state: GraphState) -> GraphState:
    prompt = f"""
You are a research summarization agent.

User query:
{state.query or "General analysis of repositories"}

Aggregated trends:
{state.aggregated_trends}

Comparison results:
{state.comparison}

Write a concise, factual summary grounded only in the data above.
"""

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)

    state.summary = response.text.strip()
    return state


def fact_checker(state: GraphState) -> GraphState:
    summary = state.summary.lower()
    state.verified = any(
        k in summary for k in ["crewai", "langchain", "percentage", "projects"]
    )
    return state


# ---------------------------------------------------------------------
# LangGraph Orchestration
# ---------------------------------------------------------------------

graph = StateGraph(GraphState)

graph.add_node("analyzer", project_analyzer)
graph.add_node("aggregator", trend_aggregator)
graph.add_node("comparator", comparator)
graph.add_node("summarizer", summarizer)
graph.add_node("fact_checker", fact_checker)

graph.set_entry_point("analyzer")
graph.add_edge("analyzer", "aggregator")
graph.add_edge("aggregator", "comparator")
graph.add_edge("comparator", "summarizer")
graph.add_edge("summarizer", "fact_checker")
graph.add_edge("fact_checker", END)

app = graph.compile()
