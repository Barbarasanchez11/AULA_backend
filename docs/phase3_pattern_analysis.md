# Fase 3: Análisis de Patrones y Generación de Recomendaciones

**Fecha de implementación**: 9 de febrero de 2026  
**Estado**: ✅ Completada (sin LangGraph)

---

## Resumen Ejecutivo

Esta fase implementa el análisis automático de patrones en eventos pedagógicos y la generación de recomendaciones basadas en esos patrones. El sistema puede detectar similitudes semánticas, patrones temporales y efectividad de apoyos, generando recomendaciones accionables con niveles de confianza.

**Características principales:**
- Clustering de eventos similares usando DBSCAN
- Detección de patrones temporales (día de semana, momento del día)
- Análisis de efectividad de apoyos pedagógicos
- Generación automática de recomendaciones
- Sistema de confianza basado en fuerza de patrones

---

## Arquitectura

```
┌─────────────────────┐
│   FastAPI Endpoint  │
│  GET /events/       │
│  patterns           │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────┐
│  PatternAnalysisService      │
│  ┌────────────────────────┐  │
│  │ cluster_similar_events │  │
│  │ (DBSCAN on embeddings) │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ detect_temporal_       │  │
│  │ patterns               │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ analyze_support_       │  │
│  │ effectiveness          │  │
│  └────────────────────────┘  │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  RecommendationGenerator     │
│  ┌────────────────────────┐  │
│  │ generate_support_      │  │
│  │ recommendations        │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ generate_temporal_    │  │
│  │ recommendations        │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ generate_clustering_  │  │
│  │ recommendations        │  │
│  └────────────────────────┘  │
└──────────┬───────────────────┘
           │
           ▼
┌─────────────────────┐
│  PostgreSQL         │
│  Recommendations     │
└─────────────────────┘
```

---

## Componentes Implementados

### 1. PatternAnalysisService

**Ubicación**: `app/services/pattern_analysis.py`

Servicio que analiza patrones en eventos pedagógicos.

#### Métodos principales:

**`cluster_similar_events()`**
- Agrupa eventos semánticamente similares usando DBSCAN
- Parámetros:
  - `eps`: Distancia máxima entre eventos (0.0-1.0)
  - `min_samples`: Mínimo de eventos para formar cluster
- Retorna: clusters, outliers, estadísticas

**`detect_temporal_patterns()`**
- Analiza cuándo ocurren los eventos
- Detecta:
  - Día de semana más común
  - Momento del día más común
  - Combinaciones día + momento
- Retorna: estadísticas de frecuencia temporal

**`analyze_support_effectiveness()`**
- Analiza qué apoyos funcionan mejor
- Calcula:
  - Tasa de éxito por apoyo
  - Apoyos más efectivos
  - Combinaciones exitosas
- Retorna: estadísticas de efectividad

**`analyze_all_patterns()`**
- Ejecuta los tres análisis y retorna resultados completos

---

### 2. RecommendationGenerator

**Ubicación**: `app/services/recommendation_generator.py`

Servicio que genera recomendaciones desde patrones detectados.

#### Métodos principales:

**`calculate_confidence()`**
- Calcula nivel de confianza (ALTA/MEDIA/BAJA)
- Factores:
  - Tamaño de muestra (número de eventos)
  - Fuerza del patrón
  - Tasa de éxito

**`generate_support_recommendations()`**
- Genera recomendaciones basadas en efectividad de apoyos
- Tipos:
  - Apoyo individual más efectivo
  - Combinaciones exitosas

**`generate_temporal_recommendations()`**
- Genera recomendaciones de anticipación
- Basadas en patrones temporales detectados

**`generate_clustering_recommendations()`**
- Genera recomendaciones desde clusters de eventos
- Estrategias para tipos de eventos similares

**`generate_all_recommendations()`**
- Genera todas las recomendaciones combinando análisis

---

## Endpoints

### GET /events/patterns

Analiza patrones en eventos de un aula.

**Parámetros:**
- `classroom_id` (requerido): ID del aula
- `clustering_eps` (opcional, default: 0.3): Parámetro DBSCAN eps
- `clustering_min_samples` (opcional, default: 2): Parámetro DBSCAN min_samples

**Respuesta:**
```json
{
  "clustering": {
    "clusters": [[event_id1, event_id2], [event_id3]],
    "outliers": [event_id4],
    "n_clusters": 2,
    "n_outliers": 1
  },
  "temporal_patterns": {
    "day_of_week": {"lunes": 5},
    "moment_of_day": {"mañana": 5},
    "most_common_day": "lunes",
    "most_common_moment": "mañana"
  },
  "support_effectiveness": {
    "support_success_rates": {
      "Anticipación visual": 1.0
    },
    "most_effective_supports": [...],
    "successful_combinations": [...]
  }
}
```

---

### POST /recommendations/generate

Genera recomendaciones automáticamente desde patrones.

**Parámetros:**
- `classroom_id` (requerido): ID del aula
- `clustering_eps` (opcional, default: 0.3): Parámetro DBSCAN eps
- `clustering_min_samples` (opcional, default: 2): Parámetro DBSCAN min_samples

**Respuesta:**
Lista de recomendaciones generadas y guardadas en la base de datos.

**Ejemplo:**
```json
[
  {
    "recommendation_type": "ESTRATEGIA",
    "title": "Priorizar uso de Anticipación visual",
    "description": "El apoyo 'Anticipación visual' ha demostrado una efectividad del 100%...",
    "applicable_context": "Aplicar Anticipación visual en situaciones similares...",
    "detected_pattern": "Patrón detectado: Anticipación visual utilizado en 5 eventos...",
    "confidence": "ALTA",
    "id": "...",
    "classroom_id": "...",
    "generated_at": "2026-02-09T15:35:52.415332"
  }
]
```

---

## Tipos de Recomendaciones Generadas

### 1. Recomendaciones de Estrategia (ESTRATEGIA)

**Basadas en efectividad de apoyos:**
- Apoyo individual más efectivo
- Combinaciones exitosas de apoyos

**Ejemplo:**
- "Priorizar uso de Anticipación visual" (100% efectividad en 5 eventos)
- "Combinar apoyos: Anticipación visual + Mediación verbal" (100% efectividad)

### 2. Recomendaciones de Anticipación (ANTICIPACION)

**Basadas en patrones temporales:**
- Días y momentos críticos
- Preparación anticipada

**Ejemplo:**
- "Anticipar eventos los lunes por la mañana" (100% de eventos en ese momento)

### 3. Recomendaciones de Adaptación (ADAPTACION)

**Basadas en clusters de eventos:**
- Estrategias para tipos de eventos similares
- (Implementado pero requiere más eventos para clusters)

---

## Sistema de Confianza

El sistema calcula confianza basándose en:

1. **Tamaño de muestra**: Más eventos = mayor confianza
   - ≥5 eventos: score alto
   - 3-4 eventos: score medio
   - <3 eventos: score bajo

2. **Fuerza del patrón**: Qué tan consistente es
   - Tasa de éxito alta = mayor confianza

3. **Tasa de éxito**: Porcentaje de eventos exitosos
   - 100% = máxima confianza
   - 70-99% = confianza media-alta
   - <70% = confianza media-baja

**Niveles:**
- **ALTA**: Score ≥ 0.75
- **MEDIA**: Score 0.5 - 0.75
- **BAJA**: Score < 0.5

---

## Ejemplo de Uso Completo

### 1. Analizar patrones

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/events/patterns?classroom_id={id}' \
  -H 'accept: application/json'
```

### 2. Generar recomendaciones

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/recommendations/generate?classroom_id={id}' \
  -H 'accept: application/json'
```

### 3. Ver recomendaciones generadas

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/recommendations/?classroom_id={id}' \
  -H 'accept: application/json'
```

---

## Limitaciones Actuales

1. **Sin LangGraph**: Las recomendaciones se generan directamente desde patrones, sin orquestación de agentes de IA
2. **Recomendaciones basadas en reglas**: No usan LLMs para generar texto, solo patrones detectados
3. **Requiere suficientes eventos**: Para clustering efectivo, se necesitan al menos 2-3 eventos similares
4. **Sin feedback loop**: Las recomendaciones no se ajustan basándose en feedback del docente (futuro)

---

## Próximos Pasos (Fase 3 con LangGraph)

1. **Integración con LangGraph**:
   - Orquestación de agentes de IA
   - Generación de texto más natural
   - Flujo completo automatizado

2. **Mejoras en recomendaciones**:
   - Más contexto en las descripciones
   - Recomendaciones más personalizadas
   - Validación humana progresiva

3. **Feedback del docente**:
   - Sistema para que el docente valide recomendaciones
   - Ajuste de patrones basado en feedback

---

## Archivos Creados/Modificados

- `app/services/pattern_analysis.py`: Servicio de análisis de patrones
- `app/services/recommendation_generator.py`: Servicio de generación de recomendaciones
- `app/routers/events.py`: Endpoint `GET /events/patterns`
- `app/routers/recommendations.py`: Endpoint `POST /recommendations/generate`
- `app/schemas/event.py`: Schema `PatternAnalysisResponse`

---

**Última actualización**: 9 de febrero de 2026  
**Autor**: Equipo de desarrollo AULA+

