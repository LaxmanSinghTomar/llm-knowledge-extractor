"""Test LLM extraction quality with diverse examples."""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

# Test cases covering different scenarios
TEST_CASES = [
    {
        "name": "Healthcare AI - Positive",
        "text": """
        Artificial intelligence is revolutionizing healthcare diagnostics. 
        Recent breakthroughs in deep learning enable doctors to detect cancer 
        earlier with unprecedented accuracy. Hospitals are deploying AI-powered 
        systems that analyze medical images faster than human radiologists. 
        This technology promises to save thousands of lives annually.
        """,
        "expected_sentiment": "positive",
        "expected_topics": ["healthcare", "AI", "diagnostics"]
    },
    {
        "name": "Cybersecurity Breach - Negative", 
        "text": """
        A massive data breach compromised millions of customer accounts yesterday.
        The company's security infrastructure failed to detect the intrusion for weeks.
        Hackers stole sensitive financial information and personal data. Customers are
        furious about the negligence, and the company faces potential lawsuits and
        regulatory fines. Stock prices plummeted 30% following the announcement.
        """,
        "expected_sentiment": "negative",
        "expected_topics": ["security", "breach", "data"]
    },
    {
        "name": "Tech Report - Neutral",
        "text": """
        The quarterly earnings report shows stable growth in cloud computing revenue.
        The company maintained its market share at 23 percent during Q3. Employee
        headcount increased by 500 positions across engineering teams. Capital
        expenditure on infrastructure remained consistent with previous quarters.
        Analysts project similar performance for the upcoming period.
        """,
        "expected_sentiment": "neutral",
        "expected_topics": ["earnings", "cloud computing", "business"]
    },
    {
        "name": "Climate Change - Mixed/Negative",
        "text": """
        Global temperatures reached record highs this summer, causing devastating
        wildfires across three continents. Scientists warn that current emission
        trends will lead to catastrophic consequences within decades. Coastal
        cities face increased flooding risks as ice caps continue melting at
        alarming rates. Urgent action is needed to prevent irreversible damage.
        """,
        "expected_sentiment": "negative",
        "expected_topics": ["climate change", "environment", "global warming"]
    },
    {
        "name": "Product Launch - Positive",
        "text": """
        Apple unveiled its latest iPhone model featuring groundbreaking camera
        technology and extended battery life. Pre-orders exceeded expectations
        with over 2 million units sold in the first 24 hours. Customers praised
        the innovative design and improved performance. Industry analysts predict
        this will be the most successful product launch in the company's history.
        """,
        "expected_sentiment": "positive",
        "expected_topics": ["technology", "product launch", "iPhone"]
    },
    {
        "name": "Short News - Edge Case",
        "text": """
        Bitcoin prices surged 15% today following institutional adoption news.
        """,
        "expected_sentiment": "positive",
        "expected_topics": ["cryptocurrency", "bitcoin", "finance"]
    },
    {
        "name": "Research Paper Abstract",
        "text": """
        This paper presents a novel approach to neural architecture search using
        reinforcement learning. We propose a method that automatically discovers
        optimal network configurations for image classification tasks. Our experiments
        on ImageNet demonstrate a 2.3% improvement over previous state-of-the-art
        models while reducing computational cost by 40%. The technique generalizes
        well across multiple computer vision benchmarks.
        """,
        "expected_sentiment": "neutral",
        "expected_topics": ["machine learning", "research", "neural networks"]
    },
    {
        "name": "Customer Service Complaint",
        "text": """
        I ordered a laptop three weeks ago and still haven't received it. Customer
        service is unresponsive and unhelpful. When I finally reached someone, they
        had no information about my shipment. This is terrible service and I'm
        extremely disappointed. I will never shop here again and will warn others
        to avoid this company. Completely unacceptable experience.
        """,
        "expected_sentiment": "negative",
        "expected_topics": ["customer service", "complaint", "shopping"]
    }
]


def print_result(test_case: Dict, response: Any, index: int):
    """Pretty print test results."""
    print(f"\n{'='*80}")
    print(f"Test {index + 1}: {test_case['name']}")
    print(f"{'='*80}")
    
    print(f"\nINPUT TEXT:")
    print(test_case['text'].strip()[:200] + "..." if len(test_case['text'].strip()) > 200 else test_case['text'].strip())
    
    if response.status_code == 201:
        data = response.json()
        print(f"\nEXTRACTED METADATA:")
        print(f"   ID: {data['id']}")
        print(f"   Title: {data.get('title', 'N/A')}")
        print(f"   Summary: {data['summary']}")
        print(f"   Topics: {', '.join(data['topics'])}")
        print(f"   Sentiment: {data['sentiment']}")
        print(f"   Keywords (spaCy): {', '.join(data['keywords'])}")
        print(f"   Confidence: {data['confidence']:.2f}")
        
        print(f"\nEXPECTATIONS vs ACTUAL:")
        print(f"   Expected Sentiment: {test_case['expected_sentiment']}")
        print(f"   Actual Sentiment: {data['sentiment']}")
        sentiment_match = "✓" if data['sentiment'] == test_case['expected_sentiment'] else "✗"
        print(f"   Match: {sentiment_match}")
        
        print(f"\n   Expected Topics (any): {', '.join(test_case['expected_topics'])}")
        print(f"   Actual Topics: {', '.join(data['topics'])}")
        
    else:
        print(f"\nERROR: {response.status_code}")
        print(f"   {response.text}")


def run_quality_tests():
    """Run all quality tests and summarize results."""
    print("\n" + "="*80)
    print("LLM KNOWLEDGE EXTRACTOR - QUALITY TESTING")
    print("="*80)
    print("\nTesting DSPy-powered structured extraction with diverse examples...")
    print(f"Running {len(TEST_CASES)} test cases\n")
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES):
        try:
            response = requests.post(
                f"{BASE_URL}/analyze",
                json={"text": test_case["text"]},
                timeout=30
            )
            print_result(test_case, response, i)
            
            if response.status_code == 201:
                data = response.json()
                sentiment_match = data['sentiment'] == test_case['expected_sentiment']
                results.append({
                    "name": test_case["name"],
                    "success": True,
                    "sentiment_match": sentiment_match
                })
            else:
                results.append({
                    "name": test_case["name"],
                    "success": False,
                    "sentiment_match": False
                })
                
        except Exception as e:
            print(f"\n❌ EXCEPTION: {str(e)}")
            results.append({
                "name": test_case["name"],
                "success": False,
                "sentiment_match": False
            })
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    sentiment_correct = sum(1 for r in results if r["sentiment_match"])
    
    print(f"\n✅ Successful Extractions: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"📊 Correct Sentiment: {sentiment_correct}/{total} ({sentiment_correct/total*100:.1f}%)")
    
    print("\n📋 Detailed Results:")
    for r in results:
        status = "✓" if r["success"] else "✗"
        sentiment = "✓" if r["sentiment_match"] else "✗"
        print(f"   {status} {r['name']:<40} | Sentiment: {sentiment}")
    
    print("\n" + "="*80)
    print("💡 OBSERVATIONS:")
    print("="*80)
    print("""
    - Check if titles are being extracted appropriately
    - Evaluate topic relevance and specificity
    - Assess sentiment accuracy (especially neutral vs positive/negative)
    - Review summary quality (conciseness and accuracy)
    - Verify keywords capture main concepts
    
    This helps validate that DSPy is producing consistent, high-quality structured outputs.
    """)
    
    return results


if __name__ == "__main__":
    try:
        # Check server health first
        health = requests.get(f"{BASE_URL}/", timeout=5)
        if health.status_code != 200:
            print("❌ Server not responding. Start it with: uv run uvicorn app.main:app --reload")
            exit(1)
        
        results = run_quality_tests()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server at http://localhost:8000")
        print("Start the server with: uv run uvicorn app.main:app --reload\n")
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user\n")

