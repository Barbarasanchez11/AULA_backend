# Guía de Testing - Script de Importación CSV

Esta guía te ayuda a probar el script de importación de eventos desde CSV.

## Prerequisitos

1. **Base de datos funcionando**:
   ```bash
   # Verificar que PostgreSQL está corriendo
   docker-compose ps
   ```

2. **Entorno virtual activado**:
   ```bash
   source venv/bin/activate
   ```

3. **Aula creada**:
   - Necesitas tener al menos un aula creada en la base de datos
   - Obtén el `classroom_id` con:
     ```bash
     curl -X 'GET' 'http://127.0.0.1:8000/classrooms/' -H 'accept: application/json'
     ```

## Paso 1: Preparar CSV de Prueba

### Opción A: Usar el CSV de ejemplo

El archivo `example_events.csv` ya está preparado con eventos de ejemplo.

**Importante**: Asegúrate de que el `classroom_id` en el CSV existe en tu base de datos.

### Opción B: Crear tu propio CSV

Crea un archivo CSV con el siguiente formato:

```csv
classroom_id,event_type,description,moment_of_day,day_of_week,duration_minutes,supports,additional_supports,result,observations
TU_CLASSROOM_ID,TRANSICION,Transición de juego libre a asamblea,mañana,lunes,5,Anticipación visual,,EXITOSO,Todos se incorporaron sin dificultades
```

**Campos requeridos**:
- `classroom_id`: UUID del aula (debe existir)
- `event_type`: TRANSICION, CAMBIO_DE_RUTINA, APRENDIZAJE, o REGULACION
- `description`: Mínimo 10 caracteres
- `moment_of_day`: mañana, mediodia, o tarde
- `supports`: Al menos uno, separado por `;` o `,`
- `result`: EXITOSO, PARCIAL, o DIFICULTAD

**Campos opcionales**:
- `day_of_week`: lunes, martes, miercoles, jueves, viernes, sabado, domingo
- `duration_minutes`: Número entero
- `additional_supports`: Texto libre
- `observations`: Texto libre

## Paso 2: Ejecutar el Script

### Método 1: Directamente con Python

```bash
python3 scripts/import_events_from_csv.py scripts/example_events.csv
```

### Método 2: Con el script de ayuda

```bash
./scripts/test_import.sh scripts/example_events.csv
```

## Paso 3: Verificar Resultados

### 3.1 Verificar en la Base de Datos

```bash
# Listar eventos importados
curl -X 'GET' \
  'http://127.0.0.1:8000/events/?classroom_id=TU_CLASSROOM_ID' \
  -H 'accept: application/json' | python3 -m json.tool
```

### 3.2 Verificar Embeddings Generados

Los embeddings se generan automáticamente. Puedes verificar buscando eventos similares:

```bash
# Obtener un event_id de los eventos importados
EVENT_ID="evento_id_aqui"

# Buscar eventos similares
curl -X 'GET' \
  "http://127.0.0.1:8000/events/similar?event_id=${EVENT_ID}&classroom_id=TU_CLASSROOM_ID" \
  -H 'accept: application/json' | python3 -m json.tool
```

### 3.3 Verificar Análisis de Patrones

```bash
# Analizar patrones
curl -X 'GET' \
  'http://127.0.0.1:8000/events/patterns?classroom_id=TU_CLASSROOM_ID' \
  -H 'accept: application/json' | python3 -m json.tool
```

### 3.4 Generar Recomendaciones

```bash
# Generar recomendaciones desde patrones
curl -X 'POST' \
  'http://127.0.0.1:8000/recommendations/generate?classroom_id=TU_CLASSROOM_ID' \
  -H 'accept: application/json' | python3 -m json.tool
```

## Casos de Prueba

### Caso 1: Importación Exitosa

**CSV válido sin PII**:
- ✅ Debe importar todos los eventos
- ✅ Debe generar embeddings
- ✅ Debe normalizar textos

### Caso 2: Rechazo por PII

**CSV con datos personales**:
```csv
classroom_id,description,...
TU_ID,María con DNI 12345678A tuvo dificultades,...
```

- ❌ Debe rechazar el evento
- ❌ Debe mostrar mensaje de error claro
- ✅ Debe continuar con otros eventos (si `--skip-errors`)

### Caso 3: Validación de Esquema

**CSV con datos inválidos**:
- Tipo de evento inválido
- Descripción muy corta
- Apoyos inválidos

- ❌ Debe rechazar eventos inválidos
- ✅ Debe mostrar mensaje de error específico

### Caso 4: Aula No Existente

**CSV con classroom_id que no existe**:
- ❌ Debe rechazar el evento
- ✅ Debe mostrar error: "Classroom not found"

## Verificación de Normalización

Los textos se normalizan automáticamente:

**Antes**:
```
"Transición   de   juego"
```

**Después**:
```
"Transición de juego"
```

## Verificación de PII

El sistema detecta y rechaza:
- ✅ Nombres propios (María, Juan, etc.)
- ✅ DNI/NIE (12345678A, X1234567L)
- ✅ Teléfonos (612345678, +34 912345678)
- ✅ Emails (juan@example.com)
- ✅ Direcciones (Calle Mayor 15)
- ✅ Fechas de nacimiento (15/03/2010, Nacido el...)

## Troubleshooting

### Error: "chromadb no está instalado"
```bash
pip install chromadb
```

### Error: "Classroom not found"
- Verifica que el `classroom_id` existe
- Crea un aula primero con `POST /classrooms/`

### Error: "PII detected"
- Revisa el texto del evento
- Elimina nombres, DNI, teléfonos, etc.
- Usa descripciones genéricas

### Error: "Invalid supports"
- Verifica que los apoyos son exactamente:
  - `Anticipación visual`
  - `Adaptación del entorno`
  - `Mediación verbal`
  - `Pausa sensorial`
  - `Apoyo individual del adulto`

## Resultado Esperado

Después de una importación exitosa:

1. ✅ Eventos guardados en PostgreSQL
2. ✅ Embeddings generados y guardados en ChromaDB
3. ✅ Puedes buscar eventos similares
4. ✅ Puedes analizar patrones
5. ✅ Puedes generar recomendaciones

---

**Nota**: Si encuentras algún error, revisa los mensajes del script. Cada error incluye información sobre qué falló y en qué fila del CSV.




