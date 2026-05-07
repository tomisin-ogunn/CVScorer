"""
AI Matcher Module for CV Scoring
Uses Google's Gemini API to perform semantic similarity analysis
between CVs and job descriptions.
"""

import os
import re
import logging
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)


class CVMatcher:
    """
    Handles CV to Job Description matching using Gemini AI.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        """
        Initialize the CV Matcher with a specific Gemini model.
        
        Args:
            model_name: Name of the Gemini model to use (default: gemini-1.5-flash for speed)
            api_key: Optional API key to use instead of environment variable
        """
        # Use provided API key or fall back to environment variable
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("API key not provided and GEMINI_API_KEY not found in environment variables")
        
        # Configure with the provided or default API key
        genai.configure(api_key=self.api_key)
        
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"Initialized CVMatcher with model: {model_name}")

    def normalize_text(self, text: str) -> str:
        """
        Normalize text by removing extra whitespace and standardizing format.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text

    def compute_similarity(
        self, cv_text: str, job_description: str
    ) -> Dict[str, any]:
        """
        Compute similarity between CV and job description using Gemini AI.
        
        Args:
            cv_text: The candidate's CV text
            job_description: The job description text
            
        Returns:
            Dictionary containing:
                - similarity_score: int (0-100)
                - matched_keywords: List[str]
                - missing_keywords: List[str]
                - analysis: str (brief explanation)
        """
        try:
            # Normalize inputs
            cv_text = self.normalize_text(cv_text)
            job_description = self.normalize_text(job_description)

            # Construct the prompt for Gemini
            prompt = self._build_prompt(cv_text, job_description)

            # Generate response
            logger.info("Sending request to Gemini API...")
            response = self.model.generate_content(prompt)
            
            # Parse the response
            result = self._parse_response(response.text)
            
            logger.info(f"Successfully computed similarity score: {result['similarity_score']}")
            return result

        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            raise Exception(f"AI matching failed: {str(e)}")

    def _build_prompt(self, cv_text: str, job_description: str) -> str:
        """
        Build the prompt for Gemini API.
        
        Args:
            cv_text: The candidate's CV text
            job_description: The job description text
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert HR assistant and technical recruiter. Analyze the following CV against the job description and provide a detailed matching assessment.

**Job Description:**
{job_description}

**Candidate CV:**
{cv_text}

**Your Task:**
1. Calculate a similarity score (0-100) indicating how well the candidate matches the job requirements
2. Identify matched keywords/skills that the candidate possesses (focus on CONCRETE technical skills)
3. Identify missing keywords/skills that the candidate lacks (focus on CRITICAL requirements)
4. Provide a brief analysis

**IMPORTANT - Keyword Guidelines:**
ONLY include keywords that are:
- Specific technologies (Python, React, AWS, PostgreSQL, Docker)
- Programming languages (JavaScript, Java, C++, TypeScript)
- Frameworks and libraries (Django, Flask, Spring Boot, Angular)
- Tools and platforms (Git, Jenkins, Kubernetes, Terraform)
- Methodologies (Agile, Scrum, TDD, CI/CD)
- Databases (MySQL, MongoDB, Redis, Elasticsearch)
- Certifications and qualifications

DO NOT include:
- Generic job titles (Developer, Engineer, Manager)
- Soft skills (teamwork, communication, leadership)
- Vague buzzwords (innovative, dynamic, passionate)
- Generic terms (experience, knowledge, skills, requirements)
- Time references (3+ years, 5 years)
- Education levels (Bachelor's, Master's) unless specifically mentioned as a requirement

**Response Format (JSON):**
{{
    "similarity_score": <integer between 0-100>,
    "matched_keywords": ["keyword1", "keyword2", ...],
    "missing_keywords": ["keyword1", "keyword2", ...],
    "analysis": "<brief 2-3 sentence explanation of the match>"
}}

**Scoring Criteria:**
- 90-100: Exceptional match - candidate exceeds most requirements with extensive relevant experience
- 75-89: Strong match - candidate meets most key technical requirements
- 60-74: Good match - candidate meets many requirements but has some technical gaps
- 40-59: Moderate match - candidate has some relevant experience but significant gaps in key technologies
- 20-39: Weak match - candidate has minimal relevant technical experience
- 0-19: Poor match - candidate does not meet basic technical requirements

**Evaluation Priority (in order):**
1. Core technical skills and technologies explicitly mentioned in the job description
2. Years of relevant experience with those technologies
3. Related technical skills that demonstrate adaptability
4. Domain expertise and industry knowledge
5. Educational background and certifications
6. Soft skills and methodologies (lowest priority)

Provide ONLY the JSON response, no additional text."""

        return prompt

    def _parse_response(self, response_text: str) -> Dict[str, any]:
        """
        Parse the Gemini API response and extract structured data.
        
        Args:
            response_text: Raw response text from Gemini
            
        Returns:
            Structured dictionary with similarity results
        """
        import json
        
        try:
            # Try to find JSON in the response
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Validate and ensure all required fields exist
            similarity_score = result.get("similarity_score", 50)
            matched_keywords = result.get("matched_keywords", [])
            missing_keywords = result.get("missing_keywords", [])
            analysis = result.get("analysis", "Analysis not available")
            
            # Ensure score is within bounds
            similarity_score = max(0, min(100, int(similarity_score)))
            
            return {
                "similarity_score": similarity_score,
                "matched_keywords": matched_keywords,
                "missing_keywords": missing_keywords,
                "analysis": analysis
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            
            # Fallback: try to extract score manually
            score_match = re.search(r'"similarity_score":\s*(\d+)', response_text)
            if score_match:
                score = int(score_match.group(1))
            else:
                score = 50  # Default fallback
            
            return {
                "similarity_score": score,
                "matched_keywords": [],
                "missing_keywords": [],
                "analysis": "Unable to parse detailed analysis. Please try again."
            }


# Singleton instance
_matcher_instance: Optional[CVMatcher] = None


def get_matcher() -> CVMatcher:
    """
    Get or create the singleton CVMatcher instance.
    
    Returns:
        CVMatcher instance
    """
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = CVMatcher()
    return _matcher_instance


def compute_similarity(cv_text: str, job_description: str, api_key: Optional[str] = None) -> Dict[str, any]:
    """
    Convenience function to compute similarity.
    
    Args:
        cv_text: The candidate's CV text
        job_description: The job description text
        api_key: Optional API key to use instead of environment variable
        
    Returns:
        Dictionary containing similarity results
    """
    # Create a new matcher instance with the provided API key if given
    if api_key:
        matcher = CVMatcher(api_key=api_key)
    else:
        matcher = get_matcher()
    return matcher.compute_similarity(cv_text, job_description)
