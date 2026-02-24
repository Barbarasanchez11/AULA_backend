"""
Pattern Analysis Service for AULA+

This service analyzes patterns in pedagogical events to detect:
- Clusters of similar events (using DBSCAN on embeddings)
- Temporal correlations (day of week, moment of day patterns)
- Support effectiveness (which supports work best for which situations)

Uses embeddings from VectorStore and event data from database.
"""

from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime
from collections import Counter, defaultdict

# Optional imports for clustering
try:
    from sklearn.cluster import DBSCAN
    import numpy as np
except ImportError:
    DBSCAN = None
    np = None

from app.services.vector_store import VectorStore
from app.services.embeddingService import EmbeddingService


class PatternAnalysisService:
    """
    Service for analyzing patterns in pedagogical events.
    
    Detects:
    - Clusters of similar events (semantic similarity)
    - Temporal patterns (when events occur)
    - Support effectiveness (which supports work best)
    """
    
    def __init__(self):
        """Initialize PatternAnalysisService with required services."""
        self.vector_store = VectorStore()
        self.embedding_service = EmbeddingService.get_instance()
    
    def get_event_embeddings(
        self,
        classroom_id: UUID,
        model_type: str = "quality"
    ) -> Tuple[List[UUID], np.ndarray]:
        """
        Get all event embeddings for a classroom.
        
        Args:
            classroom_id: UUID of the classroom
            model_type: Model type ("fast" or "quality")
            
        Returns:
            Tuple of (event_ids, embeddings_array):
            - event_ids: List of event UUIDs
            - embeddings_array: numpy array of embeddings (n_events, embedding_dim)
            
        Raises:
            ImportError: If numpy or sklearn are not installed.
        """
        if np is None:
            raise ImportError("numpy no está instalado. Instálalo con: pip install numpy")
        
        # Get collection
        collection = self.vector_store.get_or_create_collection(classroom_id, model_type)
        
        # Get all embeddings from collection
        results = collection.get(include=['embeddings'])
        
        if not results or not results['ids']:
            return [], np.array([])
        
        # Extract event IDs and embeddings
        event_ids = []
        embeddings_list = []
        
        for i, event_id_str in enumerate(results['ids']):
            # Extract original event_id from metadata if available
            # For now, assume the ID is the event_id directly
            try:
                event_id = UUID(event_id_str)
                event_ids.append(event_id)
                embeddings_list.append(results['embeddings'][i])
            except (ValueError, TypeError):
                # Skip invalid UUIDs
                continue
        
        if not embeddings_list:
            return [], np.array([])
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings_list)
        
        return event_ids, embeddings_array
    
    def cluster_similar_events(
        self,
        classroom_id: UUID,
        eps: float = 0.3,
        min_samples: int = 2,
        model_type: str = "quality"
    ) -> Dict[str, Any]:
        """
        Cluster similar events using DBSCAN on embeddings.
        
        DBSCAN groups events that are semantically similar based on their embeddings.
        
        Args:
            classroom_id: UUID of the classroom
            eps: Maximum distance between events in the same cluster (0.0 to 1.0)
                 Lower = more strict clustering (fewer clusters, more outliers)
                 Higher = more lenient (fewer outliers, larger clusters)
            min_samples: Minimum number of events required to form a cluster
            model_type: Model type to use for embeddings ("fast" or "quality")
            
        Returns:
            Dict with:
            - "clusters": List of clusters, each containing event_ids
            - "outliers": List of event_ids that don't belong to any cluster
            - "n_clusters": Number of clusters found
            - "n_outliers": Number of outliers
            
        Raises:
            ImportError: If sklearn is not installed.
        """
        if DBSCAN is None:
            raise ImportError(
                "scikit-learn no está instalado. "
                "Instálalo con: pip install scikit-learn"
            )
        
        if np is None:
            raise ImportError("numpy no está instalado. Instálalo con: pip install numpy")
        
        # Get embeddings
        event_ids, embeddings = self.get_event_embeddings(classroom_id, model_type)
        
        if len(event_ids) < min_samples:
            return {
                "clusters": [],
                "outliers": event_ids,
                "n_clusters": 0,
                "n_outliers": len(event_ids)
            }
        
        # Apply DBSCAN clustering
        # eps is cosine distance threshold (0.0 = identical, 1.0 = completely different)
        clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        cluster_labels = clustering.fit_predict(embeddings)
        
        # Organize results
        clusters = defaultdict(list)
        outliers = []
        
        for event_id, label in zip(event_ids, cluster_labels):
            if label == -1:  # -1 means outlier in DBSCAN
                outliers.append(event_id)
            else:
                clusters[label].append(event_id)
        
        # Convert clusters dict to list
        clusters_list = [cluster for cluster in clusters.values()]
        
        return {
            "clusters": clusters_list,
            "outliers": outliers,
            "n_clusters": len(clusters_list),
            "n_outliers": len(outliers)
        }
    
    def detect_temporal_patterns(
        self,
        events: List[Any]  # List of Event models
    ) -> Dict[str, Any]:
        """
        Detect temporal patterns in events.
        
        Analyzes:
        - Day of week patterns (which days have more events)
        - Moment of day patterns (which moments have more events)
        - Day + moment combinations
        
        Args:
            events: List of Event model objects from database
            
        Returns:
            Dict with:
            - "day_of_week": Dict with day -> count
            - "moment_of_day": Dict with moment -> count
            - "day_moment_combinations": Dict with (day, moment) -> count
            - "most_common_day": Most frequent day of week
            - "most_common_moment": Most frequent moment of day
        """
        if not events:
            return {
                "day_of_week": {},
                "moment_of_day": {},
                "day_moment_combinations": {},
                "most_common_day": None,
                "most_common_moment": None
            }
        
        # Count patterns
        day_counts = Counter()
        moment_counts = Counter()
        day_moment_counts = Counter()
        
        for event in events:
            # Count day of week
            if event.day_of_week:
                day_counts[event.day_of_week] += 1
            
            # Count moment of day
            moment_counts[event.moment_of_day] += 1
            
            # Count combinations
            if event.day_of_week:
                day_moment_counts[(event.day_of_week, event.moment_of_day)] += 1
        
        # Find most common
        most_common_day = day_counts.most_common(1)[0][0] if day_counts else None
        most_common_moment = moment_counts.most_common(1)[0][0] if moment_counts else None
        
        return {
            "day_of_week": dict(day_counts),
            "moment_of_day": dict(moment_counts),
            "day_moment_combinations": {
                f"{day}_{moment}": count 
                for (day, moment), count in day_moment_counts.items()
            },
            "most_common_day": most_common_day,
            "most_common_moment": most_common_moment
        }
    
    def analyze_support_effectiveness(
        self,
        events: List[Any]  # List of Event model objects
    ) -> Dict[str, Any]:
        """
        Analyze effectiveness of different supports.
        
        Compares success rates for different supports and support combinations.
        
        Args:
            events: List of Event model objects from database
            
        Returns:
            Dict with:
            - "support_success_rates": Dict with support -> success_rate (0.0 to 1.0)
            - "most_effective_supports": List of supports ordered by effectiveness
            - "support_usage_counts": Dict with support -> number of times used
            - "successful_combinations": List of support combinations with high success rates
        """
        if not events:
            return {
                "support_success_rates": {},
                "most_effective_supports": [],
                "support_usage_counts": {},
                "successful_combinations": []
            }
        
        # Track support usage and success
        support_stats = defaultdict(lambda: {"total": 0, "successful": 0})
        combination_stats = defaultdict(lambda: {"total": 0, "successful": 0})
        
        for event in events:
            # Get supports (list from JSON column)
            supports = event.supports if event.supports else []
            
            # Determine if event was successful
            is_successful = event.result == "EXITOSO"
            
            # Track individual supports
            for support in supports:
                support_stats[support]["total"] += 1
                if is_successful:
                    support_stats[support]["successful"] += 1
            
            # Track support combinations (sorted tuple for consistency)
            if len(supports) > 1:
                support_combination = tuple(sorted(supports))
                combination_stats[support_combination]["total"] += 1
                if is_successful:
                    combination_stats[support_combination]["successful"] += 1
        
        # Calculate success rates
        support_success_rates = {}
        for support, stats in support_stats.items():
            if stats["total"] > 0:
                success_rate = stats["successful"] / stats["total"]
                support_success_rates[support] = success_rate
        
        # Calculate combination success rates
        combination_success_rates = {}
        for combination, stats in combination_stats.items():
            if stats["total"] > 0:
                success_rate = stats["successful"] / stats["total"]
                combination_success_rates[combination] = {
                    "success_rate": success_rate,
                    "usage_count": stats["total"]
                }
        
        # Sort by effectiveness
        most_effective_supports = sorted(
            support_success_rates.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Get successful combinations (success rate >= 0.7 and used at least 2 times)
        successful_combinations = [
            {
                "supports": list(combo),
                "success_rate": data["success_rate"],
                "usage_count": data["usage_count"]
            }
            for combo, data in combination_success_rates.items()
            if data["success_rate"] >= 0.7 and data["usage_count"] >= 2
        ]
        successful_combinations.sort(key=lambda x: x["success_rate"], reverse=True)
        
        return {
            "support_success_rates": support_success_rates,
            "most_effective_supports": [
                {"support": support, "success_rate": rate}
                for support, rate in most_effective_supports
            ],
            "support_usage_counts": {
                support: stats["total"] 
                for support, stats in support_stats.items()
            },
            "successful_combinations": successful_combinations
        }
    
    def analyze_all_patterns(
        self,
        classroom_id: UUID,
        events: List[Any],
        clustering_eps: float = 0.3,
        clustering_min_samples: int = 2
    ) -> Dict[str, Any]:
        """
        Perform complete pattern analysis for a classroom.
        
        Combines clustering, temporal patterns, and support effectiveness.
        
        Args:
            classroom_id: UUID of the classroom
            events: List of Event model objects from database
            clustering_eps: DBSCAN eps parameter
            clustering_min_samples: DBSCAN min_samples parameter
            
        Returns:
            Dict with all analysis results:
            - "clustering": Results from cluster_similar_events
            - "temporal_patterns": Results from detect_temporal_patterns
            - "support_effectiveness": Results from analyze_support_effectiveness
        """
        results = {}
        
        # Clustering
        try:
            results["clustering"] = self.cluster_similar_events(
                classroom_id=classroom_id,
                eps=clustering_eps,
                min_samples=clustering_min_samples
            )
        except Exception as e:
            results["clustering"] = {"error": str(e)}
        
        # Temporal patterns
        results["temporal_patterns"] = self.detect_temporal_patterns(events)
        
        # Support effectiveness
        results["support_effectiveness"] = self.analyze_support_effectiveness(events)
        
        return results

