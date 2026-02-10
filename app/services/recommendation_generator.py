"""
Recommendation Generator Service for AULA+

This service generates pedagogical recommendations based on detected patterns.
Uses pattern analysis results to create actionable recommendations with confidence scores.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from app.services.pattern_analysis import PatternAnalysisService
from app.schemas.enums import RecommendationType, ConfidenceLevel


class RecommendationGenerator:
    """
    Service for generating recommendations from pattern analysis.
    
    Analyzes patterns and creates actionable recommendations with:
    - Confidence scores based on pattern strength
    - Explanations of detected patterns
    - Applicable contexts
    """
    
    def __init__(self, db_session=None):
        """
        Initialize RecommendationGenerator.
        
        Args:
            db_session: Optional database session (needed for pattern analysis)
        """
        self.db = db_session
    
    def calculate_confidence(
        self,
        pattern_strength: float,
        sample_size: int,
        success_rate: Optional[float] = None
    ) -> ConfidenceLevel:
        """
        Calculate confidence level based on pattern strength and sample size.
        
        Args:
            pattern_strength: Strength of the pattern (0.0 to 1.0)
            sample_size: Number of events that support this pattern
            success_rate: Optional success rate (0.0 to 1.0)
            
        Returns:
            ConfidenceLevel: ALTA, MEDIA, or BAJA
        """
        # Base confidence on sample size
        if sample_size >= 5:
            size_score = 1.0
        elif sample_size >= 3:
            size_score = 0.7
        else:
            size_score = 0.4
        
        # Factor in pattern strength
        strength_score = pattern_strength
        
        # Factor in success rate if available
        if success_rate is not None:
            success_score = success_rate
            # Average of all factors
            final_score = (size_score + strength_score + success_score) / 3
        else:
            # Average of size and strength
            final_score = (size_score + strength_score) / 2
        
        # Determine confidence level
        if final_score >= 0.75:
            return ConfidenceLevel.ALTA
        elif final_score >= 0.5:
            return ConfidenceLevel.MEDIA
        else:
            return ConfidenceLevel.BAJA
    
    def generate_support_recommendations(
        self,
        support_effectiveness: Dict[str, Any],
        temporal_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on support effectiveness patterns.
        
        Args:
            support_effectiveness: Results from analyze_support_effectiveness
            temporal_patterns: Results from detect_temporal_patterns
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Get most effective supports
        most_effective = support_effectiveness.get("most_effective_supports", [])
        successful_combinations = support_effectiveness.get("successful_combinations", [])
        
        # Recommendation 1: Most effective individual support
        if most_effective and len(most_effective) > 0:
            top_support = most_effective[0]
            support_name = top_support["support"]
            success_rate = top_support["success_rate"]
            usage_count = support_effectiveness.get("support_usage_counts", {}).get(support_name, 0)
            
            # Calculate confidence
            confidence = self.calculate_confidence(
                pattern_strength=success_rate,
                sample_size=usage_count,
                success_rate=success_rate
            )
            
            # Get temporal context if available
            context_info = ""
            if temporal_patterns.get("most_common_moment"):
                context_info = f" especialmente en {temporal_patterns['most_common_moment']}"
            
            # Generate more natural, pedagogical language
            if success_rate >= 0.9:
                effectiveness_desc = "muy alta efectividad"
                recommendation_text = "se recomienda priorizar su uso"
            elif success_rate >= 0.7:
                effectiveness_desc = "buena efectividad"
                recommendation_text = "se recomienda considerarlo como opción preferente"
            else:
                effectiveness_desc = "efectividad moderada"
                recommendation_text = "puede ser útil en situaciones similares"
            
            recommendation = {
                "recommendation_type": RecommendationType.ESTRATEGIA,
                "title": f"Priorizar uso de {support_name}",
                "description": (
                    f"El apoyo '{support_name}' ha mostrado {effectiveness_desc} "
                    f"({success_rate * 100:.0f}% de éxito) en {usage_count} situaciones analizadas"
                    f"{context_info}. {recommendation_text.capitalize()} cuando se presenten situaciones similares."
                ),
                "applicable_context": (
                    f"Considerar {support_name} cuando se presenten situaciones similares a las analizadas"
                    f"{context_info}. Los datos históricos del aula muestran que este apoyo "
                    f"ha funcionado de manera consistente en estos contextos."
                ),
                "detected_pattern": (
                    f"Análisis de {usage_count} eventos muestra que {support_name} se utilizó con "
                    f"una tasa de éxito del {success_rate * 100:.0f}%. "
                    f"Este patrón sugiere que es una estrategia efectiva para este aula."
                ),
                "confidence": confidence
            }
            recommendations.append(recommendation)
        
        # Recommendation 2: Successful support combinations
        if successful_combinations and len(successful_combinations) > 0:
            top_combination = successful_combinations[0]
            supports = top_combination["supports"]
            success_rate = top_combination["success_rate"]
            usage_count = top_combination["usage_count"]
            
            supports_text = " + ".join(supports)
            
            # Calculate confidence
            confidence = self.calculate_confidence(
                pattern_strength=success_rate,
                sample_size=usage_count,
                success_rate=success_rate
            )
            
            # Generate more natural language for combinations
            if success_rate >= 0.9:
                combo_desc = "especialmente efectiva"
                combo_advice = "se recomienda usar esta combinación"
            elif success_rate >= 0.7:
                combo_desc = "muy efectiva"
                combo_advice = "puede ser muy útil usar esta combinación"
            else:
                combo_desc = "efectiva"
                combo_advice = "puede ser útil considerar esta combinación"
            
            recommendation = {
                "recommendation_type": RecommendationType.ESTRATEGIA,
                "title": f"Combinar apoyos: {supports_text}",
                "description": (
                    f"La combinación de '{supports_text}' ha demostrado ser {combo_desc} "
                    f"con una tasa de éxito del {success_rate * 100:.0f}% en {usage_count} situaciones. "
                    f"{combo_advice.capitalize()} cuando se presenten contextos similares."
                ),
                "applicable_context": (
                    f"En situaciones que requieran apoyo adicional, {combo_advice}: {supports_text}. "
                    f"Los datos del aula muestran que esta combinación ha funcionado bien "
                    f"en contextos similares, sugiriendo una sinergia entre estos apoyos."
                ),
                "detected_pattern": (
                    f"Análisis de {usage_count} eventos muestra que la combinación de {supports_text} "
                    f"se utilizó con una tasa de éxito del {success_rate * 100:.0f}%. "
                    f"Este patrón indica que estos apoyos funcionan bien juntos en este contexto."
                ),
                "confidence": confidence
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def generate_temporal_recommendations(
        self,
        temporal_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on temporal patterns.
        
        Args:
            temporal_patterns: Results from detect_temporal_patterns
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        most_common_day = temporal_patterns.get("most_common_day")
        most_common_moment = temporal_patterns.get("most_common_moment")
        day_counts = temporal_patterns.get("day_of_week", {})
        moment_counts = temporal_patterns.get("moment_of_day", {})
        
        # Recommendation: Temporal pattern for anticipation
        if most_common_day and most_common_moment:
            day_count = day_counts.get(most_common_day, 0)
            moment_count = moment_counts.get(most_common_moment, 0)
            total_events = sum(day_counts.values())
            
            if total_events > 0:
                day_percentage = (day_count / total_events) * 100
                
                # Calculate confidence based on pattern strength
                pattern_strength = day_count / max(total_events, 1)
                confidence = self.calculate_confidence(
                    pattern_strength=pattern_strength,
                    sample_size=day_count
                )
                
                # Generate more natural temporal recommendation
                if day_percentage >= 50:
                    temporal_desc = "momento crítico"
                    temporal_advice = "es especialmente importante preparar"
                elif day_percentage >= 30:
                    temporal_desc = "momento que requiere atención"
                    temporal_advice = "se recomienda preparar"
                else:
                    temporal_desc = "momento a considerar"
                    temporal_advice = "puede ser útil preparar"
                
                recommendation = {
                    "recommendation_type": RecommendationType.ANTICIPACION,
                    "title": f"Anticipar eventos los {most_common_day}s por la {most_common_moment}",
                    "description": (
                        f"El análisis de eventos muestra que los {most_common_day}s por la {most_common_moment} "
                        f"concentran el {day_percentage:.0f}% de los eventos registrados ({day_count} de {total_events}). "
                        f"Esto sugiere que {temporal_advice} estrategias de anticipación para estos momentos."
                    ),
                    "applicable_context": (
                        f"Los {most_common_day}s por la {most_common_moment} han sido identificados como un {temporal_desc}. "
                        f"Se recomienda preparar con anticipación estrategias de apoyo, rutinas claras y "
                        f"recursos necesarios para facilitar la transición en estos momentos."
                    ),
                    "detected_pattern": (
                        f"Análisis temporal: {day_count} de {total_events} eventos ({day_percentage:.0f}%) "
                        f"ocurrieron los {most_common_day}s por la {most_common_moment}. "
                        f"Este patrón recurrente indica que estos momentos requieren planificación anticipada."
                    ),
                    "confidence": confidence
                }
                recommendations.append(recommendation)
        
        return recommendations
    
    def generate_clustering_recommendations(
        self,
        clustering: Dict[str, Any],
        events: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on event clusters.
        
        Args:
            clustering: Results from cluster_similar_events
            events: List of Event model objects
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        clusters = clustering.get("clusters", [])
        
        # Analyze each cluster
        for cluster_idx, cluster_event_ids in enumerate(clusters):
            if len(cluster_event_ids) < 2:
                continue  # Skip small clusters
            
            # Get events in this cluster
            cluster_events = [
                event for event in events 
                if event.id in cluster_event_ids
            ]
            
            if not cluster_events:
                continue
            
            # Analyze cluster characteristics
            event_types = [event.event_type for event in cluster_events]
            results = [event.result for event in cluster_events]
            supports_used = []
            for event in cluster_events:
                if event.supports:
                    supports_used.extend(event.supports)
            
            # Find most common characteristics
            from collections import Counter
            most_common_type = Counter(event_types).most_common(1)[0][0] if event_types else None
            success_count = results.count("EXITOSO")
            success_rate = success_count / len(cluster_events) if cluster_events else 0
            most_common_support = Counter(supports_used).most_common(1)[0][0] if supports_used else None
            
            # Calculate confidence
            confidence = self.calculate_confidence(
                pattern_strength=success_rate,
                sample_size=len(cluster_events),
                success_rate=success_rate
            )
            
            # Generate more natural clustering recommendation
            if success_rate >= 0.8:
                cluster_desc = "muy positivos"
                cluster_advice = "se recomienda aplicar estrategias similares"
            elif success_rate >= 0.6:
                cluster_desc = "mayormente positivos"
                cluster_advice = "puede ser útil considerar estrategias similares"
            else:
                cluster_desc = "mixtos"
                cluster_advice = "se sugiere revisar qué estrategias funcionaron mejor"
            
            recommendation = {
                "recommendation_type": RecommendationType.ESTRATEGIA,
                "title": f"Estrategia para eventos tipo {most_common_type}",
                "description": (
                    f"El análisis ha identificado {len(cluster_events)} eventos similares de tipo '{most_common_type}' "
                    f"con resultados {cluster_desc} ({success_rate * 100:.0f}% de éxito). "
                    f"Estos eventos comparten características semánticas que sugieren un patrón común. "
                    f"{cluster_advice.capitalize()} cuando se presenten situaciones similares."
                ),
                "applicable_context": (
                    f"Ante situaciones que se asemejen a eventos tipo '{most_common_type}', "
                    f"{cluster_advice}. Los eventos históricos similares pueden servir como referencia "
                    f"para decidir qué estrategias y apoyos utilizar."
                ),
                "detected_pattern": (
                    f"Análisis de similitud semántica: {len(cluster_events)} eventos de tipo '{most_common_type}' "
                    f"forman un grupo con características similares. De estos, {success_count} fueron exitosos "
                    f"({success_rate * 100:.0f}%), sugiriendo un patrón reconocible en el aula."
                ),
                "confidence": confidence
            }
            
            # Add support recommendation if available
            if most_common_support:
                recommendation["description"] += (
                    f" En estos eventos, el apoyo '{most_common_support}' fue el más utilizado."
                )
                recommendation["applicable_context"] += (
                    f" El apoyo '{most_common_support}' puede ser especialmente relevante en estos contextos."
                )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    async def generate_all_recommendations(
        self,
        classroom_id: UUID,
        events: List[Any],
        pattern_results: Optional[Dict[str, Any]] = None,
        clustering_eps: float = 0.3,
        clustering_min_samples: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Generate all recommendations from pattern analysis.
        
        Args:
            classroom_id: UUID of the classroom
            events: List of Event model objects
            pattern_results: Optional pre-computed pattern analysis results
            clustering_eps: DBSCAN eps parameter
            clustering_min_samples: DBSCAN min_samples parameter
            
        Returns:
            List of recommendation dictionaries ready to be saved
        """
        # Get pattern analysis results
        if pattern_results is None:
            if self.db is None:
                raise ValueError("Database session required for pattern analysis")
            pattern_service = PatternAnalysisService(self.db)
            pattern_results = await pattern_service.analyze_all_patterns(
                classroom_id=classroom_id,
                events=events,
                clustering_eps=clustering_eps,
                clustering_min_samples=clustering_min_samples
            )
        
        all_recommendations = []
        
        # Generate recommendations from support effectiveness
        support_recs = self.generate_support_recommendations(
            support_effectiveness=pattern_results.get("support_effectiveness", {}),
            temporal_patterns=pattern_results.get("temporal_patterns", {})
        )
        all_recommendations.extend(support_recs)
        
        # Generate recommendations from temporal patterns
        temporal_recs = self.generate_temporal_recommendations(
            temporal_patterns=pattern_results.get("temporal_patterns", {})
        )
        all_recommendations.extend(temporal_recs)
        
        # Generate recommendations from clustering
        clustering_recs = self.generate_clustering_recommendations(
            clustering=pattern_results.get("clustering", {}),
            events=events
        )
        all_recommendations.extend(clustering_recs)
        
        return all_recommendations

