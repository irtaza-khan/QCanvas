"""
Knowledge Base Module

This module manages the curated knowledge base of Cirq code snippets,
documentation, and educational content. It handles data loading,
indexing, and retrieval.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com

Purpose:
    - Manage knowledge base data (code snippets, docs, examples)
    - Load and parse knowledge base files
    - Index content for retrieval
    - Provide structured access to knowledge base entries

Input:
    - Knowledge base file paths
    - Query parameters (algorithm, complexity, tags)
    - Update/refresh requests

Output:
    - Knowledge base entries (code + metadata)
    - Statistics about knowledge base
    - Search results

Dependencies:
    - VectorStore: For embedding storage
    - EmbeddingModel: For generating embeddings
    - File system: For reading knowledge base files
    - JSON/YAML: For parsing metadata

Links to other modules:
    - Used by: Retriever, VectorStore initialization
    - Uses: VectorStore, EmbeddingModel
    - Part of: RAG system pipeline
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any, Iterator
from collections import defaultdict

from ..data.dataset_loader import DatasetLoader
from .embeddings import EmbeddingModel
from .vector_store import VectorStore
from ..cirq_rag_code_assistant.config import get_config
from ..cirq_rag_code_assistant.config.logging import get_logger

logger = get_logger(__name__)


class KnowledgeBase:
    """
    Manages the curated knowledge base of Cirq code snippets and documentation.
    
    Handles loading, indexing, and retrieval of knowledge base entries with
    support for semantic search via vector embeddings.
    """
    
    def __init__(
        self,
        knowledge_base_path: Optional[Path] = None,
        embedding_model: Optional[EmbeddingModel] = None,
        vector_store: Optional[VectorStore] = None,
        vector_db_type: str = "faiss",
    ):
        """
        Initialize the KnowledgeBase.
        
        Args:
            knowledge_base_path: Path to knowledge base directory or JSONL file
            embedding_model: EmbeddingModel instance (creates new if None)
            vector_store: VectorStore instance (creates new if None)
            vector_db_type: Type of vector DB backend
        """
        config = get_config()
        self.knowledge_base_path = Path(knowledge_base_path) if knowledge_base_path else Path(config.get("rag.knowledge_base.path", "data/knowledge_base"))
        
        # Initialize embedding model
        self.embedding_model = embedding_model or EmbeddingModel()
        embedding_dim = self.embedding_model.get_embedding_dimension()
        
        # Initialize vector store
        if vector_store is None:
            config = get_config()
            index_path = config.get("rag.vector_store.index_path", "data/models/vector_index")
            self.vector_store = VectorStore(
                embedding_dim=embedding_dim,
                vector_db_type=vector_db_type,
                index_path=index_path,
            )
        else:
            self.vector_store = vector_store
        
        # Storage for entries
        self.entries: List[Dict[str, Any]] = []
        self.entry_by_id: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Initialized KnowledgeBase with {len(self.entries)} entries")
    
    def load_from_jsonl(self, jsonl_path: Path) -> int:
        """
        Load knowledge base entries from a JSONL file.
        
        Args:
            jsonl_path: Path to JSONL file
            
        Returns:
            Number of entries loaded
        """
        jsonl_path = Path(jsonl_path)
        if not jsonl_path.exists():
            raise FileNotFoundError(f"Knowledge base file not found: {jsonl_path}")
        
        logger.info(f"Loading knowledge base from {jsonl_path}")
        
        loader = DatasetLoader(jsonl_path)
        entries = loader.load()
        
        self.entries.extend(entries)
        
        # Index entries by ID
        for i, entry in enumerate(entries):
            entry_id = entry.get("id", f"entry_{len(self.entry_by_id)}")
            entry["_kb_index"] = len(self.entries) - len(entries) + i
            self.entry_by_id[entry_id] = entry
        
        logger.info(f"Loaded {len(entries)} entries from {jsonl_path}")
        return len(entries)
    
    def load_from_directory(self, directory: Optional[Path] = None) -> int:
        """
        Load knowledge base from a directory containing JSONL files.
        
        Args:
            directory: Directory path (uses self.knowledge_base_path if None)
            
        Returns:
            Total number of entries loaded
        """
        directory = Path(directory) if directory else self.knowledge_base_path
        
        if not directory.exists():
            logger.warning(f"Knowledge base directory not found: {directory}")
            return 0
        
        total_loaded = 0
        
        # Find all JSONL files
        jsonl_files = list(directory.glob("*.jsonl"))
        
        for jsonl_file in jsonl_files:
            try:
                count = self.load_from_jsonl(jsonl_file)
                total_loaded += count
            except Exception as e:
                logger.error(f"Error loading {jsonl_file}: {e}")
        
        logger.info(f"Loaded {total_loaded} total entries from directory")
        return total_loaded
    
    def index_entries(
        self,
        entries: Optional[List[Dict[str, Any]]] = None,
        batch_size: int = 32,
    ) -> None:
        """
        Index knowledge base entries in the vector store.
        
        Args:
            entries: Entries to index (uses self.entries if None)
            batch_size: Batch size for embedding generation
        """
        entries_to_index = entries if entries is not None else self.entries
        
        if not entries_to_index:
            logger.warning("No entries to index")
            return
        
        logger.info(f"Indexing {len(entries_to_index)} entries in vector store")
        
        # Prepare texts for embedding
        texts = []
        ids = []
        metadatas = []
        
        for entry in entries_to_index:
            # Create text representation
            text_parts = []
            
            # Add task (natural language description) - primary search target
            if "task" in entry:
                text_parts.append(entry["task"])
            
            # Add topics as searchable text
            if "topics" in entry and entry["topics"]:
                topics_text = "Topics: " + ", ".join(entry["topics"])
                text_parts.append(topics_text)
            
            # Add constraints if available
            if "constraints" in entry and entry["constraints"]:
                constraints_text = "Constraints: " + "; ".join(entry["constraints"])
                text_parts.append(constraints_text)
            
            # Add description if available (fallback for other data formats)
            if "description" in entry:
                text_parts.append(entry["description"])
            
            # Add code
            if "code" in entry:
                text_parts.append(entry["code"])
            
            # Combine into single text
            text = "\n\n".join(text_parts)
            texts.append(text)
            
            # Generate ID
            entry_id = entry.get("id", f"entry_{len(ids)}")
            ids.append(entry_id)
            
            # Extract metadata
            metadata = {
                "framework": entry.get("framework", "Unknown"),
                "file": entry.get("file", ""),
            }
            
            # Add algorithm info if available
            if "metadata" in entry and "algorithms" in entry["metadata"]:
                metadata["algorithms"] = entry["metadata"]["algorithms"]
            
            metadatas.append(metadata)
        
        # Generate embeddings in batches
        embeddings = self.embedding_model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
        )
        
        # Add to vector store
        self.vector_store.add(
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas,
        )
        
        logger.info(f"✅ Indexed {len(entries_to_index)} entries")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base using semantic similarity.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of matching entries with scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode_queries([query])
        
        # Search vector store
        results = self.vector_store.search(
            query_embeddings=query_embedding,
            k=top_k,
            filter_dict=filter_dict,
        )
        
        # Format results with full entry data
        formatted_results = []
        for result_list in results:
            for result in result_list:
                entry_id = result["id"]
                entry = self.entry_by_id.get(entry_id)
                
                if entry:
                    formatted_result = {
                        "entry": entry,
                        "score": result["score"],
                        "metadata": result.get("metadata", {}),
                    }
                    formatted_results.append(formatted_result)
        
        return formatted_results
    
    def get_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a knowledge base entry by ID.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Entry dictionary or None if not found
        """
        return self.entry_by_id.get(entry_id)
    
    def get_by_algorithm(self, algorithm: str) -> List[Dict[str, Any]]:
        """
        Get all entries for a specific algorithm.
        
        Args:
            algorithm: Algorithm name (e.g., "vqe", "qaoa")
            
        Returns:
            List of entries matching the algorithm
        """
        matching_entries = []
        
        for entry in self.entries:
            metadata = entry.get("metadata", {})
            algorithms = metadata.get("algorithms", [])
            
            if algorithm.lower() in [a.lower() for a in algorithms]:
                matching_entries.append(entry)
        
        return matching_entries
    
    def get_by_framework(self, framework: str) -> List[Dict[str, Any]]:
        """
        Get all entries for a specific framework.
        
        Args:
            framework: Framework name (e.g., "Cirq")
            
        Returns:
            List of entries for the framework
        """
        return [entry for entry in self.entries if entry.get("framework") == framework]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        stats = {
            "total_entries": len(self.entries),
            "indexed_entries": self.vector_store.size(),
            "frameworks": defaultdict(int),
            "algorithms": defaultdict(int),
        }
        
        for entry in self.entries:
            # Count frameworks
            framework = entry.get("framework", "Unknown")
            stats["frameworks"][framework] += 1
            
            # Count algorithms
            metadata = entry.get("metadata", {})
            algorithms = metadata.get("algorithms", [])
            for algo in algorithms:
                stats["algorithms"][algo] += 1
        
        # Convert defaultdicts to regular dicts
        stats["frameworks"] = dict(stats["frameworks"])
        stats["algorithms"] = dict(stats["algorithms"])
        
        return stats
    
    def save_index(self, path: Optional[Path] = None) -> None:
        """
        Save the vector store index to disk.
        
        Args:
            path: Path to save index (uses config if None)
        """
        config = get_config()
        save_path = path or Path(config.get("rag.vector_store.index_path", "data/models/vector_index"))
        self.vector_store.save(save_path)
        logger.info(f"Saved knowledge base index to {save_path}")
    
    def load_index(self, path: Optional[Path] = None) -> None:
        """
        Load the vector store index from disk.
        
        Args:
            path: Path to load index from (uses config if None)
        """
        config = get_config()
        load_path = path or Path(config.get("rag.vector_store.index_path", "data/models/vector_index"))
        try:
            self.vector_store.load(load_path)
            logger.info(f"Loaded knowledge base index from {load_path}")
        except FileNotFoundError:
            logger.warning(f"Index not found at {load_path}, will need to rebuild")
    
    def rebuild_index(self) -> None:
        """Rebuild the vector store index from current entries."""
        logger.info("Rebuilding knowledge base index...")
        config = get_config()
        self.vector_store = VectorStore(
            embedding_dim=self.embedding_model.get_embedding_dimension(),
            vector_db_type=self.vector_store.vector_db_type,
            index_path=config.get("rag.vector_store.index_path", "data/models/vector_index"),
        )
        self.index_entries()
        self.save_index()
