# Comandos curl para probar endpoints de eventos con embeddings

## Prerequisitos

1. **Servidor FastAPI corriendo:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Base de datos inicializada** (PostgreSQL corriendo)

3. **Dependencias instaladas:**
   ```bash
   pip install sentence-transformers chromadb numpy<2.0
   ```

---

## Paso 1: Crear un aula

```bash
curl -X POST "http://localhost:8000/classrooms/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aula TEA Test",
    "type": "TEA"
  }'
```

**Respuesta esperada:**
```json
{
  "id": "uuid-del-aula",
  "name": "Aula TEA Test",
  "type": "TEA",
  "created_at": "2026-02-05T..."
}
```

**⚠️ IMPORTANTE:** Copia el `id` del aula, lo necesitarás para los siguientes pasos.

---

## Paso 2: Crear evento 1 (POST /events/)

```bash
curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "classroom_id": "TU-UUID-DEL-AULA-AQUI",
    "event_type": "TRANSICION",
    "description": "Transición de juego libre a asamblea matutina",
    "context": {
      "moment_of_day": "mañana",
      "day_of_week": "lunes",
      "duration_minutes": 5
    },
    "supports": ["Anticipación visual", "Mediación verbal"],
    "result": "EXITOSO",
    "observations": "Todos se incorporaron sin dificultades"
  }'
```

**Respuesta esperada:**
```json
{
  "id": "uuid-del-evento-1",
  "classroom_id": "uuid-del-aula",
  "event_type": "TRANSICION",
  "description": "Transición de juego libre a asamblea matutina",
  ...
}
```

**⚠️ IMPORTANTE:** 
- Copia el `id` del evento
- Espera 10-30 segundos para que se generen los embeddings (primera vez descarga modelos)

---

## Paso 3: Crear evento 2 (similar al evento 1)

```bash
curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "classroom_id": "TU-UUID-DEL-AULA-AQUI",
    "event_type": "TRANSICION",
    "description": "Cambio de actividad de trabajo individual a reunión grupal",
    "context": {
      "moment_of_day": "mañana",
      "day_of_week": "martes",
      "duration_minutes": 3
    },
    "supports": ["Adaptación del entorno", "Mediación verbal"],
    "result": "EXITOSO",
    "observations": "El grupo se adaptó bien al cambio"
  }'
```

**⚠️ IMPORTANTE:** Copia el `id` del evento 2.

---

## Paso 4: Crear evento 3 (diferente tipo)

```bash
curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "classroom_id": "TU-UUID-DEL-AULA-AQUI",
    "event_type": "APRENDIZAJE",
    "description": "Actividad de trabajo en mesa individual",
    "context": {
      "moment_of_day": "tarde",
      "day_of_week": "miercoles"
    },
    "supports": ["Adaptación del entorno"],
    "result": "PARCIAL"
  }'
```

**⚠️ IMPORTANTE:** Copia el `id` del evento 3.

---

## Paso 5: Actualizar evento 1 (PUT /events/{id})

```bash
curl -X PUT "http://localhost:8000/events/UUID-DEL-EVENTO-1" \
  -H "Content-Type: application/json" \
  -d '{
    "result": "PARCIAL",
    "observations": "Actualización: algunos estudiantes necesitaron apoyo adicional"
  }'
```

**Verificación:**
- ✅ Debe retornar el evento actualizado
- ✅ Los embeddings se regeneran automáticamente en background
- ⏱️ Espera unos segundos para que se regeneren

---

## Paso 6: Buscar eventos similares (GET /events/similar)

### 6.1. Buscar similares al evento 1 (debe encontrar el evento 2)

```bash
curl -X GET "http://localhost:8000/events/similar?event_id=UUID-DEL-EVENTO-1&classroom_id=UUID-DEL-AULA&top_k=5&model_type=quality" \
  -H "Content-Type: application/json"
```

**Respuesta esperada:**
```json
[
  {
    "event": {
      "id": "uuid-del-evento-2",
      "event_type": "TRANSICION",
      "description": "Cambio de actividad...",
      ...
    },
    "similarity_score": 0.85
  }
]
```

**Verificación:**
- ✅ Debe encontrar el evento 2 (similar porque ambos son TRANSICION)
- ✅ El score de similitud debe ser alto (>0.7)
- ✅ No debe incluir el evento 1 (es el evento de referencia)
- ✅ Puede incluir el evento 3 pero con score más bajo (diferente tipo)

### 6.2. Buscar con filtro por tipo de evento

```bash
curl -X GET "http://localhost:8000/events/similar?event_id=UUID-DEL-EVENTO-1&classroom_id=UUID-DEL-AULA&top_k=5&model_type=quality&event_type_filter=TRANSICION" \
  -H "Content-Type: application/json"
```

**Verificación:**
- ✅ Solo debe retornar eventos de tipo TRANSICION

### 6.3. Buscar con modelo rápido

```bash
curl -X GET "http://localhost:8000/events/similar?event_id=UUID-DEL-EVENTO-1&classroom_id=UUID-DEL-AULA&top_k=5&model_type=fast" \
  -H "Content-Type: application/json"
```

**Verificación:**
- ✅ Debe funcionar igual pero usando el modelo rápido
- ⚡ Debe ser más rápido que el modelo calidad

### 6.4. Buscar con umbral mínimo de similitud

```bash
curl -X GET "http://localhost:8000/events/similar?event_id=UUID-DEL-EVENTO-1&classroom_id=UUID-DEL-AULA&top_k=5&model_type=quality&min_similarity=0.75" \
  -H "Content-Type: application/json"
```

**Verificación:**
- ✅ Solo debe retornar eventos con similitud >= 0.75

---

## Paso 7: Eliminar evento (DELETE /events/{id})

```bash
curl -X DELETE "http://localhost:8000/events/UUID-DEL-EVENTO-3" \
  -H "Content-Type: application/json"
```

**Verificación:**
- ✅ Debe retornar 204 No Content
- ✅ Los embeddings se eliminan automáticamente en background
- ✅ Si intentas buscar eventos similares al evento eliminado, no debe aparecer

---

## Verificación completa del flujo

### Script completo (reemplaza los UUIDs):

```bash
# 1. Crear aula
CLASSROOM_ID=$(curl -s -X POST "http://localhost:8000/classrooms/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Aula Test", "type": "TEA"}' | jq -r '.id')

echo "Aula creada: $CLASSROOM_ID"

# 2. Crear evento 1
EVENT1_ID=$(curl -s -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d "{
    \"classroom_id\": \"$CLASSROOM_ID\",
    \"event_type\": \"TRANSICION\",
    \"description\": \"Transición de juego libre a asamblea\",
    \"context\": {\"moment_of_day\": \"mañana\", \"day_of_week\": \"lunes\"},
    \"supports\": [\"Anticipación visual\"],
    \"result\": \"EXITOSO\"
  }" | jq -r '.id')

echo "Evento 1 creado: $EVENT1_ID"
echo "Esperando 15 segundos para generación de embeddings..."
sleep 15

# 3. Crear evento 2 (similar)
EVENT2_ID=$(curl -s -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d "{
    \"classroom_id\": \"$CLASSROOM_ID\",
    \"event_type\": \"TRANSICION\",
    \"description\": \"Cambio de actividad a reunión grupal\",
    \"context\": {\"moment_of_day\": \"mañana\", \"day_of_week\": \"martes\"},
    \"supports\": [\"Mediación verbal\"],
    \"result\": \"EXITOSO\"
  }" | jq -r '.id')

echo "Evento 2 creado: $EVENT2_ID"
echo "Esperando 15 segundos para generación de embeddings..."
sleep 15

# 4. Buscar eventos similares
echo "Buscando eventos similares al evento 1..."
curl -s -X GET "http://localhost:8000/events/similar?event_id=$EVENT1_ID&classroom_id=$CLASSROOM_ID&top_k=5&model_type=quality" | jq

# 5. Actualizar evento 1
echo "Actualizando evento 1..."
curl -s -X PUT "http://localhost:8000/events/$EVENT1_ID" \
  -H "Content-Type: application/json" \
  -d '{"result": "PARCIAL"}' | jq

echo "Esperando 10 segundos para regeneración de embeddings..."
sleep 10

# 6. Buscar de nuevo
echo "Buscando eventos similares después de actualizar..."
curl -s -X GET "http://localhost:8000/events/similar?event_id=$EVENT1_ID&classroom_id=$CLASSROOM_ID&top_k=5&model_type=quality" | jq

# 7. Eliminar evento 2
echo "Eliminando evento 2..."
curl -s -X DELETE "http://localhost:8000/events/$EVENT2_ID"

echo "✅ Flujo completo probado"
```

---

## Notas importantes

1. **Primera vez:** La primera generación de embeddings puede tardar 30-60 segundos porque descarga los modelos de sentence-transformers.

2. **Background tasks:** Los embeddings se generan en background, así que la API responde rápido pero los embeddings pueden tardar unos segundos.

3. **Verificar embeddings:** Puedes verificar que los embeddings se generaron correctamente revisando el directorio `./chroma_db/` (debe tener archivos de ChromaDB).

4. **Errores:** Si hay errores en la generación de embeddings, se registran en la consola del servidor pero no afectan la respuesta HTTP.

5. **Modelos:** 
   - `fast`: Más rápido, menos preciso (512 dimensiones)
   - `quality`: Más lento, más preciso (768 dimensiones)

---

## Troubleshooting

### Error: "Embedding service not available"
- Instala dependencias: `pip install sentence-transformers chromadb numpy<2.0`

### Error: "Event not found"
- Verifica que el UUID del evento sea correcto
- Asegúrate de que el evento pertenezca al aula especificada

### No encuentra eventos similares
- Espera más tiempo para que se generen los embeddings (primera vez puede tardar)
- Verifica que hay al menos 2 eventos en el aula
- Reduce el `min_similarity` si es muy alto

### Embeddings no se regeneran al actualizar
- Los embeddings se regeneran solo si cambias campos relevantes (description, event_type, supports, result, observations, context)
- Verifica en la consola del servidor si hay errores


