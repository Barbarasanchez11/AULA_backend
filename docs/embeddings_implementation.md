# Embeddings Implementation - AULA+ Backend

**Fecha**: 9 de febrero de 2026  
**Estado**: Fase 2 completada - Sistema de embeddings híbrido funcional

---

## Resumen Ejecutivo

Este documento describe la implementación del sistema de embeddings semánticos para AULA+, que permite encontrar eventos pedagógicos similares mediante búsqueda semántica. El sistema utiliza un enfoque híbrido con dos modelos de embeddings y almacenamiento vectorial persistente con ChromaDB.

**Características principales:**
- Sistema híbrido: modelo rápido (distiluse) y modelo de calidad (mpnet)
- Lazy loading de modelos para optimizar memoria y tiempo de inicio
- Patrón Singleton para gestión eficiente de recursos
- Almacenamiento persistente con ChromaDB
- Integración automática con eventos (background tasks)
- Búsqueda semántica con filtros y umbrales de similitud

---

## Arquitectura General

```
┌─────────────────┐
│   FastAPI API   │
│  (Events Router)│
└────────┬────────┘
         │
         │ Background Tasks
         ▼
┌─────────────────────────────────────┐
│   EmbeddingService (Singleton)      │
│  ┌───────────────────────────────┐  │
│  │ Fast Model (distiluse)        │  │
│  │ - 512 dimensions              │  │
│  │ - Lazy loaded                 │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Quality Model (mpnet)         │  │
│  │ - 768 dimensions              │  │
│  │ - Lazy loaded                 │  │
│  └───────────────────────────────┘  │
└─────────────┬───────────────────────┘
              │
              │ Embeddings
              ▼
┌─────────────────────────────────────┐
│      VectorStore (ChromaDB)          │
│  ┌───────────────────────────────┐  │
│  │ Collection: classroom_{id}_fast│  │
│  │ - 512 dim embeddings          │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Collection: classroom_{id}_qual│  │
│  │ - 768 dim embeddings          │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## 1. Sistema Híbrido de Embeddings

### 1.1 Decisión Técnica

Se implementó un sistema híbrido con dos modelos para balancear velocidad y calidad semántica:

**Modelo Rápido: `distiluse-base-multilingual-cased-v2`**
- **Dimensiones**: 512
- **Velocidad**: ~0.09s por evento
- **Uso**: Búsquedas rápidas, previews, sugerencias inmediatas
- **Ventaja**: Respuesta rápida para interacciones en tiempo real

**Modelo de Calidad: `paraphrase-multilingual-mpnet-base-v2`**
- **Dimensiones**: 768
- **Velocidad**: ~0.58s por evento
- **Uso**: Clustering, análisis histórico, generación de recomendaciones
- **Ventaja**: Mayor precisión semántica (similitud 0.85 vs 0.52 del rápido)

### 1.2 Justificación

- **Volumen bajo**: 5-10 eventos/día = 3-6 segundos totales de procesamiento
- **Prioridad de calidad**: La confianza del docente depende de la coherencia semántica
- **Flexibilidad**: Permite elegir el modelo según el caso de uso
- **No tiempo real**: El sistema no opera con sensores, permite procesamiento asíncrono

---

## 2. EmbeddingService: Implementación

### 2.1 Patrón Singleton

**Ubicación**: `app/services/embeddingService.py`

El servicio implementa el patrón Singleton para garantizar:
- Una sola instancia en memoria
- Modelos cargados una sola vez
- Reutilización eficiente de recursos

```python
class EmbeddingService:
    _instance = None
    _fast_model = None
    _quality_model = None
    _fast_model_loaded = False
    _quality_model_loaded = False
    
    @staticmethod
    def get_instance() -> 'EmbeddingService':
        if EmbeddingService._instance is None:
            EmbeddingService()
        return EmbeddingService._instance
```

**¿Por qué variables de clase?**
- Compartidas entre todas las instancias (aunque solo hay una)
- Permiten verificar si los modelos ya están cargados sin crear instancias
- Evitan recargar modelos innecesariamente

**¿Por qué get_instance() es estático?**
- No requiere una instancia previa para obtener el servicio
- Permite acceso directo: `EmbeddingService.get_instance()`
- Facilita la inyección de dependencias

### 2.2 Lazy Loading

Los modelos se cargan solo cuando se necesitan por primera vez:

```python
def _load_fast_model(self) -> None:
    if EmbeddingService._fast_model_loaded:
        return  # Ya está cargado, no hacer nada
    
    # Cargar modelo solo ahora
    model_name = "distiluse-base-multilingual-cased-v2"
    EmbeddingService._fast_model = SentenceTransformer(model_name)
    EmbeddingService._fast_model_loaded = True
```

**Beneficios:**
- **Tiempo de inicio rápido**: El servidor FastAPI inicia sin cargar modelos pesados
- **Memoria eficiente**: Solo se carga el modelo que se va a usar
- **Carga bajo demanda**: Si solo se usa el modelo rápido, el de calidad nunca se carga

**Flujo de carga:**
1. Usuario llama a `generate_fast_embedding()`
2. Se verifica si el modelo está cargado (`_fast_model_loaded`)
3. Si no está cargado, se carga ahora
4. Se genera el embedding
5. Próximas llamadas reutilizan el modelo cargado

### 2.3 Combinación de Texto de Eventos

Los eventos tienen múltiples campos que aportan información semántica. Se combinan en un solo texto para generar embeddings más ricos:

```python
def combine_event_text(
    self,
    event_type: str,
    description: str,
    moment_of_day: str,
    day_of_week: Optional[str],
    supports: List[str],
    result: str,
    additional_supports: Optional[str] = None,
    observations: Optional[str] = None
) -> str:
```

**Estructura del texto combinado:**
```
{event_type}. {description}.
Momento: {moment_of_day}. Día: {day_of_week}.
Apoyos utilizados: {supports}. {additional_supports}.
Resultado: {result}.
Observaciones: {observations}.
```

**Ejemplo:**
```
TRANSICION. Transición de juego libre a asamblea matutina.
Momento: mañana. Día: lunes.
Apoyos utilizados: Anticipación visual, Mediación verbal.
Resultado: EXITOSO.
Observaciones: Todos se incorporaron sin dificultades.
```

**¿Por qué combinar?**
- Los embeddings capturan el contexto completo del evento
- Permite encontrar similitudes en diferentes aspectos (tipo, descripción, apoyos, resultado)
- Mejora la precisión de la búsqueda semántica

### 2.4 Generación de Embeddings

**Métodos principales:**

1. **`generate_fast_embedding(text: str)`**: Genera embedding con modelo rápido
2. **`generate_quality_embedding(text: str)`**: Genera embedding con modelo de calidad
3. **`generate_embeddings_batch(texts: List[str], model_type: str)`**: Procesa múltiples textos a la vez (más eficiente)
4. **`generate_event_embedding(...)`**: Método de alto nivel que combina texto y genera embedding

**Procesamiento en batch:**
```python
embeddings = model.encode(texts)  # Procesa todos a la vez
```

**Ventajas del batch:**
- Más rápido que procesar uno por uno
- Optimización interna del modelo
- Útil para regenerar embeddings de múltiples eventos

---

## 3. VectorStore: Almacenamiento con ChromaDB

### 3.1 Decisión: ChromaDB vs FAISS

**Elegido: ChromaDB**

**Razones:**
- **Persistencia automática**: Los datos se guardan en disco sin configuración adicional
- **Metadata filtering**: Permite filtrar por `event_type`, `classroom_id`, etc.
- **Búsqueda por metadata**: Más flexible que solo búsqueda vectorial
- **Fácil de usar**: API simple y clara
- **Aislamiento por colección**: Cada aula tiene sus propias colecciones

**FAISS (alternativa rechazada):**
- Más rápido en búsqueda pura
- Requiere gestión manual de persistencia
- No tiene filtrado por metadata nativo
- Más complejo de configurar

### 3.2 Estructura de Colecciones

**Separación por modelo y aula:**

```
classroom_{uuid}_fast    → Embeddings de 512 dimensiones (distiluse)
classroom_{uuid}_quality → Embeddings de 768 dimensiones (mpnet)
```

**¿Por qué colecciones separadas?**
- ChromaDB requiere que todos los embeddings en una colección tengan la misma dimensión
- Permite búsquedas independientes con cada modelo
- Facilita la gestión y el mantenimiento

**Aislamiento de datos:**
- Cada aula tiene sus propias colecciones
- No hay riesgo de mezclar datos entre aulas
- Cumple con requisitos de privacidad y aislamiento

### 3.3 Operaciones Principales

**1. `get_or_create_collection(classroom_id, model_type)`**
- Obtiene una colección existente o crea una nueva
- Creación lazy: solo cuando se necesita
- Metadata incluye `classroom_id` y `model_type`

**2. `add_event_embedding(classroom_id, event_id, embedding, metadata, model_type)`**
- Almacena o actualiza un embedding
- Metadata incluye: `event_id`, `classroom_id`, `event_type`, `result`, `moment_of_day`, `original_event_id`
- Usa `upsert` para actualizar si ya existe

**3. `search_similar_events(classroom_id, query_embedding, top_k, filters, min_similarity, model_type)`**
- Búsqueda semántica por similitud de coseno
- Filtros opcionales por metadata (ej: `{"event_type": "TRANSICION"}`)
- Umbral mínimo de similitud (`min_similarity`)
- Retorna eventos ordenados por score (mayor a menor)

**4. `delete_event_embedding(classroom_id, event_id, delete_both_models)`**
- Elimina embeddings de ambos modelos (fast y quality)
- Operación idempotente (no falla si no existe)

**5. `delete_classroom_collection(classroom_id)`**
- Elimina todas las colecciones de un aula
- Útil cuando se elimina un aula completa

### 3.4 Persistencia

**Ubicación**: `./chroma_db/` (directorio raíz del proyecto)

**Estructura:**
```
chroma_db/
├── chroma.sqlite3          # Base de datos SQLite de ChromaDB
└── [colecciones internas]  # Gestionadas por ChromaDB
```

**Ventajas:**
- Los embeddings persisten entre reinicios del servidor
- No se pierden datos si el servidor se detiene
- Fácil de hacer backup (copiar el directorio)

---

## 4. Integración con Eventos

### 4.1 Background Tasks

Los embeddings se generan en segundo plano usando FastAPI `BackgroundTasks`:

```python
@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    event: EventCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # Crear evento en PostgreSQL
    db.add(db_event)
    await db.commit()
    
    # Programar tarea en background (no bloquea la respuesta)
    background_tasks.add_task(
        _generate_and_store_embeddings,
        event_id=db_event.id,
        ...
    )
    
    return event_model_to_response(db_event)  # Respuesta inmediata
```

**¿Por qué background tasks?**
- **No bloquea la API**: El usuario recibe respuesta inmediata
- **Procesamiento asíncrono**: Los modelos pueden tardar 0.5-1s en generar embeddings
- **Mejor experiencia**: El docente no espera a que se generen los embeddings

**Flujo completo:**
1. Usuario crea evento → `POST /events/`
2. Evento se guarda en PostgreSQL
3. API responde inmediatamente (201 Created)
4. En background: se generan embeddings (fast + quality)
5. Se almacenan en ChromaDB

### 4.2 Regeneración de Embeddings

Cuando se actualiza un evento, los embeddings se regeneran si cambian campos relevantes:

**Campos que afectan embeddings:**
- `event_type`
- `description`
- `moment_of_day`
- `day_of_week`
- `supports`
- `additional_supports`
- `result`
- `observations`

**Campos que NO afectan embeddings:**
- `duration_minutes` (no aporta información semántica relevante)

**Implementación:**
```python
@router.put("/{id}", response_model=EventResponse)
async def update_event(...):
    # Actualizar evento
    embedding_fields_updated = False
    
    # Detectar cambios en campos relevantes
    if "description" in update_data:
        embedding_fields_updated = True
    # ... otros campos
    
    # Regenerar embeddings solo si es necesario
    if embedding_fields_updated:
        background_tasks.add_task(_generate_and_store_embeddings, ...)
```

### 4.3 Eliminación de Embeddings

Cuando se elimina un evento, sus embeddings también se eliminan:

```python
@router.delete("/{id}", status_code=204)
async def delete_event(...):
    # Eliminar de PostgreSQL
    await db.delete(db_event)
    await db.commit()
    
    # Eliminar embeddings en background
    background_tasks.add_task(_delete_event_embeddings, ...)
```

**Operación idempotente:**
- Si el evento no tiene embeddings, no falla
- Si ya fue eliminado, no falla
- Segura de ejecutar múltiples veces

---

## 5. Búsqueda Semántica

### 5.1 Endpoint: `GET /events/similar`

**Parámetros:**
- `event_id` (requerido): ID del evento de referencia
- `classroom_id` (requerido): ID del aula
- `top_k` (opcional, default: 5): Número de eventos similares a retornar (1-20)
- `model_type` (opcional, default: "quality"): Modelo a usar ("fast" o "quality")
- `min_similarity` (opcional, default: 0.0): Umbral mínimo de similitud (0.0-1.0)
- `event_type_filter` (opcional): Filtrar por tipo de evento

**Ejemplo de uso:**
```bash
GET /events/similar?event_id=123&classroom_id=456&top_k=5&model_type=quality&min_similarity=0.7
```

### 5.2 Flujo de Búsqueda

1. **Validar aula y evento**: Verificar que existen en PostgreSQL
2. **Generar embedding del evento de referencia**: Usar el modelo especificado
3. **Buscar en ChromaDB**: Búsqueda semántica en la colección correspondiente
4. **Filtrar resultados**:
   - Excluir el evento de referencia
   - Aplicar filtro de tipo de evento (si se especifica)
   - Aplicar umbral de similitud
5. **Obtener eventos completos**: Consultar PostgreSQL para obtener detalles completos
6. **Retornar resultados**: Lista de eventos con score de similitud

### 5.3 Respuesta

```json
[
  {
    "event": {
      "id": "uuid",
      "event_type": "TRANSICION",
      "description": "...",
      ...
    },
    "similarity_score": 0.85
  },
  ...
]
```

**Ordenamiento:**
- Resultados ordenados por `similarity_score` (mayor a menor)
- Score de 1.0 = idéntico, 0.0 = completamente diferente

### 5.4 Casos de Uso

**Búsqueda rápida (modelo fast):**
- Previews en tiempo real
- Sugerencias mientras el usuario escribe
- Búsquedas frecuentes con menor precisión aceptable

**Búsqueda de calidad (modelo quality):**
- Análisis histórico
- Generación de recomendaciones
- Clustering de eventos similares
- Cuando se requiere máxima precisión semántica

---

## 6. Manejo de Errores

### 6.1 Dependencias Opcionales

Los servicios manejan graciosamente la ausencia de dependencias:

```python
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# Al usar:
if SentenceTransformer is None:
    raise ImportError("sentence-transformers no está instalado.")
```

**Beneficios:**
- El código puede compilar sin las dependencias pesadas
- Errores claros cuando faltan dependencias
- Facilita testing y desarrollo

### 6.2 Errores en Background Tasks

Los errores en background tasks no afectan la respuesta HTTP:

```python
def _generate_and_store_embeddings(...):
    try:
        # Generar y almacenar embeddings
        ...
    except Exception as e:
        # Log error pero no fallar
        print(f"Error generating embeddings for event {event_id}: {e}")
```

**En producción:**
- Usar un sistema de logging apropiado (ej: `logging`)
- Considerar notificaciones de errores (ej: Sentry)
- Monitorear fallos de generación de embeddings

### 6.3 Validación de Dimensiones

ChromaDB valida que todos los embeddings en una colección tengan la misma dimensión. El sistema previene errores usando colecciones separadas por modelo.

**Error común (resuelto):**
```
Collection expecting embedding with dimension of 512, got 768
```

**Solución implementada:**
- Colecciones separadas: `classroom_{id}_fast` y `classroom_{id}_quality`
- Cada colección solo contiene embeddings de su modelo correspondiente

---

## 7. Optimizaciones y Mejores Prácticas

### 7.1 Singleton Pattern
- ✅ Evita múltiples instancias del servicio
- ✅ Modelos cargados una sola vez
- ✅ Reutilización eficiente de memoria

### 7.2 Lazy Loading
- ✅ Tiempo de inicio rápido del servidor
- ✅ Carga solo lo necesario
- ✅ Memoria eficiente

### 7.3 Background Tasks
- ✅ API no bloquea
- ✅ Mejor experiencia de usuario
- ✅ Procesamiento asíncrono

### 7.4 Batch Processing
- ✅ Más eficiente para múltiples eventos
- ✅ Optimización interna del modelo
- ✅ Útil para migraciones o regeneraciones

### 7.5 Aislamiento de Datos
- ✅ Colecciones separadas por aula
- ✅ Cumple requisitos de privacidad
- ✅ Fácil de eliminar datos de un aula

---

## 8. Próximos Pasos (Fase 3)

### 8.1 Análisis de Patrones
- Clustering de eventos similares (DBSCAN/HDBSCAN)
- Detección de correlaciones temporales
- Análisis de efectividad de apoyos

### 8.2 Integración con LangGraph
- Orquestación de agentes de IA
- Flujo: Evento → Embedding → Búsqueda de patrones → Recomendación
- Validación humana progresiva

### 8.3 Generación Automática de Recomendaciones
- Basadas en patrones históricos detectados
- Sistema de priorización y confianza
- Procesamiento periódico de eventos

---

## 9. Referencias Técnicas

### 9.1 Modelos Utilizados

**distiluse-base-multilingual-cased-v2**
- Fuente: [sentence-transformers](https://www.sbert.net/docs/pretrained_models.html)
- Dimensiones: 512
- Idiomas: Multilingüe (incluye español)
- Licencia: Apache 2.0

**paraphrase-multilingual-mpnet-base-v2**
- Fuente: [sentence-transformers](https://www.sbert.net/docs/pretrained_models.html)
- Dimensiones: 768
- Idiomas: Multilingüe (incluye español)
- Licencia: Apache 2.0

### 9.2 Bibliotecas

- **sentence-transformers**: Generación de embeddings
- **chromadb**: Vector database
- **numpy**: Operaciones con arrays
- **fastapi**: Framework web (background tasks)

### 9.3 Archivos del Proyecto

- `app/services/embeddingService.py`: Servicio de embeddings
- `app/services/vector_store.py`: Servicio de vector store
- `app/routers/events.py`: Endpoints de eventos (integración)
- `requirements.txt`: Dependencias del proyecto

---

## 10. Conclusión

El sistema de embeddings implementado proporciona una base sólida para la búsqueda semántica de eventos pedagógicos. El enfoque híbrido balancea velocidad y calidad, mientras que la arquitectura modular facilita el mantenimiento y la extensión futura.

**Logros:**
- ✅ Sistema híbrido funcional (fast + quality)
- ✅ Lazy loading optimizado
- ✅ Integración automática con eventos
- ✅ Búsqueda semántica con filtros
- ✅ Persistencia y aislamiento de datos

**Listo para:**
- Análisis de patrones (Fase 3)
- Generación automática de recomendaciones
- Integración con LangGraph

---

**Última actualización**: 9 de febrero de 2026  
**Autor**: Equipo de desarrollo AULA+


