"""
Test script to validate improved keyword extraction
"""

from deterministic_matcher import extract_keywords_from_text

def test_keyword_extraction():
    """Test improved keyword extraction with various job descriptions"""
    
    print("="*80)
    print("KEYWORD EXTRACTION TESTS")
    print("="*80 + "\n")
    
    # Test 1: Technical job description
    test1_jd = """
    Senior Full Stack Developer
    
    Requirements:
    - 5+ years of experience with React and Node.js
    - Strong knowledge of TypeScript and JavaScript
    - Experience with AWS (EC2, S3, Lambda)
    - Proficiency in PostgreSQL and MongoDB
    - Experience with Docker and Kubernetes
    - Knowledge of CI/CD pipelines using Jenkins or GitHub Actions
    - Bachelor's degree in Computer Science
    - Excellent communication skills
    - Strong team player
    """
    
    print("Test 1: Technical Job Description")
    print("-" * 80)
    keywords1 = extract_keywords_from_text(test1_jd)
    print(f"Extracted {len(keywords1)} keywords:")
    for kw in sorted(keywords1):
        print(f"  - {kw}")
    print()
    
    # Expected to find: react, node.js, typescript, javascript, aws, ec2, s3, lambda, 
    # postgresql, mongodb, docker, kubernetes, ci/cd, jenkins, github
    # Should NOT find: senior, developer, years, experience, strong, excellent, team, degree
    
    # Test 2: Data Science job description
    test2_jd = """
    Data Scientist Position
    
    We are looking for a talented data scientist with:
    - Experience in machine learning and deep learning
    - Proficiency in Python (NumPy, Pandas, Scikit-learn)
    - Knowledge of TensorFlow or PyTorch
    - Experience with SQL and NoSQL databases
    - Familiarity with cloud platforms (AWS or GCP)
    - Strong statistical background
    - PhD preferred but not required
    """
    
    print("Test 2: Data Science Job Description")
    print("-" * 80)
    keywords2 = extract_keywords_from_text(test2_jd)
    print(f"Extracted {len(keywords2)} keywords:")
    for kw in sorted(keywords2):
        print(f"  - {kw}")
    print()
    
    # Expected: machine learning, deep learning, python, numpy, pandas, scikit-learn,
    # tensorflow, pytorch, sql, aws, gcp
    # Should NOT find: scientist, talented, experience, strong, preferred, required
    
    # Test 3: Generic/buzzword heavy description
    test3_jd = """
    We are seeking a passionate and innovative software engineer to join our dynamic team.
    You will work on cutting-edge projects in a fast-paced environment.
    Must be a self-starter with excellent problem-solving skills.
    Ability to work independently and in teams.
    Strong communication skills are essential.
    Competitive salary and benefits offered.
    """
    
    print("Test 3: Generic/Buzzword Heavy Description (should extract very few)")
    print("-" * 80)
    keywords3 = extract_keywords_from_text(test3_jd)
    print(f"Extracted {len(keywords3)} keywords:")
    for kw in sorted(keywords3):
        print(f"  - {kw}")
    print()
    
    # Expected: Very few or none - this is mostly generic HR speak
    
    # Test 4: DevOps focused description
    test4_jd = """
    DevOps Engineer
    
    Required Skills:
    - Docker and Kubernetes (K8s)
    - Terraform and Ansible for infrastructure as code
    - CI/CD tools: Jenkins, GitLab CI, or GitHub Actions
    - Cloud platforms: AWS (preferred), Azure, or GCP
    - Monitoring: Prometheus, Grafana, Datadog
    - Scripting: Python, Bash, or PowerShell
    - Experience with microservices architecture
    """
    
    print("Test 4: DevOps Job Description")
    print("-" * 80)
    keywords4 = extract_keywords_from_text(test4_jd)
    print(f"Extracted {len(keywords4)} keywords:")
    for kw in sorted(keywords4):
        print(f"  - {kw}")
    print()
    
    # Expected: docker, kubernetes, k8s, terraform, ansible, ci/cd, jenkins, gitlab,
    # github, aws, azure, gcp, prometheus, grafana, datadog, python, bash, powershell,
    # microservices
    
    # Test 5: Multi-word technical terms
    test5_jd = """
    Machine Learning Engineer
    
    - Natural Language Processing (NLP)
    - Computer Vision
    - Deep Learning frameworks
    - RESTful API design
    - Distributed systems experience
    - Object-oriented programming
    """
    
    print("Test 5: Multi-word Technical Terms")
    print("-" * 80)
    keywords5 = extract_keywords_from_text(test5_jd)
    print(f"Extracted {len(keywords5)} keywords:")
    for kw in sorted(keywords5):
        print(f"  - {kw}")
    print()
    
    # Expected: machine learning, natural language processing, nlp, computer vision,
    # deep learning, rest, api, distributed systems, object-oriented
    
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Test 1 (Technical): {len(keywords1)} keywords")
    print(f"Test 2 (Data Science): {len(keywords2)} keywords")
    print(f"Test 3 (Generic/Buzzwords): {len(keywords3)} keywords - Should be LOW")
    print(f"Test 4 (DevOps): {len(keywords4)} keywords")
    print(f"Test 5 (Multi-word): {len(keywords5)} keywords")
    print()
    
    # Quality checks
    print("QUALITY CHECKS:")
    print("-" * 80)
    
    # Check for unwanted generic terms in Test 1
    unwanted_test1 = {'senior', 'developer', 'years', 'experience', 'strong', 
                      'excellent', 'team', 'degree', 'communication', 'skills'}
    found_unwanted = keywords1.intersection(unwanted_test1)
    if found_unwanted:
        print(f"[WARN] Test 1: Found unwanted generic terms: {found_unwanted}")
    else:
        print("[PASS] Test 1: No unwanted generic terms found")
    
    # Check for essential technical terms in Test 1
    expected_test1 = {'react', 'typescript', 'javascript', 'aws', 'postgresql', 
                      'mongodb', 'docker', 'kubernetes'}
    found_expected = keywords1.intersection(expected_test1)
    missing_expected = expected_test1 - keywords1
    if missing_expected:
        print(f"[WARN] Test 1: Missing expected terms: {missing_expected}")
    else:
        print("[PASS] Test 1: All essential technical terms found")
    
    # Check Test 3 has very few keywords (< 5)
    if len(keywords3) < 5:
        print(f"[PASS] Test 3: Correctly filtered generic description ({len(keywords3)} keywords)")
    else:
        print(f"[WARN] Test 3: Too many keywords from generic description ({len(keywords3)} keywords)")
    
    # Check for multi-word terms in Test 5
    multi_word_found = [kw for kw in keywords5 if ' ' in kw]
    if len(multi_word_found) > 0:
        print(f"[PASS] Test 5: Multi-word terms captured: {multi_word_found}")
    else:
        print("[WARN] Test 5: No multi-word terms captured")
    
    print()


if __name__ == "__main__":
    test_keyword_extraction()
