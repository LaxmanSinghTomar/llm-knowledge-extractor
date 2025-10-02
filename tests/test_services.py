"""Unit tests for service layer."""
import pytest
from app.services.nlp_service import extract_keywords


class TestNLPService:
    """Tests for the NLP keyword extraction service."""
    
    def test_keyword_extraction_basic(self):
        """Test basic keyword extraction with clear nouns."""
        text = "The cat sat on the mat. The dog ran to the cat."
        keywords = extract_keywords(text, top_n=3)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 3
        assert "cat" in keywords  # Should be most frequent
        
    def test_keyword_extraction_empty(self):
        """Test keyword extraction with empty input."""
        assert extract_keywords("") == []
        assert extract_keywords("   ") == []
        assert extract_keywords(None or "") == []
    
    def test_keyword_extraction_no_nouns(self):
        """Test keyword extraction with text containing no nouns."""
        text = "wow very much so very"
        keywords = extract_keywords(text, top_n=3)
        assert keywords == []
    
    def test_keyword_extraction_fewer_than_requested(self):
        """Test when text has fewer nouns than top_n."""
        text = "The computer is fast."
        keywords = extract_keywords(text, top_n=5)
        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        
    def test_keyword_extraction_case_insensitive(self):
        """Test that keyword extraction is case-insensitive."""
        text = "Python is great. Python is powerful. Python is popular."
        keywords = extract_keywords(text, top_n=1)
        assert "python" in keywords
    
    def test_keyword_extraction_proper_nouns(self):
        """Test extraction of proper nouns."""
        text = "Apple released the iPhone. Microsoft launched Windows. Google created Android."
        keywords = extract_keywords(text, top_n=5)
        # Should include proper nouns like company names and product names
        assert len(keywords) > 0

