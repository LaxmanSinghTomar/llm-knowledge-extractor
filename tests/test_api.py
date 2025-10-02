"""Manual testing script for the LLM Knowledge Extractor API."""
import requests
import json

BASE_URL = "http://localhost:8000"


def print_response(title: str, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_health_check():
    """Test 1: Health check endpoint."""
    response = requests.get(f"{BASE_URL}/")
    print_response("Test 1: Health Check", response)
    assert response.status_code == 200


def test_normal_analysis():
    """Test 2: Normal text analysis."""
    text = """
    Artificial intelligence is transforming healthcare in remarkable ways. 
    Machine learning algorithms can now detect diseases earlier and more 
    accurately than traditional methods. Hospitals around the world are 
    adopting AI-powered diagnostic tools to improve patient outcomes and 
    reduce costs. The future of medicine looks bright with these innovations.
    """
    
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={"text": text}
    )
    print_response("Test 2: Normal Analysis (Healthcare AI)", response)
    assert response.status_code == 201
    data = response.json()
    assert "summary" in data
    assert "topics" in data
    assert len(data["topics"]) == 3
    assert "sentiment" in data
    assert "keywords" in data
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0  # Validate range
    print(f"\n✓ Analysis ID: {data['id']}")
    print(f"✓ Confidence: {data['confidence']}")
    return data["id"]


def test_empty_input():
    """Test 3: Empty input (should fail with 422)."""
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={"text": ""}
    )
    print_response("Test 3: Empty Input (Should Fail)", response)
    assert response.status_code == 422


def test_search_all():
    """Test 4: Search without filters (get all)."""
    response = requests.get(f"{BASE_URL}/search")
    print_response("Test 4: Search All Analyses", response)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data
    print(f"\n✓ Total analyses: {data['count']}")


def test_search_by_topic():
    """Test 5: Search by topic."""
    response = requests.get(f"{BASE_URL}/search?topic=healthcare")
    print_response("Test 5: Search by Topic (healthcare)", response)
    assert response.status_code == 200


def test_negative_sentiment():
    """Test 6: Text with negative sentiment."""
    text = """
    The data breach was a disaster for the company. Thousands of customer 
    records were compromised, leading to massive financial losses and 
    damaged reputation. The security team failed to detect the vulnerability 
    in time, and now the company faces multiple lawsuits.
    """
    
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={"text": text}
    )
    print_response("Test 6: Negative Sentiment Analysis", response)
    assert response.status_code == 201


def test_short_text():
    """Test 7: Very short text."""
    text = "Python is a programming language."
    
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={"text": text}
    )
    print_response("Test 7: Short Text Analysis", response)
    assert response.status_code == 201


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("LLM Knowledge Extractor - Manual Test Suite")
    print("="*60)
    print("\nMake sure the server is running at http://localhost:8000")
    print("Start server with: uv run uvicorn app.main:app --reload\n")
    
    try:
        test_health_check()
        test_normal_analysis()
        test_empty_input()
        test_search_all()
        test_search_by_topic()
        test_negative_sentiment()
        test_short_text()
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}\n")
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server.")
        print("Make sure the server is running at http://localhost:8000\n")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")


if __name__ == "__main__":
    main()

