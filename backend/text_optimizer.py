"""
Phase 4: Text Optimization Utilities
Provides functions to truncate and optimize text for embedding to reduce token usage.
"""

import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def count_tokens(text: str) -> int:
    """
    Estimate the number of tokens in text.
    
    This is a rough estimate based on character count.
    Actual token count may vary by model.
    
    Rule of thumb:
    - English text: ~4 characters per token
    - Code: ~3-4 characters per token
    
    Args:
        text: Text to count tokens for
        
    Returns:
        Estimated token count
    """
    # Simple heuristic: divide character count by 4
    return max(1, len(text) // 4)


def truncate_text(text: str, max_tokens: int = 2000, preserve_structure: bool = True) -> str:
    """
    Truncate text to fit within a token budget.
    
    Args:
        text: Text to truncate
        max_tokens: Maximum number of tokens to keep
        preserve_structure: If True, try to keep complete sentences/sections
        
    Returns:
        Truncated text
    """
    estimated_tokens = count_tokens(text)
    
    # If already within limit, return as-is
    if estimated_tokens <= max_tokens:
        return text
    
    logger.info(f"Truncating text from ~{estimated_tokens} to ~{max_tokens} tokens")
    
    # Calculate target character count (tokens * 4)
    target_chars = max_tokens * 4
    
    if preserve_structure:
        # Try to truncate at sentence boundaries
        # Split into sentences (simple approach)
        sentences = re.split(r'([.!?]\s+)', text)
        
        # Rebuild text up to character limit
        truncated = ""
        for i, sentence in enumerate(sentences):
            if len(truncated) + len(sentence) <= target_chars:
                truncated += sentence
            else:
                break
        
        # If we got at least half the target, use it
        if len(truncated) >= target_chars * 0.5:
            return truncated.strip()
    
    # Fallback: simple character truncation
    return text[:target_chars].strip()


def extract_relevant_chunks(
    text: str,
    chunk_size: int = 500,
    keywords: List[str] = None
) -> List[str]:
    """
    Extract relevant chunks from text, optionally focusing on keyword-rich sections.
    
    This is useful for long documents where we only need to embed
    the most relevant parts.
    
    Args:
        text: Text to extract chunks from
        chunk_size: Size of each chunk in tokens
        keywords: Optional list of keywords to prioritize
        
    Returns:
        List of text chunks
    """
    # Split text into paragraphs/sections
    sections = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = ""
    target_chunk_chars = chunk_size * 4  # tokens to chars
    
    # Score each section by keyword relevance
    if keywords:
        scored_sections = []
        for section in sections:
            section_lower = section.lower()
            # Count how many keywords appear in this section
            score = sum(1 for kw in keywords if kw.lower() in section_lower)
            scored_sections.append((score, section))
        
        # Sort by score (highest first)
        scored_sections.sort(reverse=True, key=lambda x: x[0])
        sections = [section for score, section in scored_sections]
    
    # Build chunks from sections
    for section in sections:
        if not section.strip():
            continue
        
        # If section is too large, split it
        if len(section) > target_chunk_chars:
            # Split into sentences
            sentences = re.split(r'([.!?]\s+)', section)
            temp_chunk = ""
            
            for sentence in sentences:
                if len(temp_chunk) + len(sentence) <= target_chunk_chars:
                    temp_chunk += sentence
                else:
                    if temp_chunk:
                        chunks.append(temp_chunk.strip())
                    temp_chunk = sentence
            
            if temp_chunk:
                chunks.append(temp_chunk.strip())
        else:
            # Add section to current chunk
            if len(current_chunk) + len(section) <= target_chunk_chars:
                current_chunk += "\n\n" + section if current_chunk else section
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = section
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    logger.info(f"Extracted {len(chunks)} chunks from text")
    return chunks


def optimize_text_for_embedding(
    text: str,
    max_tokens: int = 2000,
    remove_boilerplate: bool = True
) -> str:
    """
    Optimize text for embedding by removing unnecessary content.
    
    Args:
        text: Text to optimize
        max_tokens: Maximum tokens to keep
        remove_boilerplate: If True, remove common boilerplate text
        
    Returns:
        Optimized text
    """
    optimized = text
    
    if remove_boilerplate:
        # Remove common boilerplate phrases that don't add semantic value
        boilerplate_patterns = [
            r'(?i)please send (your )?(cv|resume) to.*',
            r'(?i)we are an equal opportunity employer.*',
            r'(?i)equal employment opportunity.*',
            r'(?i)disclaimer:.*',
            r'(?i)confidential.*not to be shared.*',
            r'(?i)copyright \d{4}.*',
            r'(?i)all rights reserved.*',
        ]
        
        for pattern in boilerplate_patterns:
            optimized = re.sub(pattern, '', optimized)
    
    # Remove excessive whitespace
    optimized = re.sub(r'\n\s*\n\s*\n', '\n\n', optimized)
    optimized = re.sub(r' +', ' ', optimized)
    optimized = optimized.strip()
    
    # Truncate if needed
    if count_tokens(optimized) > max_tokens:
        optimized = truncate_text(optimized, max_tokens)
    
    tokens_saved = count_tokens(text) - count_tokens(optimized)
    if tokens_saved > 0:
        logger.info(f"Optimized text: saved ~{tokens_saved} tokens")
    
    return optimized


def split_text_for_batch(texts: List[str], batch_size: int = 100) -> List[List[str]]:
    """
    Split a list of texts into batches for batch processing.
    
    Args:
        texts: List of texts to batch
        batch_size: Maximum number of texts per batch
        
    Returns:
        List of batches (each batch is a list of texts)
    """
    batches = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batches.append(batch)
    
    logger.info(f"Split {len(texts)} texts into {len(batches)} batches")
    return batches


def smart_truncate_for_sections(
    text: str,
    section_max_tokens: int = 1000
) -> Tuple[str, str, str]:
    """
    Smart truncation that preserves key sections for section-based analysis.
    
    Ensures that skills, experience, and education sections are preserved
    as much as possible within the token budget.
    
    Args:
        text: Text to truncate
        section_max_tokens: Maximum tokens per section
        
    Returns:
        Tuple of (skills_section, experience_section, education_section)
        Each truncated to fit within the token budget.
    """
    from deterministic_matcher import detect_sections
    
    # Detect sections
    sections = detect_sections(text)
    
    # Truncate each section independently
    truncated_sections = {}
    for section_name, section_text in sections.items():
        if section_text and count_tokens(section_text) > section_max_tokens:
            truncated_sections[section_name] = truncate_text(
                section_text,
                section_max_tokens,
                preserve_structure=True
            )
        else:
            truncated_sections[section_name] = section_text
    
    return (
        truncated_sections.get('skills', ''),
        truncated_sections.get('experience', ''),
        truncated_sections.get('education', '')
    )


def calculate_token_savings(original_text: str, optimized_text: str) -> dict:
    """
    Calculate token savings from optimization.
    
    Args:
        original_text: Original text
        optimized_text: Optimized text
        
    Returns:
        Dictionary with savings statistics
    """
    original_tokens = count_tokens(original_text)
    optimized_tokens = count_tokens(optimized_text)
    tokens_saved = original_tokens - optimized_tokens
    savings_percent = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0
    
    return {
        'original_tokens': original_tokens,
        'optimized_tokens': optimized_tokens,
        'tokens_saved': tokens_saved,
        'savings_percent': round(savings_percent, 2)
    }


if __name__ == "__main__":
    # Test text optimization
    test_text = """
    Senior Software Engineer Position
    
    We are looking for an experienced software engineer to join our team.
    
    Requirements:
    - 5+ years of experience with Python
    - Strong knowledge of React and Node.js
    - Experience with databases like PostgreSQL
    - Docker and Kubernetes experience is a plus
    
    We are an equal opportunity employer and welcome applications from all backgrounds.
    Please send your resume to jobs@example.com
    
    Copyright 2024. All rights reserved. This job posting is confidential and not to be shared.
    """
    
    print("Original text:")
    print(f"Length: {len(test_text)} chars")
    print(f"Estimated tokens: {count_tokens(test_text)}")
    print()
    
    optimized = optimize_text_for_embedding(test_text, max_tokens=100)
    print("Optimized text:")
    print(optimized)
    print()
    print(f"Length: {len(optimized)} chars")
    print(f"Estimated tokens: {count_tokens(optimized)}")
    print()
    
    savings = calculate_token_savings(test_text, optimized)
    print(f"Token savings: {savings['tokens_saved']} ({savings['savings_percent']}%)")
