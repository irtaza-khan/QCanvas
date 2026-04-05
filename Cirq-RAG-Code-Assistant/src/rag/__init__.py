"""
RAG (Retrieval-Augmented Generation) System Module

This module implements the RAG system for the Cirq-RAG-Code-Assistant.
It provides components for knowledge retrieval, embedding generation, and
context-aware code generation.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com
"""

# This file exports the main RAG system components
from .retriever import (
    Retriever,
    extract_query_keywords,
    compute_topic_boost,
    DEFAULT_TOPIC_BOOST,
)
from .generator import Generator
from .embeddings import EmbeddingModel
from .vector_store import VectorStore
from .knowledge_base import KnowledgeBase

__all__ = [
    "Retriever",
    "Generator",
    "EmbeddingModel",
    "VectorStore",
    "KnowledgeBase",
    "extract_query_keywords",
    "compute_topic_boost",
    "DEFAULT_TOPIC_BOOST",
]
