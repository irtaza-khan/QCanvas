"""
Vector Store Module

This module implements the vector database for storing and searching
embeddings. It provides efficient similarity search using FAISS or
ChromaDB.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com

Purpose:
    - Store embeddings of code snippets and documentation
    - Perform fast similarity search (k-NN)
    - Support metadata filtering
    - Manage vector index persistence

Input:
    - Embeddings (vectors)
    - Metadata (algorithm type, tags, complexity)
    - Query embeddings for search
    - Search parameters (top-k, threshold)

Output:
    - Similar vectors with scores
    - Associated metadata
    - Search statistics

Dependencies:
    - FAISS or ChromaDB: For vector storage and search
    - NumPy: For vector operations
    - EmbeddingModel: For generating embeddings

Links to other modules:
    - Used by: Retriever, KnowledgeBase
    - Uses: EmbeddingModel, FAISS/ChromaDB
    - Part of: RAG system pipeline
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Union
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from ..cirq_rag_code_assistant.config import get_config
from ..cirq_rag_code_assistant.config.logging import get_logger

logger = get_logger(__name__)


class VectorStore:
    """
    Vector database for storing and searching embeddings.
    
    Supports both FAISS and ChromaDB backends for efficient similarity search.
    """
    
    def __init__(
        self,
        embedding_dim: int,
        vector_db_type: str = "faiss",
        index_path: Optional[Union[str, Path]] = None,
        use_gpu: bool = False,
    ):
        """
        Initialize the VectorStore.
        
        Args:
            embedding_dim: Dimension of embeddings
            vector_db_type: Type of vector DB ("faiss" or "chroma")
            index_path: Path to save/load index
            use_gpu: Whether to use GPU for FAISS (if available)
        """
        self.embedding_dim = embedding_dim
        self.vector_db_type = vector_db_type.lower()
        self.index_path = Path(index_path) if index_path else None
        self.use_gpu = use_gpu
        
        # Validate vector DB type
        if self.vector_db_type == "faiss" and not FAISS_AVAILABLE:
            raise ImportError(
                "FAISS is required for 'faiss' backend. "
                "Install it with: pip install faiss-cpu (or faiss-gpu)"
            )
        
        if self.vector_db_type == "chroma" and not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is required for 'chroma' backend. "
                "Install it with: pip install chromadb"
            )
        
        # Initialize backend
        config = get_config()
        if self.vector_db_type == "faiss":
            self._init_faiss()
        elif self.vector_db_type == "chroma":
            self._init_chroma()
        else:
            raise ValueError(f"Unsupported vector DB type: {vector_db_type}")
        
        # Metadata storage
        self.metadata: List[Dict[str, Any]] = []
        self.id_to_index: Dict[str, int] = {}
        self.index_to_id: Dict[int, str] = {}
        self.next_id = 0
        
        logger.info(f"Initialized VectorStore with {self.vector_db_type} backend")
        logger.info(f"Embedding dimension: {embedding_dim}")
    
    def _init_faiss(self) -> None:
        """Initialize FAISS index."""
        # Use L2 distance (Euclidean) for similarity search
        # For normalized embeddings, L2 is equivalent to cosine similarity
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Use GPU if requested and available
        if self.use_gpu and faiss.get_num_gpus() > 0:
            try:
                res = faiss.StandardGpuResources()
                self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
                logger.info("Using FAISS GPU acceleration")
            except Exception as e:
                logger.warning(f"Failed to use GPU, falling back to CPU: {e}")
                self.use_gpu = False
        
        logger.info("Initialized FAISS index")
    
    def _init_chroma(self) -> None:
        """Initialize ChromaDB client."""
        # Create or get collection
        chroma_path = self.index_path / "chroma_db" if self.index_path else None
        
        self.chroma_client = chromadb.Client(
            settings=ChromaSettings(
                persist_directory=str(chroma_path) if chroma_path else None,
                anonymized_telemetry=False,
            )
        )
        
        # Create or get collection
        collection_name = "cirq_rag_embeddings"
        try:
            self.collection = self.chroma_client.get_collection(collection_name)
            logger.info(f"Loaded existing ChromaDB collection: {collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"embedding_dim": self.embedding_dim}
            )
            logger.info(f"Created new ChromaDB collection: {collection_name}")
        
        logger.info("Initialized ChromaDB")
    
    def add(
        self,
        embeddings: np.ndarray,
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Add embeddings to the vector store.
        
        Args:
            embeddings: Numpy array of embeddings (shape: [n, embedding_dim])
            ids: Optional list of IDs for each embedding
            metadatas: Optional list of metadata dictionaries
            
        Returns:
            List of IDs for added embeddings
        """
        n = len(embeddings)
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{self.next_id + i}" for i in range(n)]
        
        # Default metadata
        if metadatas is None:
            metadatas = [{}] * n
        
        # Validate inputs
        if len(ids) != n or len(metadatas) != n:
            raise ValueError("Lengths of embeddings, ids, and metadatas must match")
        
        # Add to backend
        if self.vector_db_type == "faiss":
            self._add_faiss(embeddings, ids, metadatas)
        else:
            self._add_chroma(embeddings, ids, metadatas)
        
        logger.debug(f"Added {n} embeddings to vector store")
        return ids
    
    def _add_faiss(
        self,
        embeddings: np.ndarray,
        ids: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """Add embeddings to FAISS index."""
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        start_idx = len(self.metadata)
        for i, (id_, metadata) in enumerate(zip(ids, metadatas)):
            idx = start_idx + i
            self.metadata.append(metadata)
            self.id_to_index[id_] = idx
            self.index_to_id[idx] = id_
            self.next_id = max(self.next_id, idx + 1)
    
    def _add_chroma(
        self,
        embeddings: np.ndarray,
        ids: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """Add embeddings to ChromaDB."""
        # Convert to list format for ChromaDB
        embeddings_list = embeddings.tolist()
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings_list,
            ids=ids,
            metadatas=metadatas,
        )
        
        # Update local tracking
        start_idx = len(self.metadata)
        for i, (id_, metadata) in enumerate(zip(ids, metadatas)):
            idx = start_idx + i
            self.metadata.append(metadata)
            self.id_to_index[id_] = idx
            self.index_to_id[idx] = id_
            self.next_id = max(self.next_id, idx + 1)
    
    def search(
        self,
        query_embeddings: np.ndarray,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[List[Dict[str, Any]]]:
        """
        Search for similar embeddings.
        
        Args:
            query_embeddings: Query embeddings (shape: [n_queries, embedding_dim])
            k: Number of results to return per query
            filter_dict: Optional metadata filter dictionary
            
        Returns:
            List of lists of results, one per query
            Each result is a dict with 'id', 'score', 'metadata'
        """
        if self.vector_db_type == "faiss":
            return self._search_faiss(query_embeddings, k, filter_dict)
        else:
            return self._search_chroma(query_embeddings, k, filter_dict)
    
    def _search_faiss(
        self,
        query_embeddings: np.ndarray,
        k: int,
        filter_dict: Optional[Dict[str, Any]],
    ) -> List[List[Dict[str, Any]]]:
        """Search using FAISS."""
        # Normalize query embeddings
        query_embeddings = query_embeddings.astype('float32')
        faiss.normalize_L2(query_embeddings)
        
        # Search
        k = min(k, self.index.ntotal) if self.index.ntotal > 0 else 0
        if k == 0:
            return [[] for _ in range(len(query_embeddings))]
        
        distances, indices = self.index.search(query_embeddings, k)
        
        # Format results
        results = []
        for query_idx, (dists, idxs) in enumerate(zip(distances, indices)):
            query_results = []
            for dist, idx in zip(dists, idxs):
                if idx == -1:  # FAISS returns -1 for invalid indices
                    continue
                
                # Convert distance to similarity score (for L2 on normalized vectors)
                score = 1.0 / (1.0 + dist)  # Simple conversion
                
                doc_id = self.index_to_id.get(idx, f"doc_{idx}")
                metadata = self.metadata[idx] if idx < len(self.metadata) else {}
                
                # Apply filter if provided
                if filter_dict and not self._matches_filter(metadata, filter_dict):
                    continue
                
                query_results.append({
                    "id": doc_id,
                    "score": float(score),
                    "distance": float(dist),
                    "metadata": metadata,
                    "index": int(idx),
                })
            
            results.append(query_results)
        
        return results
    
    def _search_chroma(
        self,
        query_embeddings: np.ndarray,
        k: int,
        filter_dict: Optional[Dict[str, Any]],
    ) -> List[List[Dict[str, Any]]]:
        """Search using ChromaDB."""
        # Convert to list format
        query_embeddings_list = query_embeddings.tolist()
        
        # Search
        results = []
        for query_emb in query_embeddings_list:
            chroma_results = self.collection.query(
                query_embeddings=[query_emb],
                n_results=k,
                where=filter_dict,  # ChromaDB supports where clauses
            )
            
            # Format results
            query_results = []
            if chroma_results['ids'] and len(chroma_results['ids'][0]) > 0:
                for i, doc_id in enumerate(chroma_results['ids'][0]):
                    query_results.append({
                        "id": doc_id,
                        "score": float(chroma_results['distances'][0][i]),
                        "metadata": chroma_results['metadatas'][0][i] if chroma_results['metadatas'] else {},
                    })
            
            results.append(query_results)
        
        return results
    
    def _matches_filter(self, metadata: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Check if metadata matches filter criteria."""
        for key, value in filter_dict.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False
        return True
    
    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get embedding and metadata by ID.
        
        Args:
            id: Document ID
            
        Returns:
            Dictionary with 'id', 'metadata', or None if not found
        """
        if self.vector_db_type == "faiss":
            if id not in self.id_to_index:
                return None
            
            idx = self.id_to_index[id]
            return {
                "id": id,
                "metadata": self.metadata[idx] if idx < len(self.metadata) else {},
                "index": idx,
            }
        else:
            try:
                result = self.collection.get(ids=[id])
                if result['ids']:
                    return {
                        "id": id,
                        "metadata": result['metadatas'][0] if result['metadatas'] else {},
                    }
            except:
                pass
            return None
    
    def size(self) -> int:
        """Get the number of embeddings in the store."""
        if self.vector_db_type == "faiss":
            return self.index.ntotal
        else:
            return self.collection.count()
    
    def save(self, path: Optional[Union[str, Path]] = None) -> None:
        """
        Save the vector store to disk.
        
        Args:
            path: Path to save the index (uses self.index_path if None)
        """
        save_path = Path(path) if path else self.index_path
        if not save_path:
            raise ValueError("No path provided for saving")
        
        save_path.mkdir(parents=True, exist_ok=True)
        
        if self.vector_db_type == "faiss":
            # Save FAISS index
            index_file = save_path / "faiss.index"
            faiss.write_index(self.index, str(index_file))
            
            # Save metadata
            metadata_file = save_path / "metadata.pkl"
            with open(metadata_file, 'wb') as f:
                pickle.dump({
                    "metadata": self.metadata,
                    "id_to_index": self.id_to_index,
                    "index_to_id": self.index_to_id,
                    "next_id": self.next_id,
                }, f)
            
            logger.info(f"Saved FAISS index to {save_path}")
        else:
            # ChromaDB persists automatically
            self.chroma_client.persist()
            logger.info(f"Persisted ChromaDB to {save_path}")
    
    def load(self, path: Optional[Union[str, Path]] = None) -> None:
        """
        Load the vector store from disk.
        
        Args:
            path: Path to load the index from (uses self.index_path if None)
        """
        load_path = Path(path) if path else self.index_path
        if not load_path or not load_path.exists():
            raise FileNotFoundError(f"Index path not found: {load_path}")
        
        if self.vector_db_type == "faiss":
            # Load FAISS index
            index_file = load_path / "faiss.index"
            if not index_file.exists():
                raise FileNotFoundError(f"FAISS index file not found: {index_file}")
            
            self.index = faiss.read_index(str(index_file))
            
            # Load metadata
            metadata_file = load_path / "metadata.pkl"
            if metadata_file.exists():
                with open(metadata_file, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data["metadata"]
                    self.id_to_index = data["id_to_index"]
                    self.index_to_id = data["index_to_id"]
                    self.next_id = data["next_id"]
            
            logger.info(f"Loaded FAISS index from {load_path}")
        else:
            # ChromaDB loads automatically on initialization
            logger.info(f"ChromaDB loaded from {load_path}")
