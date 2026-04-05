"""
RAG Retriever Module

This module implements the retrieval component of the RAG system.
It handles semantic search, context retrieval, and relevance ranking
for Cirq code examples and documentation.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com

Purpose:
    - Retrieve relevant Cirq code examples from knowledge base
    - Perform semantic similarity search using embeddings
    - Rank and filter results based on relevance scores
    - Provide context for code generation
    - Apply hybrid scoring with topic boosting

Input:
    - Natural language queries (user requests)
    - Algorithm type (optional)
    - Similarity threshold
    - Top-k results count

Output:
    - Ranked list of relevant code snippets
    - Metadata (algorithm type, complexity, tags)
    - Similarity scores (semantic + topic boost)
    - Contextual information

Dependencies:
    - VectorStore: For similarity search
    - EmbeddingModel: For query embeddings
    - KnowledgeBase: For accessing code examples
    - PyTorch: For GPU-accelerated embeddings

Links to other modules:
    - Used by: DesignerAgent, OptimizerAgent, ValidatorAgent, EducationalAgent
    - Uses: VectorStore, EmbeddingModel, KnowledgeBase
    - Part of: RAG system pipeline
"""

import re
from typing import List, Dict, Optional, Any, Set
from .knowledge_base import KnowledgeBase
from ..cirq_rag_code_assistant.config import get_config
from ..cirq_rag_code_assistant.config.logging import get_logger

logger = get_logger(__name__)


# Default configuration for hybrid scoring
DEFAULT_TOPIC_BOOST = 0.15  # Boost per matching topic keyword
DEFAULT_FETCH_MULTIPLIER = 3  # Fetch more candidates for re-ranking


def extract_query_keywords(query: str) -> Set[str]:
    """
    Extract keywords from a query string.
    
    Args:
        query: The search query string
        
    Returns:
        Set of lowercase keywords (len > 2)
    """
    # Split on non-alphanumeric characters (except underscore)
    words = re.split(r'[^a-zA-Z0-9_]+', query.lower())
    # Filter out short words
    return {w for w in words if len(w) > 2}


def compute_topic_boost(query_keywords: Set[str], topics: List[str], boost_per_match: float = DEFAULT_TOPIC_BOOST) -> float:
    """
    Compute topic boost score based on keyword-to-word matching.
    
    Counts how many query keywords match words in each topic.
    A topic with more matching keywords gets a higher boost.
    
    Examples:
    - Query: "bell state circuit", Topics: ["bell_state"]
      "bell" matches, "state" matches → 2 matches → +0.30
    - Query: "bell state circuit", Topics: ["bell_measurement"]  
      "bell" matches, "state" does not → 1 match → +0.15
    
    Args:
        query_keywords: Set of keywords extracted from query
        topics: List of topics from an entry
        boost_per_match: Score boost per matching keyword
        
    Returns:
        Total topic boost score
    """
    if not topics or not query_keywords:
        return 0.0
    
    # For each topic, extract matchable word forms
    # "bell_state" -> {"bell_state", "bellstate", "bell", "state"}
    topic_word_sets = {}
    for topic in topics:
        topic_lower = topic.lower()
        words = set()
        words.add(topic_lower)  # "bell_state"
        words.add(topic_lower.replace('_', '').replace('-', ''))  # "bellstate"
        # Split into individual words
        parts = topic_lower.replace('_', ' ').replace('-', ' ').split()
        words.update(parts)  # ["bell", "state"]
        topic_word_sets[topic] = words
    
    # Count total keyword matches across all topics
    # Each keyword can match at most once per topic
    total_matches = 0
    
    for keyword in query_keywords:
        keyword_clean = keyword.replace('_', '').replace('-', '')
        
        # Check if this keyword matches ANY topic
        for topic, topic_words in topic_word_sets.items():
            matched = False
            for topic_word in topic_words:
                if keyword == topic_word:
                    matched = True
                    break
                if keyword_clean == topic_word.replace('_', '').replace('-', ''):
                    matched = True
                    break
            
            if matched:
                total_matches += 1
                break  # Each keyword only counts once (best match)
    
    return total_matches * boost_per_match


class Retriever:
    """
    Retrieves relevant context from the knowledge base using semantic search.
    
    Handles query processing, similarity search, and result ranking to provide
    high-quality context for code generation.
    
    Supports hybrid scoring that combines:
    - Semantic similarity (from embeddings)
    - Topic keyword boost (for explicit topic matching)
    """
    
    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        topic_boost: float = DEFAULT_TOPIC_BOOST,
        use_hybrid_scoring: bool = True,
    ):
        """
        Initialize the Retriever.
        
        Args:
            knowledge_base: KnowledgeBase instance
            top_k: Default number of results to retrieve
            similarity_threshold: Minimum similarity score threshold
            topic_boost: Score boost per matching topic keyword
            use_hybrid_scoring: Whether to apply topic boosting (default True)
        """
        self.knowledge_base = knowledge_base
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.topic_boost = topic_boost
        self.use_hybrid_scoring = use_hybrid_scoring
        
        logger.info(
            f"Initialized Retriever with top_k={top_k}, threshold={similarity_threshold}, "
            f"topic_boost={topic_boost}, hybrid_scoring={use_hybrid_scoring}"
        )
    
    def _apply_hybrid_scoring(
        self,
        results: List[Dict[str, Any]],
        query: str,
    ) -> List[Dict[str, Any]]:
        """
        Apply hybrid scoring to results by adding topic boost.
        
        Args:
            results: List of search results with scores and entries
            query: Original query string
            
        Returns:
            Results with updated hybrid scores, sorted descending
        """
        if not self.use_hybrid_scoring:
            return results
        
        query_keywords = extract_query_keywords(query)
        
        scored_results = []
        for result in results:
            semantic_score = result.get("score", 0)
            entry = result.get("entry", {})
            topics = entry.get("topics", [])
            
            # Compute topic boost
            topic_boost_score = compute_topic_boost(
                query_keywords, topics, self.topic_boost
            )
            
            # Create updated result with hybrid score
            hybrid_result = {
                **result,
                "semantic_score": semantic_score,
                "topic_boost": topic_boost_score,
                "score": semantic_score + topic_boost_score,  # Hybrid score
            }
            scored_results.append(hybrid_result)
        
        # Sort by hybrid score (descending)
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_results
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        algorithm: Optional[str] = None,
        framework: Optional[str] = None,
        similarity_threshold: Optional[float] = None,
        use_hybrid: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query with hybrid scoring.
        
        Args:
            query: Natural language query
            top_k: Number of results to return (uses self.top_k if None)
            algorithm: Optional algorithm filter
            framework: Optional framework filter (not applied by default)
            similarity_threshold: Minimum similarity score (uses self.similarity_threshold if None)
            use_hybrid: Override hybrid scoring setting
            
        Returns:
            List of retrieved entries with scores and metadata
        """
        top_k = top_k or self.top_k
        threshold = similarity_threshold or self.similarity_threshold
        use_hybrid = use_hybrid if use_hybrid is not None else self.use_hybrid_scoring
        
        # Build filter dictionary - only add filters that are explicitly provided
        filter_dict = {}
        if framework:
            filter_dict["framework"] = framework
        if algorithm:
            filter_dict["algorithms"] = algorithm
        
        # Fetch more candidates when using hybrid scoring for better re-ranking
        fetch_k = top_k * DEFAULT_FETCH_MULTIPLIER if use_hybrid else top_k * 2
        
        # Search knowledge base (use None if no filters)
        results = self.knowledge_base.search(
            query=query,
            top_k=fetch_k,
            filter_dict=filter_dict if filter_dict else None,
        )
        
        # Apply hybrid scoring if enabled
        if use_hybrid:
            results = self._apply_hybrid_scoring(results, query)
        
        # Filter by similarity threshold (using hybrid score if enabled)
        filtered_results = [
            result for result in results
            if result["score"] >= threshold
        ]
        
        # Limit to top_k
        filtered_results = filtered_results[:top_k]
        
        logger.debug(
            f"Retrieved {len(filtered_results)} results for query: {query[:50]}... "
            f"(hybrid={use_hybrid})"
        )
        
        return filtered_results
    
    def retrieve_code_examples(
        self,
        query: str,
        top_k: Optional[int] = None,
        algorithm: Optional[str] = None,
    ) -> List[str]:
        """
        Retrieve code examples as strings.
        
        Args:
            query: Natural language query
            top_k: Number of examples to return
            algorithm: Optional algorithm filter
            
        Returns:
            List of code strings
        """
        results = self.retrieve(query, top_k=top_k, algorithm=algorithm)
        
        code_examples = []
        for result in results:
            entry = result["entry"]
            code = entry.get("code", "")
            if code:
                code_examples.append(code)
        
        return code_examples
    
    def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        algorithm: Optional[str] = None,
        include_descriptions: bool = True,
    ) -> str:
        """
        Retrieve and format context as a single string.
        
        Args:
            query: Natural language query
            top_k: Number of examples to include
            algorithm: Optional algorithm filter
            include_descriptions: Whether to include descriptions
            
        Returns:
            Formatted context string
        """
        results = self.retrieve(query, top_k=top_k, algorithm=algorithm)
        
        context_parts = []
        for i, result in enumerate(results, 1):
            entry = result["entry"]
            
            part = f"Example {i}:\n"
            
            if include_descriptions and "description" in entry:
                part += f"Description: {entry['description']}\n"
            
            # Include task if available
            if include_descriptions and "task" in entry:
                part += f"Task: {entry['task']}\n"
            
            if "code" in entry:
                part += f"Code:\n{entry['code']}\n"
            
            context_parts.append(part)
        
        return "\n\n".join(context_parts)
    
    def retrieve_with_metadata(
        self,
        query: str,
        top_k: Optional[int] = None,
        algorithm: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve results with full metadata including hybrid scoring details.
        
        Args:
            query: Natural language query
            top_k: Number of results to return
            algorithm: Optional algorithm filter
            
        Returns:
            List of dictionaries with entry, score, semantic_score, 
            topic_boost, and metadata
        """
        return self.retrieve(query, top_k=top_k, algorithm=algorithm)
