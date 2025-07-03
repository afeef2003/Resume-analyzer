Simple test runner for the Resume Analysis API
"""
import requests
import json
import time
from test_examples.sample_resumes import SAMPLE_RESUME_1, SAMPLE_RESUME_2

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_analyze_resume():
    """Test resume analysis with streaming"""
    print("Testing resume analysis...")
    
    response = requests.post(
        f"{BASE_URL}/analyze-resume",
        json={"resume_text": SAMPLE_RESUME_1},
        stream=True
    )
    
    print(f"Status Code: {response.status_code}")
    
    checkpoint_id = None
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = json.loads(line_str[6:])
                print(f"Received: {data['type']} - {data['content'][:100]}...")
                if data['type'] == 'complete':
                    checkpoint_id = data.get('checkpoint_id')
                    break
    
    print(f"Checkpoint ID: {checkpoint_id}")
    print("-" * 50)
    return checkpoint_id

def test_resume_questions(checkpoint_id):
    """Test checkpoint resumption"""
    if not checkpoint_id:
        print("No checkpoint ID available, skipping test")
        return
    
    print("Testing checkpoint resumption...")
    
    response = requests.post(
        f"{BASE_URL}/resume-questions",
        json={
            "checkpoint_id": checkpoint_id,
            "insights": [
                "5+ years of software engineering experience",
                "Led team of 6 engineers", 
                "Experience with microservices architecture"
            ]
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Generated {len(data['questions'])} questions:")
        for i, question in enumerate(data['questions'][:3], 1):
            print(f"{i}. {question}")
    else:
        print(f"Error: {response.text}")
    
    print("-" * 50)

def main():
    """Run all tests"""
    print("Starting Resume Analysis API Tests")
    print("=" * 50)
    
    try:
        # Test health
        test_health()
        
        # Test resume analysis
        checkpoint_id = test_analyze_resume()
        
        # Wait a bit for processing
        time.sleep(2)
        
        # Test checkpoint resumption
        test_resume_questions(checkpoint_id)
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    main()
