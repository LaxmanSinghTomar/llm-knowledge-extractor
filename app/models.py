"""Pydantic models for API request and response validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class AnalyzeRequest(BaseModel):
    """
    Request model for text analysis endpoint.
    
    Validates that text is provided and not empty.
    """
    text: str = Field(
        ...,
        min_length=1,
        description="Text to analyze (cannot be empty)",
        examples=["Artificial intelligence is transforming healthcare..."]
    )


class AnalysisResponse(BaseModel):
    """
    Response model for analysis results.
    
    Returns all extracted metadata plus the analysis ID and timestamp.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(description="Unique analysis ID")
    summary: str = Field(description="1-2 sentence summary")
    title: Optional[str] = Field(description="Extracted title, if available")
    topics: List[str] = Field(description="3 key topics")
    sentiment: str = Field(description="Sentiment: positive, neutral, or negative")
    keywords: List[str] = Field(description="Top 3 most frequent nouns")
    confidence: float = Field(description="Confidence score (0.0-1.0) based on text characteristics")
    created_at: datetime = Field(description="Timestamp of analysis")


class SearchResponse(BaseModel):
    """
    Response model for search results.
    
    Returns matching analyses and total count.
    """
    results: List[AnalysisResponse] = Field(description="List of matching analyses")
    count: int = Field(description="Total number of results")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(description="Service health status")
    service: str = Field(description="Service name")
    version: str = Field(description="API version")

