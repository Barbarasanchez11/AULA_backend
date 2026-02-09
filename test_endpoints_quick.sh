#!/bin/bash

# Script rápido para probar endpoints de eventos con embeddings
# Uso: ./test_endpoints_quick.sh

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "TEST RÁPIDO DE ENDPOINTS CON EMBEDDINGS"
echo "=========================================="
echo ""

# 1. Crear aula
echo "1. Creando aula..."
CLASSROOM_RESPONSE=$(curl -s -X POST "$BASE_URL/classrooms/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Aula Test Embeddings", "type": "TEA"}')

CLASSROOM_ID=$(echo $CLASSROOM_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$CLASSROOM_ID" ]; then
  echo "❌ Error creando aula"
  echo "Respuesta: $CLASSROOM_RESPONSE"
  exit 1
fi

echo "✅ Aula creada: $CLASSROOM_ID"
echo ""

# 2. Crear evento 1
echo "2. Creando evento 1..."
EVENT1_RESPONSE=$(curl -s -X POST "$BASE_URL/events/" \
  -H "Content-Type: application/json" \
  -d "{
    \"classroom_id\": \"$CLASSROOM_ID\",
    \"event_type\": \"TRANSICION\",
    \"description\": \"Transición de juego libre a asamblea matutina\",
    \"context\": {
      \"moment_of_day\": \"mañana\",
      \"day_of_week\": \"lunes\",
      \"duration_minutes\": 5
    },
    \"supports\": [\"Anticipación visual\", \"Mediación verbal\"],
    \"result\": \"EXITOSO\",
    \"observations\": \"Todos se incorporaron sin dificultades\"
  }")

EVENT1_ID=$(echo $EVENT1_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$EVENT1_ID" ]; then
  echo "❌ Error creando evento 1"
  echo "Respuesta: $EVENT1_RESPONSE"
  exit 1
fi

echo "✅ Evento 1 creado: $EVENT1_ID"
echo "⏳ Esperando 20 segundos para generación de embeddings..."
sleep 20
echo ""

# 3. Crear evento 2 (similar)
echo "3. Creando evento 2 (similar al evento 1)..."
EVENT2_RESPONSE=$(curl -s -X POST "$BASE_URL/events/" \
  -H "Content-Type: application/json" \
  -d "{
    \"classroom_id\": \"$CLASSROOM_ID\",
    \"event_type\": \"TRANSICION\",
    \"description\": \"Cambio de actividad de trabajo individual a reunión grupal\",
    \"context\": {
      \"moment_of_day\": \"mañana\",
      \"day_of_week\": \"martes\"
    },
    \"supports\": [\"Adaptación del entorno\", \"Mediación verbal\"],
    \"result\": \"EXITOSO\",
    \"observations\": \"El grupo se adaptó bien\"
  }")

EVENT2_ID=$(echo $EVENT2_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$EVENT2_ID" ]; then
  echo "❌ Error creando evento 2"
  echo "Respuesta: $EVENT2_RESPONSE"
  exit 1
fi

echo "✅ Evento 2 creado: $EVENT2_ID"
echo "⏳ Esperando 20 segundos para generación de embeddings..."
sleep 20
echo ""

# 4. Buscar eventos similares
echo "4. Buscando eventos similares al evento 1..."
SIMILAR_RESPONSE=$(curl -s -X GET "$BASE_URL/events/similar?event_id=$EVENT1_ID&classroom_id=$CLASSROOM_ID&top_k=5&model_type=quality")

echo "$SIMILAR_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SIMILAR_RESPONSE"
echo ""

# 5. Verificar en BD (usando docker exec)
echo "5. Verificando en base de datos..."
EVENT_COUNT=$(docker exec aula_plus_db psql -U aulaplus -d aulaplus_db -t -c "SELECT COUNT(*) FROM events WHERE classroom_id = '$CLASSROOM_ID';" 2>/dev/null | tr -d ' ')

if [ ! -z "$EVENT_COUNT" ]; then
  echo "✅ Eventos en BD: $EVENT_COUNT"
else
  echo "⚠️  No se pudo verificar en BD (puede ser normal si hay problemas de conexión)"
fi

echo ""
echo "=========================================="
echo "TEST COMPLETADO"
echo "=========================================="
echo ""
echo "IDs generados:"
echo "  - Aula: $CLASSROOM_ID"
echo "  - Evento 1: $EVENT1_ID"
echo "  - Evento 2: $EVENT2_ID"
echo ""
echo "Puedes verificar en Adminer: http://localhost:8081"
echo "  - Sistema: PostgreSQL"
echo "  - Servidor: postgres"
echo "  - Usuario: aulaplus"
echo "  - Contraseña: dev_password_2024"
echo "  - Base de datos: aulaplus_db"

