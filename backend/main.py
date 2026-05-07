from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
from deterministic_matcher import (
    compute_similarity as compute_deterministic_similarity,
    compute_similarity_with_sections,
    get_phase4_stats,
    clear_cache
)
from ai_matcher import compute_similarity as compute_ai_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title="CV Scorer Backend")

# Allow requests from the frontend dev server
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScoreRequest(BaseModel):
    cv_text: str
    job_description: str
    api_key: Optional[str] = None
    use_deterministic: Optional[bool] = True  # Phase 1: Use deterministic by default
    use_sections: Optional[bool] = False  # Phase 3: Enable section-based analysis


class ScoreResponse(BaseModel):
    score: int
    similarity_score: int
    matched_keywords: List[str]
    missing_keywords: List[str]
    analysis: Optional[str] = None
    sections: Optional[Dict[str, Optional[float]]] = None  # Phase 3: Section scores
    aggregated_similarity: Optional[float] = None  # Phase 3: Weighted section average


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/stats")
def get_stats() -> dict:
    """
    Get Phase 4 optimization statistics.
    
    Returns:
        Dictionary with cache and usage statistics
    """
    try:
        stats = get_phase4_stats()
        return {
            "status": "ok",
            "phase4_optimizations": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.post("/cache/clear")
def clear_embedding_cache() -> dict:
    """
    Clear the embedding cache.
    
    Returns:
        Information about the cleared cache
    """
    try:
        result = clear_cache()
        logger.info(f"Cache cleared: {result['files_deleted']} files deleted")
        return {
            "status": "ok",
            **result
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@app.post("/score", response_model=ScoreResponse)
def score(request: ScoreRequest) -> ScoreResponse:
    """
    Compute similarity score between CV and job description using AI.
    
    Args:
        request: ScoreRequest containing cv_text and job_description
        
    Returns:
        ScoreResponse with similarity score and keyword analysis
    """
    try:
        logger.info("Received scoring request")
        
        # Validate inputs
        if not request.cv_text or not request.cv_text.strip():
            raise HTTPException(status_code=400, detail="CV text cannot be empty")
        
        if not request.job_description or not request.job_description.strip():
            raise HTTPException(status_code=400, detail="Job description cannot be empty")
        
        # Ensure inputs have meaningful content (at least 10 words)
        cv_words = len(request.cv_text.strip().split())
        job_words = len(request.job_description.strip().split())
        
        if cv_words < 10:
            raise HTTPException(status_code=400, detail="CV text is too short. Please provide a more detailed CV (at least 10 words).")
        
        if job_words < 10:
            raise HTTPException(status_code=400, detail="Job description is too short. Please provide a more detailed job description (at least 10 words).")
        
        # Choose which similarity method to use
        if request.use_deterministic:
            # Check if section-based analysis is requested (Phase 3)
            if request.use_sections:
                logger.info("Using Phase 3 section-based similarity analysis")
                result = compute_similarity_with_sections(
                    request.cv_text,
                    request.job_description
                )
                
                # Phase 3 returns section breakdown
                overall_score = int(round(result["overall_similarity"]))
                aggregated_score = result["aggregated_similarity"]
                
                # Format section scores for response
                section_scores = result["sections"]
                
                # Count valid sections
                valid_sections = sum(1 for v in section_scores.values() if v is not None)
                
                return ScoreResponse(
                    score=overall_score,
                    similarity_score=overall_score,
                    matched_keywords=result.get("matched_keywords", []),
                    missing_keywords=result.get("missing_keywords", []),
                    sections=section_scores,
                    aggregated_similarity=aggregated_score,
                    analysis=f"Phase 3: Section-based analysis with {valid_sections} sections analyzed. "
                            f"Overall similarity: {overall_score}%, Aggregated from sections: {aggregated_score}%. "
                            f"Found {len(result.get('matched_keywords', []))} matching keywords."
                )
            else:
                # Phase 1+2: Standard deterministic similarity
                logger.info("Using Phase 1+2 deterministic similarity (embeddings + cosine + keyword matching)")
                result = compute_deterministic_similarity(
                    request.cv_text, 
                    request.job_description
                )
                # Phase 1+2 returns similarity score and keyword analysis
                similarity_score = int(round(result["similarity_score"]))
                return ScoreResponse(
                    score=similarity_score,
                    similarity_score=similarity_score,
                    matched_keywords=result.get("matched_keywords", []),
                    missing_keywords=result.get("missing_keywords", []),
                    analysis=f"Phase 1+2: Deterministic similarity using embeddings and keyword matching. Found {len(result.get('matched_keywords', []))} matching keywords and {len(result.get('missing_keywords', []))} missing keywords."
                )
        else:
            logger.info("Using AI-based similarity (LLM analysis)")
            result = compute_ai_similarity(
                request.cv_text, 
                request.job_description,
                api_key=request.api_key
            )
            # Return response
            return ScoreResponse(
                score=result["similarity_score"],
                similarity_score=result["similarity_score"],
                matched_keywords=result["matched_keywords"],
                missing_keywords=result["missing_keywords"],
                analysis=result.get("analysis")
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing score request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

