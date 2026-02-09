"""
Vector Store Service for AULA+

This service manages the storage and retrieval of event embeddings using ChromaDB.
Each classroom has its own collection to ensure data isolation.

Uses ChromaDB for:
- Persistent storage of embeddings
- Semantic search (finding similar events)
- Metadata filtering (by classroom, event type, etc.)
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
import os

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None
    Settings = None


class VectorStore:
    """
    Service for managing event embeddings in ChromaDB.
    
    Each classroom has its own collection to ensure data isolation.
    Collections are created on-demand (lazy creation).
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize VectorStore with ChromaDB client.
        
        Args:
            persist_directory: Directory to persist ChromaDB data.
                             If None, uses in-memory mode (for testing).
                             If provided, data is persisted to disk.
        """
        if chromadb is None:
            raise ImportError(
                "chromadb no está instalado. "
                "Instálalo con: pip install chromadb"
            )
        
        # Set persist directory (default: ./chroma_db in project root)
        if persist_directory is None:
            # Use persistent storage by default
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            persist_directory = os.path.join(project_root, "chroma_db")
        
        # Create ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False  # Disable telemetry
            )
        )
    
    def _get_collection_name(self, classroom_id: UUID) -> str:
        """
        Generate collection name for a classroom.
        
        Args:
            classroom_id: UUID of the classroom
            
        Returns:
            str: Collection name (format: "classroom_{uuid}")
        """
        return f"classroom_{str(classroom_id)}"
    
    def get_or_create_collection(self, classroom_id: UUID) -> Any:
        """
        Get or create a collection for a classroom.
        
        Collections are created lazily - only when first needed.
        Each classroom has its own isolated collection.
        
        Args:
            classroom_id: UUID of the classroom
            
        Returns:
            chromadb.Collection: Collection for the classroom
        """
        collection_name = self._get_collection_name(classroom_id)
        
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            # Collection doesn't exist, create it
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"classroom_id": str(classroom_id)}
            )
        
        return collection
    
    def add_event_embedding(
        self,
        classroom_id: UUID,
        event_id: UUID,
        embedding: Any,  # numpy array or list
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add or update an event embedding in the vector store.
        
        If the event already exists, it will be updated.
        
        Args:
            classroom_id: UUID of the classroom
            event_id: UUID of the event
            embedding: Embedding vector (numpy array or list)
            metadata: Optional metadata (e.g., event_type, result, etc.)
            
        Raises:
            ImportError: If chromadb is not installed.
            Exception: If embedding cannot be added.
        """
        collection = self.get_or_create_collection(classroom_id)
        
        # Convert embedding to list if it's a numpy array
        if hasattr(embedding, 'tolist'):
            embedding_list = embedding.tolist()
        else:
            embedding_list = list(embedding)
        
        # Prepare metadata
        event_metadata = {
            "event_id": str(event_id),
            "classroom_id": str(classroom_id)
        }
        if metadata:
            event_metadata.update(metadata)
        
        # Add or update embedding
        # ChromaDB will update if the ID already exists
        collection.upsert(
            ids=[str(event_id)],
            embeddings=[embedding_list],
            metadatas=[event_metadata]
        )
    
    def search_similar_events(
        self,
        classroom_id: UUID,
        query_embedding: Any,  # numpy array or list
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        min_similarity: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar events using semantic similarity.
        
        Args:
            classroom_id: UUID of the classroom to search in
            query_embedding: Embedding vector to search for
            top_k: Number of similar events to return (default: 5)
            filters: Optional metadata filters (e.g., {"event_type": "TRANSICION"})
            min_similarity: Minimum similarity score (0.0 to 1.0). If None, no threshold.
            
        Returns:
            List[Dict]: List of similar events with scores, each containing:
                - "event_id": UUID of the event
                - "score": Similarity score (0.0 to 1.0)
                - "metadata": Event metadata
                
        Raises:
            ImportError: If chromadb is not installed.
            Exception: If search fails.
        """
        collection = self.get_or_create_collection(classroom_id)
        
        # Convert embedding to list if it's a numpy array
        if hasattr(query_embedding, 'tolist'):
            query_embedding_list = query_embedding.tolist()
        else:
            query_embedding_list = list(query_embedding)
        
        # Prepare where clause for filtering
        where_clause = None
        if filters:
            where_clause = filters
        
        # Search for similar events
        results = collection.query(
            query_embeddings=[query_embedding_list],
            n_results=top_k,
            where=where_clause
        )
        
        # Format results
        similar_events = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i, event_id in enumerate(results['ids'][0]):
                # ChromaDB returns distances, convert to similarity scores
                # Distance 0 = similarity 1.0, higher distance = lower similarity
                distance = results['distances'][0][i]
                similarity = 1.0 - distance  # Convert distance to similarity
                
                # Apply minimum similarity threshold if specified
                if min_similarity is not None and similarity < min_similarity:
                    continue
                
                similar_events.append({
                    "event_id": UUID(event_id),
                    "score": similarity,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                })
        
        return similar_events
    
    def delete_event_embedding(
        self,
        classroom_id: UUID,
        event_id: UUID
    ) -> None:
        """
        Delete an event embedding from the vector store.
        
        Args:
            classroom_id: UUID of the classroom
            event_id: UUID of the event to delete
            
        Raises:
            ImportError: If chromadb is not installed.
            Exception: If deletion fails.
        """
        collection = self.get_or_create_collection(classroom_id)
        
        try:
            collection.delete(ids=[str(event_id)])
        except Exception as e:
            # If event doesn't exist, that's okay (idempotent operation)
            pass
    
    def delete_classroom_collection(self, classroom_id: UUID) -> None:
        """
        Delete all embeddings for a classroom (delete the entire collection).
        
        This is useful when a classroom is deleted.
        
        Args:
            classroom_id: UUID of the classroom
            
        Raises:
            ImportError: If chromadb is not installed.
            Exception: If deletion fails.
        """
        collection_name = self._get_collection_name(classroom_id)
        
        try:
            self.client.delete_collection(name=collection_name)
        except Exception as e:
            # If collection doesn't exist, that's okay
            pass
    
    def get_collection_count(self, classroom_id: UUID) -> int:
        """
        Get the number of events stored in a classroom's collection.
        
        Args:
            classroom_id: UUID of the classroom
            
        Returns:
            int: Number of events in the collection
        """
        collection = self.get_or_create_collection(classroom_id)
        return collection.count()

