# Flujo de IA - AULA+ Backend


---

## Resumen Ejecutivo

Este documento describe el flujo completo del sistema de IA de AULA+, desde la creación de un evento hasta la generación de recomendaciones pedagógicas. El sistema utiliza embeddings semánticos, análisis de patrones y generación automática de recomendaciones basadas en datos históricos del aula.

**Principio fundamental**: El sistema aprende de patrones históricos del aula específica, no de literatura clínica general. Cada recomendación está basada en eventos reales que ocurrieron en ese contexto educativo.

---

## Flujo Completo del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO COMPLETO DEL SISTEMA                    │
└─────────────────────────────────────────────────────────────────┘

1. REGISTRO DE EVENTO
   │
   ├─> Docente crea evento (POST /events/)
   │   └─> Evento guardado en PostgreSQL
   │
   └─> Background Task: Generación de Embeddings
       ├─> EmbeddingService genera embedding rápido (distiluse)
       ├─> EmbeddingService genera embedding calidad (mpnet)
       └─> VectorStore almacena ambos en ChromaDB
           ├─> Collection: classroom_{id}_fast (512 dims)
           └─> Collection: classroom_{id}_quality (768 dims)

2. ANÁLISIS DE PATRONES (Bajo demanda)
   │
   ├─> Docente solicita análisis (GET /events/patterns)
   │
   └─> PatternAnalysisService analiza:
       ├─> Clustering: Agrupa eventos similares (DBSCAN)
       ├─> Patrones temporales: Detecta días/momentos críticos
       └─> Efectividad de apoyos: Analiza qué funciona mejor

3. GENERACIÓN DE RECOMENDACIONES (Bajo demanda)
   │
   ├─> Docente solicita recomendaciones (POST /recommendations/generate)
   │
   └─> RecommendationGenerator genera:
       ├─> Recomendaciones de estrategia (apoyos efectivos)
       ├─> Recomendaciones de anticipación (patrones temporales)
       └─> Recomendaciones de adaptación (clusters de eventos)
           │
           └─> Guarda recomendaciones en PostgreSQL

4. CONSULTA DE RECOMENDACIONES
   │
   └─> Docente consulta recomendaciones (GET /recommendations/)
       └─> Sistema retorna recomendaciones con:
           ├─> Título accionable
           ├─> Descripción clara
           ├─> Contexto de aplicación
           ├─> Patrón detectado (explicabilidad)
           └─> Nivel de confianza (ALTA/MEDIA/BAJA)
```

---

## Flujo Detallado: Registro de Evento

### Paso 1: Creación del Evento

**Endpoint**: `POST /events/`

**Input del docente:**
```json
{
  "event_type": "TRANSICION",
  "description": "Transición de juego libre a asamblea matutina",
  "context": {
    "moment_of_day": "mañana",
    "day_of_week": "lunes",
    "duration_minutes": 5
  },
  "supports": ["Anticipación visual", "Mediación verbal"],
  "result": "EXITOSO",
  "observations": "Todos se incorporaron sin dificultades",
  "classroom_id": "..."
}
```

**Proceso:**
1. Validación del aula (existe en PostgreSQL)
2. Creación del evento en PostgreSQL
3. Respuesta inmediata al docente (201 Created)
4. **Background Task**: Generación de embeddings (no bloquea la respuesta)

---

### Paso 2: Generación de Embeddings (Background)

**Servicio**: `EmbeddingService`

**Proceso:**
1. **Combinación de texto del evento**:
   ```
   TRANSICION. Transición de juego libre a asamblea matutina.
   Momento: mañana. Día: lunes.
   Apoyos utilizados: Anticipación visual, Mediación verbal.
   Resultado: EXITOSO.
   Observaciones: Todos se incorporaron sin dificultades.
   ```

2. **Generación de embedding rápido** (distiluse):
   - Modelo: `distiluse-base-multilingual-cased-v2`
   - Dimensiones: 512
   - Tiempo: ~0.09s
   - Uso: Búsquedas rápidas, previews

3. **Generación de embedding calidad** (mpnet):
   - Modelo: `paraphrase-multilingual-mpnet-base-v2`
   - Dimensiones: 768
   - Tiempo: ~0.58s
   - Uso: Análisis profundo, clustering, recomendaciones

4. **Almacenamiento en ChromaDB**:
   - Fast embedding → `classroom_{id}_fast`
   - Quality embedding → `classroom_{id}_quality`
   - Metadata: `event_id`, `event_type`, `result`, `moment_of_day`

**Resultado**: Evento indexado para búsqueda semántica

---

## Flujo Detallado: Análisis de Patrones

### Paso 1: Solicitud de Análisis

**Endpoint**: `GET /events/patterns?classroom_id={id}`

**Proceso:**
1. Validación del aula
2. Obtención de todos los eventos del aula desde PostgreSQL
3. Obtención de embeddings desde ChromaDB
4. Análisis de patrones

---

### Paso 2: Clustering de Eventos Similares

**Servicio**: `PatternAnalysisService.cluster_similar_events()`

**Algoritmo**: DBSCAN (Density-Based Spatial Clustering)

**Proceso:**
1. Obtener todos los embeddings de calidad del aula
2. Aplicar DBSCAN con:
   - `eps`: Distancia máxima entre eventos (default: 0.3)
   - `min_samples`: Mínimo de eventos para formar cluster (default: 2)
   - `metric`: Cosine distance
3. Agrupar eventos semánticamente similares
4. Identificar outliers (eventos únicos)

**Resultado**:
```json
{
  "clusters": [
    [event_id_1, event_id_2, event_id_3],  // Eventos similares
    [event_id_4, event_id_5]
  ],
  "outliers": [event_id_6],  // Eventos únicos
  "n_clusters": 2,
  "n_outliers": 1
}
```

**Interpretación**: Eventos en el mismo cluster comparten características semánticas similares (tipo, descripción, apoyos, resultado).

---

### Paso 3: Detección de Patrones Temporales

**Servicio**: `PatternAnalysisService.detect_temporal_patterns()`

**Proceso:**
1. Contar eventos por día de semana
2. Contar eventos por momento del día
3. Contar combinaciones día + momento
4. Identificar patrones más frecuentes

**Resultado**:
```json
{
  "day_of_week": {"lunes": 5, "martes": 3},
  "moment_of_day": {"mañana": 8, "tarde": 2},
  "most_common_day": "lunes",
  "most_common_moment": "mañana"
}
```

**Interpretación**: Los lunes por la mañana concentran más eventos, sugiriendo que es un momento crítico que requiere atención especial.

---

### Paso 4: Análisis de Efectividad de Apoyos

**Servicio**: `PatternAnalysisService.analyze_support_effectiveness()`

**Proceso:**
1. Para cada apoyo utilizado:
   - Contar total de usos
   - Contar eventos exitosos
   - Calcular tasa de éxito
2. Para combinaciones de apoyos:
   - Identificar combinaciones más usadas
   - Calcular tasa de éxito de combinaciones
3. Ordenar por efectividad

**Resultado**:
```json
{
  "support_success_rates": {
    "Anticipación visual": 1.0,  // 100% éxito
    "Mediación verbal": 0.6      // 60% éxito
  },
  "most_effective_supports": [
    {"support": "Anticipación visual", "success_rate": 1.0}
  ],
  "successful_combinations": [
    {
      "supports": ["Anticipación visual", "Mediación verbal"],
      "success_rate": 0.9,
      "usage_count": 5
    }
  ]
}
```

**Interpretación**: "Anticipación visual" funciona mejor individualmente, y la combinación con "Mediación verbal" es especialmente efectiva.

---

## Flujo Detallado: Generación de Recomendaciones

### Paso 1: Solicitud de Generación

**Endpoint**: `POST /recommendations/generate?classroom_id={id}`

**Proceso:**
1. Validación del aula
2. Obtención de eventos del aula
3. Análisis de patrones (si no se proporciona)
4. Generación de recomendaciones

---

### Paso 2: Generación de Recomendaciones de Estrategia

**Servicio**: `RecommendationGenerator.generate_support_recommendations()`

**Basadas en**: Efectividad de apoyos

**Proceso:**
1. Identificar apoyo más efectivo individual
2. Identificar combinaciones exitosas
3. Para cada uno:
   - Calcular confianza (basada en muestra, fuerza, éxito)
   - Generar título accionable
   - Generar descripción con estadísticas
   - Generar contexto de aplicación
   - Documentar patrón detectado

**Ejemplo de recomendación generada**:
```json
{
  "recommendation_type": "ESTRATEGIA",
  "title": "Priorizar uso de Anticipación visual",
  "description": "El apoyo 'Anticipación visual' ha demostrado una efectividad del 100% en 5 eventos analizados especialmente en mañana. Se recomienda considerarlo como primera opción en situaciones similares.",
  "applicable_context": "Aplicar Anticipación visual en situaciones similares a los eventos históricos analizados especialmente en mañana. Este apoyo ha mostrado resultados consistentemente positivos.",
  "detected_pattern": "Patrón detectado: Anticipación visual utilizado en 5 eventos con una tasa de éxito del 100%. Este apoyo muestra efectividad consistente en el contexto del aula.",
  "confidence": "ALTA"
}
```

---

### Paso 3: Generación de Recomendaciones de Anticipación

**Servicio**: `RecommendationGenerator.generate_temporal_recommendations()`

**Basadas en**: Patrones temporales

**Proceso:**
1. Identificar día y momento más frecuentes
2. Calcular porcentaje de eventos en ese momento
3. Generar recomendación de anticipación
4. Calcular confianza basada en frecuencia

**Ejemplo de recomendación generada**:
```json
{
  "recommendation_type": "ANTICIPACION",
  "title": "Anticipar eventos los lunes por la mañana",
  "description": "Se ha detectado un patrón temporal: los lunes por la mañana concentran el 100% de los eventos (5 de 5 eventos). Se recomienda preparar estrategias de anticipación para estos momentos.",
  "applicable_context": "Los lunes por la mañana son momentos críticos. Preparar con anticipación estrategias de apoyo y rutinas claras para estos momentos.",
  "detected_pattern": "Patrón temporal detectado: 5 eventos ocurrieron los lunes por la mañana (100% del total). Este patrón sugiere que estos momentos requieren atención especial.",
  "confidence": "ALTA"
}
```

---

### Paso 4: Generación de Recomendaciones de Adaptación

**Servicio**: `RecommendationGenerator.generate_clustering_recommendations()`

**Basadas en**: Clusters de eventos similares

**Proceso:**
1. Para cada cluster de eventos:
   - Analizar características comunes (tipo, apoyos, resultado)
   - Calcular tasa de éxito del cluster
   - Generar recomendación de estrategia
2. Calcular confianza basada en tamaño y éxito del cluster

**Ejemplo de recomendación generada**:
```json
{
  "recommendation_type": "ESTRATEGIA",
  "title": "Estrategia para eventos tipo TRANSICION",
  "description": "Se identificaron 3 eventos similares de tipo 'TRANSICION' con una tasa de éxito del 100%. Estos eventos comparten características semánticas similares.",
  "applicable_context": "Cuando se presente una situación similar a eventos tipo 'TRANSICION', considerar las estrategias que funcionaron en eventos similares anteriores.",
  "detected_pattern": "Cluster detectado: 3 eventos semánticamente similares de tipo 'TRANSICION' con 3 eventos exitosos. Estos eventos forman un patrón reconocible en el aula.",
  "confidence": "ALTA"
}
```

---

### Paso 5: Cálculo de Confianza

**Servicio**: `RecommendationGenerator.calculate_confidence()`

**Factores considerados:**
1. **Tamaño de muestra**: Número de eventos que sustentan el patrón
   - ≥5 eventos: score alto (1.0)
   - 3-4 eventos: score medio (0.7)
   - <3 eventos: score bajo (0.4)

2. **Fuerza del patrón**: Consistencia del patrón
   - Tasa de éxito alta = mayor fuerza

3. **Tasa de éxito**: Porcentaje de eventos exitosos
   - 100% = máxima confianza
   - 70-99% = confianza media-alta
   - <70% = confianza media-baja

**Cálculo final**:
```
score_final = (score_tamaño + score_fuerza + score_éxito) / 3
```

**Niveles de confianza:**
- **ALTA**: score ≥ 0.75
- **MEDIA**: score 0.5 - 0.75
- **BAJA**: score < 0.5

---

### Paso 6: Almacenamiento de Recomendaciones

**Proceso:**
1. Cada recomendación generada se guarda en PostgreSQL
2. Campos guardados:
   - `recommendation_type`: Tipo (ESTRATEGIA, ANTICIPACION, ADAPTACION)
   - `title`: Título accionable
   - `description`: Descripción detallada
   - `applicable_context`: Cuándo aplicar
   - `detected_pattern`: Patrón que la sustenta (explicabilidad)
   - `confidence`: Nivel de confianza (ALTA, MEDIA, BAJA)
   - `classroom_id`: Aula a la que pertenece
   - `generated_at`: Fecha de generación

3. Retorno de recomendaciones al docente

---

## Flujo Detallado: Consulta de Recomendaciones

### Paso 1: Solicitud de Recomendaciones

**Endpoint**: `GET /recommendations/?classroom_id={id}`

**Proceso:**
1. Validación del aula
2. Obtención de recomendaciones desde PostgreSQL
3. Retorno ordenado por fecha de generación (más recientes primero)

**Respuesta**:
```json
[
  {
    "id": "...",
    "recommendation_type": "ESTRATEGIA",
    "title": "Priorizar uso de Anticipación visual",
    "description": "...",
    "applicable_context": "...",
    "detected_pattern": "...",
    "confidence": "ALTA",
    "classroom_id": "...",
    "generated_at": "2026-02-09T15:35:52.415332"
  },
  ...
]
```

---

## Búsqueda Semántica de Eventos Similares

### Flujo: Buscar Eventos Similares

**Endpoint**: `GET /events/similar?event_id={id}&classroom_id={id}`

**Proceso:**
1. Obtener evento de referencia desde PostgreSQL
2. Generar embedding del evento (usando modelo especificado)
3. Buscar eventos similares en ChromaDB usando búsqueda por coseno
4. Filtrar resultados:
   - Excluir el evento de referencia
   - Aplicar filtro de tipo de evento (opcional)
   - Aplicar umbral de similitud mínimo
5. Obtener eventos completos desde PostgreSQL
6. Retornar eventos ordenados por similitud

**Uso**: Permite al docente ver eventos históricos similares a uno actual, para entender qué estrategias funcionaron antes.

---

## Principios de Diseño

### 1. Explicabilidad

**Cada recomendación incluye:**
- `detected_pattern`: Explicación clara del patrón que la sustenta
- Estadísticas concretas (número de eventos, tasa de éxito)
- Contexto de aplicación específico

**Objetivo**: El docente entiende por qué se generó la recomendación y puede validarla.

### 2. Control Humano

**Características:**
- Recomendaciones bajo demanda (no automáticas)
- El docente decide cuándo generar recomendaciones
- El docente decide qué aplicar
- No hay prescripciones, solo sugerencias

**Objetivo**: El docente mantiene control total sobre las decisiones pedagógicas.

### 3. Aprendizaje del Contexto Específico

**Características:**
- Cada aula tiene sus propios patrones
- Recomendaciones basadas en eventos históricos del aula
- No usa conocimiento general, solo experiencia del aula

**Objetivo**: Recomendaciones relevantes para el contexto específico.

### 4. Privacidad por Diseño

**Características:**
- Aislamiento de datos por aula
- Sin datos personales en embeddings
- Sin datos personales en recomendaciones
- Anonimización desde el registro

**Objetivo**: Cumplimiento estricto de privacidad y protección de datos.

---

## Flujo Futuro: Con LangGraph

### Cambios Esperados

1. **Orquestación de Agentes**:
   - Agente de análisis de patrones
   - Agente de generación de recomendaciones
   - Agente de validación

2. **Generación de Texto con LLMs**:
   - Descripciones más naturales
   - Contexto más rico
   - Personalización mejorada

3. **Flujo Automatizado**:
   - Generación automática periódica
   - Notificaciones al docente
   - Feedback loop para mejora continua

4. **Validación Humana Progresiva**:
   - Nivel 1: Patrones observados (actual)
   - Nivel 2: Feedback del docente (futuro)
   - Nivel 3: Curaduría de expertos (futuro)

---

## Diagrama de Flujo Simplificado

```
EVENTO CREADO
    │
    ├─> PostgreSQL (persistencia)
    │
    └─> Background: Embeddings
        │
        ├─> EmbeddingService (fast + quality)
        │
        └─> ChromaDB (búsqueda semántica)
            │
            └─> Listo para análisis

ANÁLISIS SOLICITADO
    │
    └─> PatternAnalysisService
        │
        ├─> Clustering (DBSCAN)
        ├─> Patrones temporales
        └─> Efectividad de apoyos
            │
            └─> Resultados de análisis

GENERACIÓN SOLICITADA
    │
    └─> RecommendationGenerator
        │
        ├─> Recomendaciones de estrategia
        ├─> Recomendaciones de anticipación
        └─> Recomendaciones de adaptación
            │
            ├─> Cálculo de confianza
            │
            └─> PostgreSQL (recomendaciones guardadas)
                │
                └─> Docente consulta recomendaciones
```

---

## Casos de Uso

### Caso 1: Docente registra evento exitoso

1. Docente crea evento: "Transición exitosa usando Anticipación visual"
2. Sistema genera embeddings automáticamente
3. Docente solicita análisis de patrones
4. Sistema detecta: "Anticipación visual tiene 100% éxito"
5. Docente genera recomendaciones
6. Sistema recomienda: "Priorizar Anticipación visual" (confianza ALTA)

### Caso 2: Docente busca eventos similares

1. Docente tiene un evento actual: "Transición difícil"
2. Docente busca eventos similares
3. Sistema encuentra 3 eventos similares históricos
4. Docente ve qué apoyos funcionaron en esos eventos
5. Docente decide aplicar estrategias similares

### Caso 3: Docente anticipa momento crítico

1. Docente solicita análisis de patrones
2. Sistema detecta: "Lunes por la mañana = 80% de eventos"
3. Docente genera recomendaciones
4. Sistema recomienda: "Anticipar eventos los lunes por la mañana"
5. Docente prepara estrategias de anticipación

---

## Limitaciones Actuales

1. **Sin LangGraph**: Recomendaciones basadas en reglas, no en LLMs
2. **Sin feedback loop**: Recomendaciones no se ajustan con feedback
3. **Requiere suficientes eventos**: Clustering efectivo necesita 2+ eventos similares
4. **Sin procesamiento automático**: Recomendaciones solo bajo demanda

---

## Próximos Pasos

1. **Integración con LangGraph**: Orquestación de agentes y generación con LLMs
2. **Feedback del docente**: Sistema para validar y ajustar recomendaciones
3. **Procesamiento periódico**: Generación automática de recomendaciones
4. **Mejora continua**: Ajuste de patrones basado en feedback

---


