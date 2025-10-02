"""NLP service for keyword extraction using spaCy."""
import spacy
from collections import Counter
from typing import List

# Load spaCy model once at module level for efficiency
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback error message if model not installed
    raise RuntimeError(
        "spaCy model 'en_core_web_sm' not found. "
        "Install it with: python -m spacy download en_core_web_sm"
    )


def extract_keywords(text: str, top_n: int = 3) -> List[str]:
    """
    Extract top N most frequent nouns from text.
    
    This function uses spaCy's linguistic features to identify and count nouns,
    then returns the most frequent ones. This is implemented manually (not via LLM)
    as per assignment requirements.
    
    Args:
        text: Input text to analyze
        top_n: Number of top keywords to return (default: 3)
    
    Returns:
        List of top N keywords (nouns), or fewer if text contains fewer unique nouns
        
    Edge cases handled:
        - Empty text → returns empty list
        - Text with no nouns → returns empty list
        - Fewer nouns than top_n → returns all available nouns
    
    Examples:
        >>> extract_keywords("The cat sat on the mat. The cat ran.", top_n=2)
        ['cat', 'mat']
    """
    # Handle empty or whitespace-only input
    if not text or not text.strip():
        return []
    
    # Process text with spaCy
    doc = nlp(text.lower())
    
    # Extract nouns (NOUN and PROPN parts of speech)
    # Filter out stop words, punctuation, and very short words
    nouns = [
        token.lemma_ for token in doc 
        if token.pos_ in ("NOUN", "PROPN")  # Common and proper nouns
        and not token.is_stop  # Remove common words like 'the', 'a'
        and not token.is_punct  # Remove punctuation
        and len(token.text) > 2  # Filter very short words
        and token.is_alpha  # Only alphabetic tokens
    ]
    
    # Handle case where no nouns found
    if not nouns:
        return []
    
    # Count noun frequencies
    noun_counts = Counter(nouns)
    
    # Return top N most common nouns
    return [noun for noun, count in noun_counts.most_common(top_n)]

