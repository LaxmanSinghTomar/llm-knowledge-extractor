"""FastAPI application for LLM Knowledge Extractor."""
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import json
from typing import Optional

from app.database import init_db, get_db, Analysis
from app.models import (
    AnalyzeRequest,
    AnalysisResponse,
    SearchResponse,
    HealthResponse
)
from app.services.llm_service import analyze_text, configure_dspy
from app.services.nlp_service import extract_keywords
from app.config import settings

# Initialize FastAPI application
app = FastAPI(
    title="LLM Knowledge Extractor",
    description=(
        "Extract structured knowledge from unstructured text using LLMs. "
        "Built with DSPy for reliable structured extraction, FastAPI for "
        "production-ready APIs, and spaCy for traditional NLP."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.on_event("startup")
def startup_event():
    """
    Initialize application on startup.
    
    - Creates database tables if they don't exist
    - Configures DSPy with OpenAI backend
    """
    init_db(settings.database_url)
    configure_dspy(settings.openai_api_key, settings.llm_model)


@app.get("/", response_model=HealthResponse)
def root():
    """
    Health check endpoint.
    
    Returns:
        Service status and version information
    """
    return HealthResponse(
        status="healthy",
        service="LLM Knowledge Extractor",
        version="1.0.0"
    )


@app.post("/analyze", response_model=AnalysisResponse, status_code=201)
def analyze(
    request: AnalyzeRequest,
    db: Session = Depends(lambda: next(get_db(settings.database_url)))
):
    """
    Analyze text and extract structured metadata.
    
    This endpoint:
    1. Extracts keywords using spaCy (manual noun frequency analysis)
    2. Uses DSPy + LLM to extract summary, title, topics, and sentiment
    3. Stores all results in the database
    4. Returns the complete analysis
    
    Edge cases handled:
    - Empty input: Validated by Pydantic (min_length=1) → 422 error
    - LLM API failure: Catches exceptions → 503 error
    - Invalid LLM response: Catches JSON parsing errors → 503 error
    
    Args:
        request: AnalyzeRequest with text field
        db: Database session (injected)
        
    Returns:
        AnalysisResponse with all extracted metadata
        
    Raises:
        HTTPException(400): Invalid input
        HTTPException(503): Service unavailable (LLM API failure)
    """
    try:
        # Step 1: Extract keywords manually (not via LLM)
        keywords = extract_keywords(request.text, top_n=3)
        
        # Step 2: LLM analysis using DSPy (includes confidence score)
        metadata = analyze_text(request.text)
        
        # Step 3: Store in database
        analysis = Analysis(
            raw_text=request.text,
            summary=metadata.summary,
            title=metadata.title,
            topics=json.dumps(metadata.topics),
            sentiment=metadata.sentiment,
            keywords=json.dumps(keywords),
            confidence=str(metadata.confidence)
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Step 4: Return response
        return AnalysisResponse(
            id=analysis.id,
            summary=analysis.summary,
            title=analysis.title,
            topics=json.loads(analysis.topics),
            sentiment=analysis.sentiment,
            keywords=json.loads(analysis.keywords),
            confidence=float(analysis.confidence),
            created_at=analysis.created_at
        )
        
    except ValueError as e:
        # Client errors (empty input, etc.)
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # LLM API errors
        raise HTTPException(
            status_code=503,
            detail=f"Service temporarily unavailable: {str(e)}"
        )
    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=503,
            detail=f"Internal error: {str(e)}"
        )


@app.get("/search", response_model=SearchResponse)
def search(
    topic: Optional[str] = None,
    db: Session = Depends(lambda: next(get_db(settings.database_url)))
):
    """
    Search analyses by topic or keyword.
    
    Performs case-insensitive substring matching on topics and keywords.
    If no topic parameter provided, returns all analyses.
    
    Args:
        topic: Search term to match against topics/keywords (optional)
        db: Database session (injected)
        
    Returns:
        SearchResponse with matching analyses and count
        
    Examples:
        - GET /search → returns all analyses
        - GET /search?topic=healthcare → returns analyses mentioning "healthcare"
        - GET /search?topic=AI → returns analyses with "AI" in topics/keywords
    """
    # Start with base query
    query = db.query(Analysis)
    
    # Apply topic filter if provided
    if topic:
        # Case-insensitive search in both topics and keywords (stored as JSON strings)
        search_term = f"%{topic.lower()}%"
        query = query.filter(
            (Analysis.topics.like(search_term)) | 
            (Analysis.keywords.like(search_term))
        )
    
    # Execute query and order by most recent first
    results = query.order_by(Analysis.created_at.desc()).all()
    
    # Convert database models to response models
    response_list = [
        AnalysisResponse(
            id=r.id,
            summary=r.summary,
            title=r.title,
            topics=json.loads(r.topics),
            sentiment=r.sentiment,
            keywords=json.loads(r.keywords),
            confidence=float(r.confidence),
            created_at=r.created_at
        )
        for r in results
    ]
    
    return SearchResponse(results=response_list, count=len(response_list))

