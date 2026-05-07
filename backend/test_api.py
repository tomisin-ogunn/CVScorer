"""
Test script for CV Scorer API
"""

import requests
import json


def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        print("[PASS] Health check passed!\n")
        return True
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}\n")
        return False


def test_score_endpoint():
    """Test the score endpoint with sample CV and job description"""
    print("Testing /score endpoint...")
    
    # Sample CV text
    cv_text = """
    John Doe
    Senior Software Engineer
    
    Experience:
    - 5 years of experience in full-stack web development
    - Proficient in React, Node.js, TypeScript, and Python
    - Experience with AWS cloud services (EC2, S3, Lambda)
    - Built and maintained RESTful APIs using FastAPI and Express
    - Strong knowledge of SQL and NoSQL databases (PostgreSQL, MongoDB)
    - Implemented CI/CD pipelines using GitHub Actions
    
    Education:
    - Bachelor of Science in Computer Science
    
    Skills:
    - JavaScript, TypeScript, Python, React, Node.js
    - AWS, Docker, Kubernetes
    - PostgreSQL, MongoDB, Redis
    - Git, Agile methodologies
    """
    
    # Sample job description
    job_description = """
    Position: Full Stack Developer
    
    Requirements:
    - 3+ years of experience with React and Node.js
    - Strong understanding of TypeScript
    - Experience with cloud platforms (AWS preferred)
    - Knowledge of RESTful API design
    - Experience with databases (SQL and NoSQL)
    - Familiarity with Docker and containerization
    - Understanding of CI/CD practices
    - Bachelor's degree in Computer Science or related field
    
    Nice to have:
    - Python experience
    - Kubernetes knowledge
    - Experience with FastAPI
    """
    
    try:
        payload = {
            "cv_text": cv_text,
            "job_description": job_description
        }
        
        print("Sending request to API...")
        response = requests.post("http://localhost:8000/score", json=payload)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*60)
            print("RESULTS:")
            print("="*60)
            print(f"Similarity Score: {result['similarity_score']}/100")
            print(f"\nMatched Keywords ({len(result['matched_keywords'])}):")
            for keyword in result['matched_keywords']:
                print(f"  + {keyword}")
            print(f"\nMissing Keywords ({len(result['missing_keywords'])}):")
            for keyword in result['missing_keywords']:
                print(f"  - {keyword}")
            if result.get('analysis'):
                print(f"\nAnalysis:\n{result['analysis']}")
            print("="*60)
            print("[PASS] Score endpoint test passed!\n")
            return True
        else:
            print(f"[FAIL] Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Score endpoint test failed: {e}\n")
        return False


def test_empty_inputs():
    """Test the score endpoint with empty inputs"""
    print("Testing /score endpoint with empty inputs...")
    
    try:
        payload = {
            "cv_text": "",
            "job_description": "Some job description"
        }
        
        response = requests.post("http://localhost:8000/score", json=payload)
        
        if response.status_code == 400:
            print(f"[PASS] Correctly rejected empty CV with status code: {response.status_code}")
            return True
        else:
            print(f"[FAIL] Expected status code 400, got: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Empty input test failed: {e}\n")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CV SCORER API TESTS")
    print("="*60 + "\n")
    
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_health_endpoint():
        tests_passed += 1
    
    if test_score_endpoint():
        tests_passed += 1
    
    if test_empty_inputs():
        tests_passed += 1
    
    # Summary
    print("\n" + "="*60)
    print(f"TEST SUMMARY: {tests_passed}/{total_tests} tests passed")
    print("="*60 + "\n")
