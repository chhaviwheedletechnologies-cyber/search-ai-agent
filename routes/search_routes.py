from fastapi import APIRouter

from models.schemas import BusinessContext
from services.query_fanout import QueryFanout
from services.scan_engine import ScanEngine
from services.citation_engine import CitationEngine
from services.sentiment_engine import SentimentEngine
from services.score_engine import ScoreEngine
from services.optimization_engine import OptimizationEngine

router = APIRouter(prefix="/search-ai", tags=["Search AI"])


@router.post("/scan")
def scan(data: BusinessContext):

    prompts = QueryFanout().generate(data.business, data.location)

    responses = ScanEngine().scan(prompts)

    raw_responses = responses.get("responses", []) if isinstance(responses, dict) else responses

    successful = [
        r for r in raw_responses
        if isinstance(r, dict) and r.get("status") == "success"
    ]

    failed_engines = [
        {
            "engine": r.get("engine", "Unknown"),
            "prompt": r.get("prompt", "")
        }
        for r in raw_responses
        if isinstance(r, dict) and r.get("status") == "failed"
    ]

    citations = CitationEngine().extract(
        successful,
        business_name=data.business
    )

    sentiment = SentimentEngine().analyze(successful)

    score = ScoreEngine().calculate(successful)

    recommendations = OptimizationEngine().recommend()

    google_results = [
        r for r in successful
        if r.get("engine") == "Google Search"
    ]

    brand_found = any(
        (r.get("knowledge_graph") or {}).get("title")
        for r in google_results
    )

    has_official = any(
        data.business.lower() in (
            ((r.get("knowledge_graph") or {}).get("title") or "").lower()
        )
        for r in google_results
    )

    has_linkedin = any(
        any(
            "linkedin.com" in c.get("link", "").lower()
            for c in r.get("competitors", [])
        )
        for r in google_results
    )

    has_reviews = any(
        ((r.get("knowledge_graph") or {}).get("reviews") or 0) >= 5
        for r in google_results
    )

    strengths = []

    if has_official:
        strengths.append("Official business listing detected.")

    if has_linkedin:
        strengths.append("LinkedIn presence detected.")

    if brand_found:
        strengths.append("Google Search visibility detected.")

    gaps = []

    if not has_reviews:
        gaps.append("More public reviews recommended.")

    gaps.append("FAQ schema recommended.")
    gaps.append("Local SEO can be strengthened.")

    return {
        "fanout": prompts,
        "responses": successful,
        "failed_engines": failed_engines,
        "brand_found": brand_found,
        "overall_sentiment": sentiment,
        "visibility_score": score,
        "summary": {
            "strengths": strengths,
            "gaps": gaps
        },
        "recommendations": recommendations,
        "citations": citations
    }


@router.get("/visibility")
def visibility():
    return {
        "message": "Use POST /search-ai/scan to calculate live visibility score."
    }


@router.get("/recommendations")
def recommendations():
    return OptimizationEngine().recommend()