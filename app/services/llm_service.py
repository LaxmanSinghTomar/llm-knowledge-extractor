"""LLM service for structured knowledge extraction using DSPy."""
import dspy
import json
from typing import Optional, List
from pydantic import BaseModel, Field


class ExtractedMetadata(BaseModel):
    """
    Structured metadata extracted from text.
    
    This Pydantic model ensures type safety and validation for LLM outputs.
    """
    summary: str = Field(description="1-2 sentence summary of the text")
    title: Optional[str] = Field(description="Title if identifiable, else None")
    topics: List[str] = Field(description="3 key topics from the text")
    sentiment: str = Field(description="One of: positive, neutral, negative")
    confidence: float = Field(description="Confidence score (0.0-1.0) for the analysis quality")


class KnowledgeExtractor(dspy.Signature):
    """
    DSPy Signature for extracting structured knowledge from unstructured text.
    
    Using DSPy over LangChain provides:
    - Type-safe prompt contracts via Signatures
    - Better error handling for structured outputs
    - Clear separation of prompt logic from application code
    """
    
    text: str = dspy.InputField(desc="The input text to analyze")
    metadata: str = dspy.OutputField(
        desc=(
            "JSON object containing: "
            "1) summary: a concise 1-2 sentence summary, "
            "2) title: the title if identifiable (otherwise null), "
            "3) topics: array of exactly 3 key topics, "
            "4) sentiment: one of 'positive', 'neutral', or 'negative', "
            "5) confidence: a score from 0.0 to 1.0 indicating confidence in the analysis"
        )
    )


class TextAnalyzer(dspy.Module):
    """
    DSPy Module for text analysis with chain-of-thought reasoning.
    
    ChainOfThought improves extraction quality by having the LLM
    reason about the text before generating structured output.
    """
    
    def __init__(self):
        super().__init__()
        self.extract = dspy.ChainOfThought(KnowledgeExtractor)
    
    def forward(self, text: str) -> ExtractedMetadata:
        """
        Analyze text and return structured metadata.
        
        Args:
            text: Input text to analyze
            
        Returns:
            ExtractedMetadata: Parsed and validated metadata
            
        Raises:
            ValueError: If text is empty
            json.JSONDecodeError: If LLM returns invalid JSON
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Execute DSPy chain-of-thought extraction
        result = self.extract(text=text)
        
        # Parse JSON response from LLM
        try:
            metadata_dict = json.loads(result.metadata)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        
        # Validate and return using Pydantic
        return ExtractedMetadata(**metadata_dict)


# Global analyzer instance (initialized after DSPy configuration)
_analyzer: Optional[TextAnalyzer] = None


def configure_dspy(api_key: str, model: str = "gpt-4.1-mini") -> None:
    """
    Initialize DSPy with OpenAI backend.
    
    This should be called once at application startup.
    
    Args:
        api_key: OpenAI API key
        model: Model name (default: gpt-4.1-mini)
    """
    global _analyzer
    
    # Modern DSPy API uses dspy.LM() instead of dspy.OpenAI()
    lm = dspy.LM(
        f"openai/{model}",
        api_key=api_key,
        max_tokens=2000,
        temperature=0.7
    )
    dspy.configure(lm=lm)
    
    # Initialize analyzer after configuration
    _analyzer = TextAnalyzer()


def analyze_text(text: str) -> ExtractedMetadata:
    """
    Main entry point for LLM-powered text analysis.
    
    Args:
        text: Input text to analyze
        
    Returns:
        ExtractedMetadata: Structured metadata extracted from text
        
    Raises:
        ValueError: If text is empty or DSPy not configured
        RuntimeError: If LLM API fails
        
    Edge cases handled:
        - Empty input: raises ValueError with clear message
        - LLM API failure: raises RuntimeError with error details
        - Invalid JSON from LLM: raises ValueError
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    if _analyzer is None:
        raise ValueError(
            "DSPy not configured. Call configure_dspy() before analyzing text."
        )
    
    try:
        # Call module as callable (DSPy best practice) instead of .forward()
        return _analyzer(text)
    except Exception as e:
        # Wrap any LLM errors in RuntimeError for API layer to handle
        if "API" in str(e) or "rate" in str(e).lower():
            raise RuntimeError(f"LLM API error: {e}")
        raise

