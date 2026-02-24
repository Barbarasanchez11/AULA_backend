# AULA+ Backend

> **Capa de inteligencia pedagógica para aulas TEA**  
> Sistema de agentes IA que detecta patrones del entorno educativo y genera recomendaciones preventivas — sin registrar datos personales de ningún alumno.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Salamandra](https://img.shields.io/badge/LLM-Salamandra--7b--instruct-orange.svg)](https://huggingface.co/BSC-LT/salamandra-7b-instruct)
[![ALIA](https://img.shields.io/badge/infraestructura-ALIA%20%2F%20BSC--CNS-blue.svg)](https://alia.gob.es)

---

## ¿Qué es AULA+?

AULA+ es el primer sistema de análisis pedagógico para aulas TEA (Trastorno del Espectro Autista) que analiza el **entorno educativo** en lugar del alumno individual.

En lugar de registrar conductas o generar perfiles de alumnos, AULA+ captura eventos pedagógicos del aula — transiciones, apoyos utilizados, tipos de actividad — y detecta los patrones contextuales que preceden a los momentos difíciles. El objetivo es pasar de un modelo reactivo (intervenir en la crisis) a uno preventivo (anticipar las condiciones que la producen).

El sistema se integra sobre plataformas educativas existentes como **Raíces** (Madrid) o **Séneca** (Andalucía) sin reemplazarlas. Es una capa de inteligencia pedagógica sobre la infraestructura ya invertida.

**El motor de lenguaje es [Salamandra-7b-instruct](https://huggingface.co/BSC-LT/salamandra-7b-instruct)**, desarrollado por el Barcelona Supercomputing Center (BSC-CNS) dentro de la iniciativa pública [ALIA](https://alia.gob.es) del Gobierno de España, verificado por AESIA. Los datos del alumnado nunca salen de soberanía europea.

---

## Principios de diseño

- **Privacidad por diseño** — el sistema es arquitectónicamente incapaz de almacenar datos personales de alumnos. No existe ningún campo de "nombre de alumno" en el modelo de datos. El `PIIValidator` bloquea automáticamente cualquier dato identificativo antes de persistirlo.
- **Human-in-the-loop** — el sistema propone. El docente decide siempre. Sin acciones automáticas, sin notificaciones sin validación explícita.
- **Explicabilidad** — cada recomendación incluye el patrón concreto que la sustenta. No hay caja negra.
- **Soberanía tecnológica europea** — stack completo sobre infraestructura pública: Salamandra/ALIA para LLM, sentence-transformers en local para embeddings, PostgreSQL y ChromaDB en servidores propios o de la Consejería.
- **Complementariedad** — no sustituye Raíces ni Séneca. Los amplía con la capa que les falta.

---

## Stack técnico

| Componente | Tecnología | Función |
|---|---|---|
| API REST | **FastAPI** + Python 3.11 | 13 endpoints con validación Pydantic v2, async |
| Base de datos relacional | **PostgreSQL 16** | Eventos, aulas, recomendaciones, logs de auditoría |
| ORM | **SQLAlchemy 2.0** | Acceso a datos async |
| Embeddings semánticos | **sentence-transformers** (mpnet + distiluse) | Vectorización de eventos en local — sin API externa |
| Base de datos vectorial | **ChromaDB** (persistente) | Búsqueda semántica por aula, instancia independiente por aula |
| Detección de patrones | **scikit-learn — DBSCAN** | Clustering semántico + análisis temporal + efectividad de apoyos |
| Sistema de agentes | **LangGraph** (4 nodos) | Orchestración: Receive → Search → LLM → Validate |
| Modelo de lenguaje | **Salamandra-7b-instruct** (BSC-CNS/ALIA) | Generación de recomendaciones y resúmenes en castellano |
| Privacidad | **PIIValidator + TextNormalizer** | Detección y bloqueo de datos personales en cada ingesta |
| Despliegue | **Docker Compose** | Contenedorización reproducible de todos los servicios |

---

## Arquitectura del sistema de agentes

```
Solicitud docente
       │
       ▼
┌─────────────┐
│   RECEIVE   │  Interpreta la solicitud y valida el contexto del aula
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   SEARCH    │  Recupera eventos similares de ChromaDB (búsqueda semántica)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     LLM     │  Salamandra-7b-instruct genera texto pedagógico en castellano
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  VALIDATE   │  Verifica coherencia, calcula nivel de confianza (ALTA/MEDIA/BAJA)
└──────┬──────┘
       │
       ▼
Recomendación con patrón explicado → Docente decide
```

---

## Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/classrooms` | Crear un aula nueva |
| `GET` | `/classrooms/{id}` | Datos del aula |
| `POST` | `/events` | Registrar evento pedagógico (con validación PII) |
| `GET` | `/events/{classroom_id}` | Historial de eventos del aula |
| `GET` | `/events/similar` | Búsqueda semántica de eventos similares |
| `GET` | `/patterns/{classroom_id}` | Análisis de patrones: clustering + temporal + efectividad |
| `POST` | `/recommendations` | Solicitar recomendación pedagógica (agente LangGraph) |
| `GET` | `/recommendations/{classroom_id}` | Historial de recomendaciones |
| `POST` | `/recommendations/{id}/feedback` | Feedback docente (útil / no útil) |
| `POST` | `/summaries` | Generar resumen semanal para familias |
| `GET` | `/health` | Estado del sistema |

---

## Instalación y despliegue

### Requisitos previos

- Docker y Docker Compose instalados
- Acceso a la API de Salamandra/ALIA ([solicitar acceso en alia.gob.es](https://alia.gob.es))
- Python 3.11+ (para desarrollo local sin Docker)

### Despliegue con Docker Compose (recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/Barbarasanchez11/AULA_backend.git
cd AULA_backend

# 2. Copiar y configurar variables de entorno
cp .env.example .env
# Editar .env con tu API key de Salamandra/ALIA y configuración de base de datos

# 3. Levantar todos los servicios
docker compose up -d

# 4. Verificar que el sistema está operativo
curl http://localhost:8000/health
```

### Desarrollo local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Iniciar el servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Variables de entorno necesarias

```env
# API de Salamandra/ALIA
ALIA_API_KEY=tu_api_key_aqui
ALIA_API_URL=https://api.alia.gob.es/v1

# Base de datos
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/aulaplus

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_data

# Configuración de seguridad
SECRET_KEY=tu_clave_secreta
```

---

## Privacidad y cumplimiento RGPD

El sistema implementa privacidad por diseño en múltiples capas:

**PIIValidator** — detecta y bloquea automáticamente antes de cualquier persistencia:
- Nombres propios (NER con spaCy)
- Números de DNI / NIE
- Números de teléfono
- Direcciones de email

**Aislamiento por aula** — cada aula tiene su propia instancia de ChromaDB y su propio namespace en PostgreSQL. Es arquitectónicamente imposible que una consulta de un aula retorne datos de otra.

**Sin identificadores de alumnos** — el modelo de datos no incluye ningún campo para identificar alumnos individualmente. Los eventos son del aula como entidad, nunca del alumno.

**Logs de auditoría** — todas las operaciones críticas quedan registradas con timestamp y classroom_id, sin incluir el contenido de los eventos.

El sistema está diseñado para facilitar el cumplimiento del RGPD (UE 2016/679) en el tratamiento de datos en entornos educativos con menores. Para el despliegue en producción se recomienda elaborar un DPIA específico para el centro educativo.

---

## Estructura del proyecto

```
AULA_backend/
├── app/                       # Directorio raíz del código
│   ├── main.py                # Punto de entrada FastAPI
│   ├── routers/               # Endpoints por dominio
│   │   ├── admin.py           # Endpoint de seeding (/admin/seed)
│   │   ├── classrooms.py
│   │   ├── events.py
│   │   ├── recommendations.py
│   │   └── summaries.py
│   ├── services/
│   │   ├── langgraph/         # Pipeline de agentes (4 nodos)
│   │   ├── embeddingService.py # sentence-transformers en local
│   │   ├── pii_validator.py   # Detección y bloqueo de PII
│   │   ├── vector_store.py    # Gestión de ChromaDB
│   │   └── pattern_analysis.py # DBSCAN + análisis temporal
│   ├── models/                # Modelos SQLAlchemy y database.py
│   └── schemas/               # Esquemas Pydantic v2
├── docs/                      # Documentación detallada
├── scripts/                   # Scripts de utilidad
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Cómo contribuir

AULA+ es software libre y las contribuciones son bienvenidas, especialmente de:

- **Profesionales de la educación especial y TEA** — feedback sobre los tipos de eventos, los apoyos disponibles y el lenguaje de las recomendaciones
- **Desarrolladores** — mejoras en el pipeline de análisis, nuevos tipos de patrones, optimizaciones de rendimiento
- **Investigadores** — validación del enfoque pedagógico, estudios de caso, propuestas de nuevas métricas

Para contribuir:

1. Haz un fork del repositorio
2. Crea una rama con un nombre descriptivo: `git checkout -b feature/nombre-de-la-mejora`
3. Realiza tus cambios y asegúrate de que los tests pasan
4. Abre un Pull Request describiendo qué cambia y por qué

Para cambios significativos en el comportamiento del sistema o en el modelo de datos, abre primero un Issue para discutirlo antes de implementar.

---

## Licencia

AULA+ Backend está publicado bajo la **[Licencia Apache 2.0](LICENSE)**.

Puedes usar, modificar y redistribuir este código libremente, incluso con fines comerciales, manteniendo el aviso de copyright original. Consulta el archivo [LICENSE](LICENSE) para el texto completo.

---

## Créditos y reconocimientos

- **Salamandra-7b-instruct** — [Barcelona Supercomputing Center (BSC-CNS)](https://www.bsc.es/) / Iniciativa [ALIA](https://alia.gob.es) del Gobierno de España
- **Verificación regulatoria** — [AESIA](https://www.aesia.es/) — Agencia Española de Supervisión de la Inteligencia Artificial
- **Desarrollado en el contexto de** — Hackathon OdiseIA4Good 2026

---

*AULA+ no analiza a los alumnos. Analiza el entorno que produce las dificultades.*