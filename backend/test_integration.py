"""
Integration test to verify keyword improvements work end-to-end
"""

from deterministic_matcher import extract_keywords_from_text, match_keywords

def test_real_world_scenario():
    """Test with a realistic job description and CV"""
    
    print("="*80)
    print("REAL-WORLD INTEGRATION TEST")
    print("="*80 + "\n")
    
    # Realistic job description
    job_description = """
    Senior Full Stack Engineer
    
    Our innovative company is looking for a passionate and dynamic full-stack developer
    to join our world-class engineering team!
    
    Requirements:
    - 5+ years of experience in software development
    - Strong proficiency in React and TypeScript
    - Experience with Node.js and Express
    - Knowledge of PostgreSQL and Redis
    - Familiarity with AWS (EC2, S3, Lambda)
    - Understanding of Docker and Kubernetes
    - Experience with CI/CD pipelines
    - Bachelor's degree in Computer Science or related field
    - Excellent communication and teamwork skills
    - Self-starter with strong problem-solving abilities
    
    Nice to have:
    - Experience with GraphQL
    - Knowledge of microservices architecture
    - Familiarity with Python
    """
    
    # Candidate CV
    cv_text = """
    John Smith
    Senior Software Engineer
    
    EXPERIENCE:
    Software Engineer at Tech Corp (2019-Present)
    - Built scalable web applications using React and TypeScript
    - Developed RESTful APIs with Node.js and Express
    - Implemented microservices architecture using Docker and Kubernetes
    - Managed PostgreSQL databases and Redis caching
    - Set up CI/CD pipelines using GitHub Actions
    - Deployed applications on AWS (EC2, S3, Lambda)
    
    Software Developer at StartupXYZ (2017-2019)
    - Developed features using JavaScript and Python
    - Worked with MongoDB and MySQL databases
    - Collaborated with cross-functional teams
    
    EDUCATION:
    Bachelor of Science in Computer Science
    University of Technology, 2017
    
    SKILLS:
    React, TypeScript, JavaScript, Node.js, Express, PostgreSQL, Redis,
    MongoDB, AWS, Docker, Kubernetes, Python, Git, CI/CD
    """
    
    print("Step 1: Extract keywords from job description")
    print("-" * 80)
    job_keywords = extract_keywords_from_text(job_description)
    print(f"Extracted {len(job_keywords)} keywords from job description:")
    for kw in sorted(job_keywords):
        print(f"  - {kw}")
    print()
    
    print("Step 2: Match keywords against CV")
    print("-" * 80)
    matched, missing = match_keywords(cv_text, job_keywords)
    print(f"\nMatched Keywords ({len(matched)}):")
    for kw in matched:
        print(f"  + {kw}")
    print(f"\nMissing Keywords ({len(missing)}):")
    for kw in missing:
        print(f"  - {kw}")
    
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)
    
    match_ratio = len(matched) / len(job_keywords) if job_keywords else 0
    print(f"Match Ratio: {match_ratio:.1%} ({len(matched)}/{len(job_keywords)})")
    
    # Verify no bad keywords
    bad_keywords = {'senior', 'engineer', 'years', 'experience', 'strong', 
                   'excellent', 'communication', 'teamwork', 'self-starter',
                   'problem-solving', 'bachelor', 'degree', 'innovative',
                   'dynamic', 'passionate', 'world-class', 'familiarity',
                   'understanding', 'knowledge'}
    
    found_bad = job_keywords.intersection(bad_keywords)
    if found_bad:
        print(f"\n[WARN] Found unwanted generic keywords: {found_bad}")
    else:
        print(f"\n[PASS] No generic keywords found in extraction")
    
    # Verify essential keywords are present
    essential = {'react', 'typescript', 'node.js', 'express', 'postgresql', 
                'redis', 'aws', 'docker', 'kubernetes', 'ci/cd'}
    found_essential = job_keywords.intersection(essential)
    missing_essential = essential - job_keywords
    
    if missing_essential:
        print(f"[WARN] Missing essential keywords: {missing_essential}")
    else:
        print(f"[PASS] All essential technical keywords captured")
    
    print()


if __name__ == "__main__":
    test_real_world_scenario()
