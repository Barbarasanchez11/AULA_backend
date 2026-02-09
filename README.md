# AULA+ — Sistema de Apoyo Pedagógico para Aulas TEA

## Descripción

AULA+ es un sistema backend de apoyo para docentes en aulas de alumnado con Trastorno del Espectro Autista (TEA). Su objetivo es registrar eventos pedagógicos anonimizados, analizar patrones históricos del aula y ofrecer recomendaciones pedagógicas bajo demanda, respetando estrictamente la privacidad y protección de datos de los menores.

**Principios fundamentales:**
- NO recopila datos personales de menores
- NO usa biometría (cámaras, audio, sensores)
- NO diagnostica ni evalúa clínicamente
- Cada aula es una unidad independiente (aislamiento de datos)
- El control humano es siempre prioritario

## Funcionalidades Principales

### Registro de Eventos Pedagógicos

El sistema registra eventos anonimizados del aula en cuatro categorías:

1. **TRANSICIÓN**: Cambios entre actividades, espacios o estados
   - Ejemplo: "Transición de juego libre a asamblea", "Transición de aula a patio"

2. **CAMBIO_DE_RUTINA**: Modificaciones a rutinas establecidas
   - Ejemplo: "Cambio de horario de recreo", "Actividad nueva no prevista"

3. **APRENDIZAJE**: Actividades pedagógicas estructuradas
   - Ejemplo: "Trabajo en mesa individual", "Actividad grupal"

4. **REGULACIÓN**: Situaciones relacionadas con estados emocionales o conductuales observables
   - Ejemplo: "Momento de calma", "Necesidad de espacio"

**Estructura de un evento:**
- Tipo de evento (obligatorio)
- Descripción breve y objetiva (obligatorio)
- Contexto: momento del día (mañana/mediodía/tarde), día de la semana (opcional)
- Apoyos utilizados: lista predefinida (obligatorio) + texto libre opcional
- Resultado: EXITOSO | PARCIAL | DIFICULTAD
- Observaciones: texto libre opcional

**Lista predefinida de apoyos:**
- Anticipación visual
- Adaptación del entorno
- Mediación verbal
- Pausa sensorial
- Apoyo individual del adulto

### Generación de Recomendaciones

**Modo principal: bajo demanda del docente**
- El docente solicita recomendaciones cuando las necesita
- El sistema no interrumpe ni lanza alertas automáticas
- Las recomendaciones se basan en patrones históricos del aula

**Excepción controlada:**
- Si se registra un evento planificado (ej. salida, cambio de rutina), el sistema puede sugerir orientaciones generales automáticamente
- Siempre visibles como "propuestas", nunca como acciones automáticas

**Estructura de una recomendación:**
- Tipo: ANTICIPACIÓN | ESTRATEGIA | ADAPTACIÓN
- Título: descriptivo y accionable
- Descripción: explicación clara de la recomendación
- Contexto aplicable: cuándo/cómo aplicar
- Patrón detectado: breve explicación del patrón histórico que la sustenta
- Confianza: ALTA | MEDIA | BAJA (basada en frecuencia del patrón)
- Fecha de generación

**Validación humana progresiva:**
- Nivel 1 (inicio): recomendaciones basadas en patrones observados y literatura pedagógica general
- Nivel 2 (escalable): feedback del docente ("útil / no útil") y selección de recomendaciones aplicadas
- Nivel 3 (futuro): curaduría por expertos pedagógicos
- **Importante:** Nunca se afirma que una recomendación es "correcta", solo "coherente con experiencias previas del aula"

### Acceso Familiar

**Solo a través del docente:**
- Las familias NO acceden directamente al sistema
- El docente genera resúmenes interpretados para las familias

**Qué ven las familias:**
- Resúmenes semanales interpretados: "Esta semana se trabajó la anticipación de cambios"
- Orientaciones generales para casa, no informes de conducta

**Qué NO ven:**
- Eventos en bruto
- Análisis del aula
- Recomendaciones internas del sistema

## Qué NO Hace el Sistema

**Límites explícitos y claros:**

- ❌ NO recopila datos personales de menores (nombres, DNI, fotos, etc.)
- ❌ NO usa biometría (cámaras, audio, sensores, reconocimiento facial)
- ❌ NO diagnostica ni evalúa clínicamente
- ❌ NO genera informes clínicos ni psicológicos
- ❌ NO identifica ni etiqueta a estudiantes individuales
- ❌ NO toma decisiones automáticas que afecten a personas
- ❌ NO comparte datos entre aulas (cada aula es independiente)
- ❌ NO almacena información que permita identificar a menores
- ❌ NO predice comportamientos individuales
- ❌ NO reemplaza la evaluación profesional ni la intervención especializada
- ❌ NO genera alertas automáticas a familias o administración
- ❌ NO usa datos para entrenar modelos externos o comerciales
- ❌ NO sustituye decisiones pedagógicas del docente

## Arquitectura Técnica

### Stack Tecnológico

- **Backend**: Python 3.11 + FastAPI
- **Base de datos relacional**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 (async)
- **Validación de datos**: Pydantic v2
- **Orquestación IA**: LangGraph (futuro)
- **Embeddings semánticos**: Para análisis de similitud entre eventos (futuro)
- **Vector DB**: FAISS o Chroma (para búsqueda semántica de patrones) (futuro)
- **Despliegue**: Contenedores Docker, escalable por aula
- **Visor de BD**: Adminer (puerto 8080)

### Estructura del Proyecto

```
AULA_backend/
├── app/
│   ├── main.py                 # Aplicación FastAPI principal
│   ├── config.py               # Configuración (settings)
│   ├── models/
│   │   ├── database.py         # Configuración BD y sesiones
│   │   ├── models.py           # Modelos SQLAlchemy (Classroom, Event, Recommendation)
│   │   └── init_db.py          # Script de inicialización de BD
│   ├── routers/
│   │   ├── classrooms.py       # Endpoints de gestión de aulas
│   │   ├── events.py           # Endpoints de gestión de eventos
│   │   └── recommendations.py  # Endpoints de gestión de recomendaciones
│   ├── schemas/
│   │   ├── enums.py            # Enumeraciones (EventType, Result, etc.)
│   │   ├── classroom.py        # Schemas Pydantic de aulas
│   │   ├── event.py            # Schemas Pydantic de eventos
│   │   └── recommendation.py   # Schemas Pydantic de recomendaciones
│   └── services/              # Lógica de negocio (futuro)
├── docs/
│   └── database_structure.md   # Documentación de estructura de BD
├── docker-compose.yml          # Configuración Docker (PostgreSQL + Adminer)
└── requirements.txt           # Dependencias Python
```

### Flujo de Funcionamiento

```
1. REGISTRO DE EVENTO
   └─> Docente registra evento anonimizado vía POST /events/
   └─> FastAPI valida datos con Pydantic (schemas)
   └─> Router valida que el classroom_id existe
   └─> Se crea objeto Event (SQLAlchemy)
   └─> Se almacena en PostgreSQL
   └─> Se devuelve EventResponse (JSON)

2. PROCESAMIENTO PERIÓDICO (ej: diario/nocturno) [FUTURO]
   └─> Sistema analiza eventos históricos del aula
   └─> Genera embeddings semánticos de eventos similares
   └─> Identifica patrones recurrentes (clustering)
   └─> Detecta correlaciones temporales (día/hora)
   └─> Analiza efectividad de apoyos utilizados

3. GENERACIÓN DE RECOMENDACIONES [FUTURO]
   └─> Basado en patrones detectados
   └─> Considera contexto temporal y situacional
   └─> Prioriza recomendaciones con mayor evidencia histórica
   └─> Almacena recomendaciones generadas en PostgreSQL

4. CONSULTA POR DOCENTE
   └─> Docente solicita recomendaciones vía GET /recommendations/?classroom_id={id}
   └─> Sistema consulta PostgreSQL
   └─> Devuelve lista de recomendaciones ordenadas por relevancia
   └─> Docente puede consultar detalles vía GET /recommendations/{id}

5. RETROALIMENTACIÓN (opcional, futuro)
   └─> Docente puede marcar recomendaciones como útiles/no útiles
   └─> Sistema ajusta priorización (sin modificar recomendaciones existentes)
```

### Diagrama de Arquitectura Actual

```
┌─────────────────┐
│   Docente       │
│   (API Client)  │
│   Swagger UI    │
└────────┬────────┘
         │
         │ HTTP/REST (FastAPI)
         │
┌────────▼─────────────────────────────────────┐
│         Backend FastAPI                      │
│  ┌──────────────────────────────────────┐   │
│  │  Routers (app/routers/):              │   │
│  │  - /classrooms (5 endpoints)          │   │
│  │  - /events (5 endpoints)              │   │
│  │  - /recommendations (3 endpoints)     │   │
│  └──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────┐   │
│  │  Schemas (app/schemas/):              │   │
│  │  - Validación Pydantic                │   │
│  │  - Conversión modelo ↔ schema         │   │
│  └──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────┐   │
│  │  Models (app/models/):                │   │
│  │  - SQLAlchemy ORM                     │   │
│  │  - Relaciones y constraints           │   │
│  └──────────────────────────────────────┘   │
└────────┬─────────────────────────────────────┘
         │
         ├──────────────────┬──────────────────┐
         │                  │                  │
┌────────▼────────┐  ┌──────▼──────┐  ┌───────▼──────┐
│  PostgreSQL     │  │  Vector DB  │  │  LangGraph   │
│  (Eventos,      │  │  (FAISS/    │  │  (Orquestación│
│   Aulas,        │  │   Chroma)   │  │   IA)        │
│   Recomend.)    │  │   [FUTURO]  │  │   [FUTURO]   │
└─────────────────┘  └─────────────┘  └──────────────┘
```

### Diagrama de Flujo de Datos

```
┌──────────────┐
│   Cliente    │
│  (HTTP/JSON) │
└──────┬───────┘
       │
       │ 1. Request HTTP
       ▼
┌─────────────────────────────────┐
│      FastAPI Router             │
│  (app/routers/*.py)             │
│  - Valida ruta y método         │
│  - Extrae parámetros            │
└──────┬──────────────────────────┘
       │
       │ 2. Valida con Pydantic
       ▼
┌─────────────────────────────────┐
│   Pydantic Schema               │
│  (app/schemas/*.py)             │
│  - Valida tipos                  │
│  - Valida enums                  │
│  - Valida longitudes             │
└──────┬──────────────────────────┘
       │
       │ 3. Si válido → Continúa
       │    Si inválido → 422 Error
       ▼
┌─────────────────────────────────┐
│   SQLAlchemy Model              │
│  (app/models/models.py)         │
│  - Crea/lee/actualiza/elimina    │
│  - Maneja relaciones             │
└──────┬──────────────────────────┘
       │
       │ 4. Query SQL
       ▼
┌─────────────────────────────────┐
│      PostgreSQL                  │
│  - Almacena datos                │
│  - Mantiene integridad           │
└──────┬──────────────────────────┘
       │
       │ 5. Resultado
       ▼
┌─────────────────────────────────┐
│   Conversión a Schema            │
│  - Model → Pydantic Schema      │
│  - Enums, fechas, etc.          │
└──────┬──────────────────────────┘
       │
       │ 6. Response JSON
       ▼
┌──────────────┐
│   Cliente    │
│  (HTTP/JSON) │
└──────────────┘
```

### API Endpoints Implementados

#### Classrooms (`/classrooms`)

| Método | Ruta | Descripción | Status Code |
|--------|------|-------------|-------------|
| `GET` | `/classrooms/` | Lista todas las aulas del sistema | 200 |
| `GET` | `/classrooms/{id}` | Obtiene un aula específica por ID | 200 / 404 |
| `POST` | `/classrooms/` | Crea una nueva aula | 201 / 422 |
| `PUT` | `/classrooms/{id}` | Actualiza un aula (campos opcionales) | 200 / 404 |
| `DELETE` | `/classrooms/{id}` | Elimina un aula y sus eventos/recomendaciones | 204 / 404 |

**Ejemplo de uso:**
```bash
# Crear aula
POST /classrooms/
{
  "name": "Aula TEA 1",
  "type": "TEA"
}

# Listar todas las aulas
GET /classrooms/

# Obtener aula específica
GET /classrooms/{uuid}
```

#### Events (`/events`)

| Método | Ruta | Descripción | Status Code |
|--------|------|-------------|-------------|
| `GET` | `/events/?classroom_id={id}` | Lista eventos de un aula específica | 200 / 404 |
| `GET` | `/events/{id}` | Obtiene un evento específico por ID | 200 / 404 |
| `POST` | `/events/` | Crea un nuevo evento pedagógico | 201 / 422 / 404 |
| `PUT` | `/events/{id}` | Actualiza un evento (campos opcionales) | 200 / 404 |
| `DELETE` | `/events/{id}` | Elimina un evento | 204 / 404 |

**Ejemplo de uso:**
```bash
# Crear evento
POST /events/
{
  "classroom_id": "uuid-del-aula",
  "event_type": "TRANSICION",
  "description": "Transición de juego libre a asamblea",
  "context": {
    "moment_of_day": "mañana",
    "day_of_week": "lunes",
    "duration_minutes": 5
  },
  "supports": ["Anticipación visual", "Mediación verbal"],
  "result": "EXITOSO"
}

# Listar eventos de un aula
GET /events/?classroom_id={uuid}

# Actualizar solo el resultado
PUT /events/{uuid}
{
  "result": "PARCIAL"
}
```

#### Recommendations (`/recommendations`)

| Método | Ruta | Descripción | Status Code |
|--------|------|-------------|-------------|
| `GET` | `/recommendations/?classroom_id={id}` | Lista recomendaciones de un aula | 200 / 404 |
| `GET` | `/recommendations/{id}` | Obtiene una recomendación específica por ID | 200 / 404 |
| `POST` | `/recommendations/` | Crea una recomendación (útil para testing) | 201 / 422 / 404 |

**Nota:** En producción, las recomendaciones se generan automáticamente. El POST es útil para desarrollo y testing.

**Ejemplo de uso:**
```bash
# Listar recomendaciones de un aula
GET /recommendations/?classroom_id={uuid}

# Obtener recomendación específica
GET /recommendations/{uuid}
```

### Principios de Diseño Aplicados

#### SOLID
- **Single Responsibility**: Cada router maneja un solo recurso
- **Open/Closed**: Fácil añadir nuevos endpoints sin modificar existentes
- **Dependency Inversion**: Dependemos de abstracciones (schemas, models)

#### KISS (Keep It Simple, Stupid)
- Un archivo por recurso
- Lógica clara y directa
- Sin complejidad innecesaria

#### Separación de Responsabilidades
- **Routers**: Manejan HTTP, validan entrada, llaman a servicios
- **Schemas**: Validan y estructuran datos
- **Models**: Acceso a base de datos
- **Services**: Lógica de negocio (futuro)

### Validación y Manejo de Errores

#### Validación Automática (Pydantic)
- Tipos de datos (string, int, UUID, enum)
- Longitudes mínimas/máximas
- Valores obligatorios vs opcionales
- Enums con valores permitidos
- **Código de error**: 422 Unprocessable Entity

#### Errores Personalizados
- **404 Not Found**: Recurso no existe (aula, evento, recomendación)
- **422 Validation Error**: Datos inválidos (Pydantic)
- **500 Internal Server Error**: Error del servidor (capturado automáticamente)

### Acceso a Base de Datos

#### Dependency Injection
```python
async def endpoint(db: AsyncSession = Depends(get_db)):
    # db es la sesión de base de datos
    # Se cierra automáticamente al terminar
```

#### Transacciones
- Cada request tiene su propia sesión
- `commit()` guarda cambios
- `refresh()` recarga objeto desde BD
- Rollback automático en caso de error

### Documentación Automática

FastAPI genera automáticamente:
- **Swagger UI**: `http://localhost:8000/docs` (interactivo)
- **ReDoc**: `http://localhost:8000/redoc` (documentación alternativa)
- Incluye todos los endpoints, schemas, y ejemplos

## Protección de Datos y Privacidad

- **Anonimización completa**: Todos los eventos son anonimizados desde el registro
- **Aislamiento por aula**: Cada aula es una unidad independiente, sin compartición de datos
- **Minimización de datos**: Solo se recopila lo estrictamente necesario para el análisis de patrones
- **Control docente**: El docente tiene control total sobre qué eventos registrar y qué recomendaciones consultar
- **Cumplimiento RGPD**: Transparencia, minimización, limitación de propósito y control humano

## Uso en el Aula

1. El docente registra eventos pedagógicos anonimizados cuando ocurren o se planifican
2. El sistema procesa eventos históricos periódicamente para identificar patrones (futuro)
3. El docente solicita recomendaciones bajo demanda cuando las necesita
4. El docente aplica las recomendaciones que considere apropiadas
5. El docente puede generar resúmenes interpretados para las familias
6. Los patrones se acumulan y ajustan gradualmente, manteniendo historial del aula sin identificar alumnos

## Inicio Rápido

### Requisitos Previos

- Python 3.11+
- Docker y Docker Compose
- Git

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd AULA_backend
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   Crear archivo `.env`:
   ```env
   POSTGRES_USER=aulaplus
   POSTGRES_PASSWORD=dev_password_2024
   POSTGRES_DB=aulaplus_db
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```

5. **Levantar servicios con Docker**
   ```bash
   docker-compose up -d
   ```

6. **Inicializar base de datos**
   ```bash
   python -m app.models.init_db
   ```

7. **Iniciar servidor FastAPI**
   ```bash
   uvicorn app.main:app --reload
   ```

### Acceso a la API

- **API Base**: `http://localhost:8000`
- **Documentación Swagger**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Adminer (BD)**: `http://localhost:8080`

### Probar los Endpoints

#### Opción 1: Swagger UI (Recomendado)

1. Abre `http://localhost:8000/docs` en tu navegador
2. Expande cualquier endpoint
3. Haz clic en "Try it out"
4. Rellena los datos necesarios
5. Haz clic en "Execute"
6. Verás la respuesta

#### Opción 2: curl

```bash
# Listar aulas
curl http://localhost:8000/classrooms/

# Crear aula
curl -X POST http://localhost:8000/classrooms/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Aula TEA 1", "type": "TEA"}'

# Listar eventos de un aula
curl "http://localhost:8000/events/?classroom_id=UUID_AQUI"
```

### Flujo de Prueba Completo

1. **Crear un aula**
   ```bash
   POST /classrooms/
   {
     "name": "Aula TEA 1",
     "type": "TEA"
   }
   ```
   Copia el `id` de la respuesta.

2. **Crear un evento**
   ```bash
   POST /events/
   {
     "classroom_id": "id-del-paso-1",
     "event_type": "TRANSICION",
     "description": "Transición de juego libre a asamblea matutina",
     "context": {
       "moment_of_day": "mañana",
       "day_of_week": "lunes",
       "duration_minutes": 5
     },
     "supports": ["Anticipación visual"],
     "result": "EXITOSO"
   }
   ```

3. **Listar eventos del aula**
   ```bash
   GET /events/?classroom_id=id-del-paso-1
   ```

4. **Crear una recomendación**
   ```bash
   POST /recommendations/
   {
     "classroom_id": "id-del-paso-1",
     "recommendation_type": "ANTICIPACION",
     "title": "Anticipar cambios de rutina",
     "description": "Recomendación basada en patrones observados...",
     "applicable_context": "Aplicar en cambios de rutina",
     "detected_pattern": "Patrón detectado en eventos similares",
     "confidence": "ALTA"
   }
   ```

5. **Listar recomendaciones**
   ```bash
   GET /recommendations/?classroom_id=id-del-paso-1
   ```

## Beneficios Sociales

- Mejora la calidad educativa de aulas TEA y su integración
- Facilita decisiones pedagógicas basadas en datos, respetando autonomía docente
- Proporciona información útil a familias sin comprometer la privacidad
- Escalable: de un piloto a cientos de aulas, manteniendo costes controlados
- Cada aula aprende de su propia experiencia histórica

## Roadmap y Estado del Proyecto

### ✅ Fase 1: Fundamentos (COMPLETADA)
- ✅ Estructura de base de datos (PostgreSQL)
- ✅ Backend FastAPI con 13 endpoints funcionales
- ✅ Modelos de datos (Classroom, Event, Recommendation)
- ✅ Validación de esquemas Pydantic
- ✅ Relaciones entre tablas configuradas
- ✅ Adminer configurado para visualización de BD
- ✅ Documentación de estructura de BD

**Endpoints implementados:**
- 5 endpoints de Classrooms (CRUD completo)
- 6 endpoints de Events (CRUD completo + similar + patterns)
- 4 endpoints de Recommendations (GET list, GET by ID, POST, POST generate)

### ✅ Fase 2: Base IA (COMPLETADA)
- ✅ Sistema de embeddings híbrido (distiluse + mpnet)
- ✅ Vector DB con ChromaDB (persistente, por aula)
- ✅ Búsqueda semántica de eventos similares
- ✅ Integración automática con eventos (background tasks)
- ✅ Endpoint: `GET /events/similar`

**Archivos:**
- `app/services/embeddingService.py`: Servicio de embeddings híbrido
- `app/services/vector_store.py`: Gestión de ChromaDB
- Documentación: `docs/embeddings_implementation.md`

### ✅ Fase 3: Análisis de Patrones y Recomendaciones (COMPLETADA - Sin LangGraph)
- ✅ Análisis de patrones (clustering, temporal, efectividad)
- ✅ Generación automática de recomendaciones desde patrones
- ✅ Sistema de confianza (ALTA/MEDIA/BAJA)
- ✅ Explicabilidad de patrones detectados

**Endpoints implementados:**
- `GET /events/patterns`: Analiza patrones en eventos
- `POST /recommendations/generate`: Genera recomendaciones automáticamente

**Archivos:**
- `app/services/pattern_analysis.py`: Análisis de patrones
- `app/services/recommendation_generator.py`: Generación de recomendaciones
- Documentación: `docs/phase3_pattern_analysis.md`

### ⏳ Fase 3.5: Integración con LangGraph (PENDIENTE)
- ⏳ Orquestación de agentes de IA
- ⏳ Generación de texto más natural con LLMs
- ⏳ Flujo completo automatizado
- ⏳ Validación humana progresiva

### ⏳ Fase 4: Validación y Despliegue (PENDIENTE)
- ⏳ Sistema de feedback del docente
- ⏳ Optimización de contenedores Docker
- ⏳ Despliegue en nube
- ⏳ Prueba piloto con datos reales (anonimizados)

## Limitaciones Actuales

- No diagnostica ni sustituye decisiones pedagógicas
- No usa sensores biométricos ni identifica alumnos individuales
- Requiere supervisión humana constante para validar recomendaciones
- Las recomendaciones son sugerencias, no prescripciones
- El sistema aprende de patrones históricos, no de literatura clínica

## Documentación

Documentación técnica detallada disponible en `docs/`:

- **[Arquitectura Técnica](docs/architecture.md)**: Estructura del sistema, tecnologías y decisiones de diseño
- **[Implementación de Embeddings](docs/embeddings_implementation.md)**: Sistema híbrido de embeddings, lazy loading y vector store
- **[Análisis de Patrones y Recomendaciones](docs/phase3_pattern_analysis.md)**: Servicios de análisis de patrones y generación de recomendaciones
- **[Flujo de IA](docs/ai_workflow.md)**: Flujo completo del sistema desde eventos hasta recomendaciones
- **[Protección de Datos](docs/privacy_and_data_protection.md)**: Medidas de privacidad y cumplimiento RGPD
- **[Requisitos de Ciberseguridad](docs/cybersecurity_requirements.md)**: Plan de ciberseguridad y PII scanner

## Contribuciones y Contacto

Este proyecto está en desarrollo activo. Para contribuciones o consultas, contactar con el equipo de desarrollo.

---

**Nota importante**: Este sistema está diseñado como herramienta de apoyo pedagógico, no como sistema de diagnóstico o evaluación clínica. Todas las decisiones finales recaen en el profesional docente.
