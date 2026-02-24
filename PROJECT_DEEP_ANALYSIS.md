# Project Deep Analysis Report

## 1. Executive Summary
El proyecto **AULA+** es un microservicio backend innovador, diseñado como sistema de apoyo pedagógico para docentes en aulas TEA. Utiliza un stack moderno (FastAPI, PostgreSQL, ChromaDB, LangGraph) para generar recomendaciones pasadas en historial del aula a través del cruce de datos tabulares, búsqueda vectorial y análisis generativo LLM. 
A nivel de madurez, se encuentra en una fase funcional y de Prueba de Concepto Avanzada (PoC). Sin embargo, carece de controles fundamentales para su paso a producción segura: adolece de exposición de herramientas administrativas (Adminer), CORS muy permisivos, ausencia de migraciones de base de datos, configuraciones de despliegue basadas en "modo desarrollo" (uvicorn reload), y vulnerabilidades específicas de Agentes AI frente a Prompt Injections indirectas, además de no parsear/validar estandarizadamente las salidas del framework LLM.

**Top 5 hallazgos más importantes**:
1. **Critical:** La configuración de base de datos y herramientas como Adminer, CORS general `["*"]` y credenciales expuestas en `docker-compose.yml` son riesgos severos en caso de despliegue accidental a producción.
2. **High:** Falta de mitigación contra Prompt Injection indirecto en LangGraph; los descriptores introducidos por usuarios no se aíslan o escapan antes de llegar al promting del LLM.
3. **High:** Ausencia de validación estructurada / guardrails a la salida del LLM antes de formatearla como Recomendación.
4. **Medium:** Falta de un sistema de migraciones (Alembic) que ponga en grave riesgo la integridad de la base de datos de producción post-lanzamiento ante futuras evoluciones.
5. **Medium:** Deuda técnica transversal en observabilidad: uso de `print()` generalizado para debugging en vez de telemetría o logging estructurado corporativo, e inexistencia de endpoints formales de `/health`.

## 2. Repository Overview
- **Stack detectado**: Python 3.11, FastAPI, SQLAlchemy (Async), PostgreSQL, ChromaDB (persistente local), LangGraph, Llama-3.1-8b (vía HuggingFace / Groq), Pydantic v2.
- **Suposiciones y límites**: Se ha analizado el código estático actual del backend de AULA+, no se han observado flujos de red dinámicos o integraciones vivas con sistemas de front-end o servicios de terceros.

| Componente Principal | Ruta de ejemplo | Función |
|----------------------|----------------|---------|
| **Core API** | `app/main.py`, `app/routers/` | Enrrutamiento, middleware, handlers HTTP, Pydantic validation. |
| **Modelos Relacionales** | `app/models/` | Definición SQLAlchemy Async para aulas, eventos y recomendaciones. |
| **Orquestación LangGraph** | `app/services/langgraph/` | Nodos, estado, y grafo para la cadena de recomendación predictiva. |
| **Vector Database** | `app/services/vector_store.py`| Alojamiento y particionamiento de ChromaDB para aislar colecciones por Aula.|
| **Protección Privacidad**| `app/services/pii_validator.py`| Limpieza pre-almacenamiento y pre-procesado para evitar datos PII (Identificativos). |

## 3. Architecture & Core Flows
### Descripción Híbrida
AULA+ cuenta con una arquitectura de Layered/Controller-Service Pattern que expone una API REST tradicional, pero su core de negocio invoca un State Graph dinámico (LangGraph).
1. **Flujo Principal (Registro Evento):** HTTP POST -> Validador Router Pydantic -> PIIValidator (Privacidad) -> DB PostgreSQL (Persistencia) -> BackgroundTask -> EmbeddingService (Sentence-Transformers) -> ChromaDB.
2. **Flujo del agente (Recomendaciones):** HTTP POST -> Iniciación LangGraphState -> Nodo 1 (`receive_event`) -> Nodo 2 (`search_context` en ChromaDB) -> Nodo 3 (`generate_llm` en HF Endpoint) -> Nodo 4 (`validate_format`) -> Retorno API FastAPI -> Guardado DB.

**Riesgos Arquitectónicos**:
- Alta conjunción de responsabilidades asíncronas / síncronas. En LangGraph `node_generate_llm` la invocación es secuencial bloquante pero FastAPI es asíncrono. Esto bloquea el Event Loop si el LLM tarda (aunque es minoritario si se usa hilos, se recomienda AsyncLangChain/AsyncHuggingFaceEndpoint).
- No hay persistencia robusta nativa de checkpoints o fallos intermedios del grafo. Si el LLM falla, el router FastAPI devuelve un error 500 y el estado en vuelo se pierde sin retries / resiliencia (circuit breaking).

## 4. Engineering Best Practices Review
### 4.1 Lo que está bien
- **Validación robusta del tipado**: Exhaustivo uso de esquemas `Pydantic` (v2) y enums estructurados que protegen las fronteras del sistema.
- **Validación PII temprana**: El componente `PIIValidator` está estratégicamente integrado antes del guardado en DB / VectorDB, lo que evidencia buenas intenciones de Secure-by-Design en privacidad educativa.
- **Aislamiento Multitenant Vectorial**: Mantenimiento de colecciones separadas por classroom (`classroom_{uuid}_{model_type}`) en ChromaDB es una topológica genial para aislar y evitar fugas RAG de tenant cruzado.

### 4.2 Oportunidades de mejora
- **Migraciones (Alembic)**: Aunque `alembic` está en el `requirements.txt`, no hay carpetas ni sistema preconfigurado para su uso; el base inicial es un mero `Base.metadata.create_all()`.
- **Dependencias No Ancladas**: En `requirements.txt` hay carencia de hard pinning (`fastapi`, `chromadb`, etc). Se aconseja `poetry` o pinning de subversiones seguras.
- **Observabilidad Limitada**: Predominan los `print(f" [DEBUG] ...")` directos a `stdout` (e.g. `vector_store.py`) en lugar de `logger`.
- **Organización de Testing**: Gran mezcla entre el directorio `scripts/` y `tests/` con tests que parecen más scripts ad-hoc que flujos de aserción automática.

### 4.3 Anti-patterns detectados
- Bloqueo en BackgroundTasks: Las operaciones sobre vector_store son manejadas de fondo pero carecen de una cola transaccional segura; si uvicorn crashea durante una `BackgroundTask`, el embedding se desincroniza frente a Postgres de por vida, generando la anomalía de "escritura fragmentada".

## 5. Security Review (Backend + Agentic/LLM)
### 5.1 Hallazgos de seguridad (Tradicional)
| ID | Severidad | Categoría | Hallazgo | Evidencia | Riesgo | Recomendación |
|----|-----------|-----------|----------|------------|--------|---------------|
| SEC-01 | **CRITICAL** | DevEx / Ops | Herramienta de BD expuesta. | `docker-compose.yml` (Adminer 8081) | Riesgo extremo si la instancia final lo despliega expuesto. | Remover de production docker manifest o encapsular con Auth (BasicAuth, network cerrada). |
| SEC-02 | **HIGH** | Configuración | CORS Permisivo Mundial (`["*"]`). | `app/main.py:18` | Posibles ataques CSRF o secuestro front. | Limitar orígenes en entorno prod explícitamente (`frontend.domain.es`). |
| SEC-03 | **MEDIUM** | Credenciales | Valores duros en compose. | `docker-compose.yml:20` | Leak interno si el repo es expuesto. | Mover estrictamente al `.env` y usar `${POSTGRES_PASSWORD}` . |

### 5.2 Hallazgos específicos de agentes/LLM
| ID | Severidad | Categoría | Hallazgo | Evidencia | Riesgo | Recomendación |
|----|-----------|-----------|----------|------------|--------|---------------|
| AI-01 | **HIGH** | Input / Prompt Injection | Inyeccion indirecta desde observaciones o entrada docente. | `generate_llm.py:49` | El LLM puede salirse de su rol y generar payloads ofensivos al front. | Aislar las entradas de usuario del prompt del sistema mediante demarcadores XML (`<user_input></user_input>`) o ChatTemplates en mensajes dedicados (HumanMessage). |
| AI-02 | **HIGH** | Output / Guardrails | Ceguera estructurada en Output. | `validate_format.py` | La validación únicamente intenta extraer el título partiendo `\n`, sin garantía real ni output format compliance. | Obligar salida JSON en la LLM y procesar con Validadores estructurados desde `instructor` o Guardrails Output Parsers. |
| AI-03 | **MEDIUM** | Denial of Service | Excesivos reintentos asíncronos en ChromaDB sin rate limits. | `events.py:202` | RAG DDOS si Chroma sufre presión de requests concurrentes. | Añadir limitadores de RateLimit, timeouts y circuit breakers en LangGraph orchestrator. |

### 5.3 Controles existentes identificados
- `PIIValidator`: Cubre muy bien filtrado de DNI, teléfono y nombres en lenguaje educativo previo al paso a Base de Datos. Excelente control implementado.
- Pydantic Validations: Esquemas con enums acotados previenen una gran banda de abusos HTTP convencionales.

## 6. Code Quality & Maintainability
- **Code Quality**: En general modularizada bajo capas. Sin embargo, hay exceso de bloques Try-except abarca genéricos `except Exception as e:` que esconden errores críticos detrás del telón, en lugar de atrapar problemas de conectividad concretos de red HTTP.
- **Testing**: A mejorar severamente. Los scripts manuales dominan, por lo que escalar la solución sin que rompan las regresiones del LLM (ejemplo, evaluar si el RAG mejora con el tiempo usando PromptFoo o Ragas) es insostenible temporalmente.
- **Deuda Técnica Priorizada**:
  1. Testing estructurado QA.
  2. Implementación real de un plan de Migraciones en Alembic.
  3. Desglose del archivo `docker-compose` a un `prod-compose` sin `adminer`.

## 7. Prioritized Remediation Plan

**Fase 1: Quick Wins (1-7 días. Esfuerzo: Bajo)**
- **Backend**: Sustituir CORS `*` por orígenes explícitos configurables por environment (Responsable: Backend). 
- **Security**: Parametrizar las contraseñas hardcoreadas en el docker-compose con lecturas de entorno (Responsable: DevOps).
- **IA**: Añadir barreras XML en el core prompt de `generate_llm` para proteger la entrada inyectada del contexto docente (Responsable: AI/Security).

**Fase 2: Corto plazo (2-4 semanas. Esfuerzo: Medio)**
- **Backend / DB**: Iniciar repositorio de `Alembic` para consolidar el esquema SQLAlchemy y congelarlo antes de que haya datos reales (Responsable: Backend).
- **Operaciones**: Empezar a utilizar el logger `logging` incorporado de Python a través de todos los archivos y eliminar trazas de `print` (Responsable: Backend).
- **IA**: Evolucionar `validate_format.py` para forzar e interrogar la LLM pidiendo JSON Output. Validar directamente con Pydantic. (Responsable: Backend/AI).

**Fase 3: Medio plazo (1-3 meses. Esfuerzo: Alto)**
- **Quality**: Crear suite E2E completa de Test Unitarios sobre las APIs y aserciones deterministas sobre el framework de LangGraph (Responsable: Backend).
- **IA Security**: Desplegar una protección externa semántica contra Prompt Injections / Output Moderation (ej: LakeraGuard / NeMo Guardrails) antes de presentar la respuesta final a la base de datos (Responsable: Security/AI).

## 8. Skill Extraction for Future Review
- **Skills de arquitectura**: Transacciones asíncronas seguras distribuidas (Postgres + VectorStore Eventual Consistency).
- **Skills de FastAPI**: Middleware de observabilidad/logging custom; Testing in FastAPI Async con Pytest-Asyncio.
- **Skills de LangGraph/agentes**: Async LangGraph Nodes; Control de estados de fallo con Fallback Edges; Structured Output Parsers.
- **Skills de seguridad backend**: CORS policies dinámicas por entorno; Gestión segura de compose en multi-ambiente.
- **Skills de seguridad IA/LLM**: Técnicas anti-indirect prompt injection (XML tagging); Output Moderation en entornos educativos con LLM-as-a-Judge.
- **Skills de datos**: Alembic Database Migrations en modelos asíncronos.
- **Skills de DevOps/Operación**: Despliegue seguro de modelos Docker-compose vs Kubernetes. Puesta de health checks HTTP formales.

## 9. Appendix: Evidence Map
- `docker-compose.yml:32-44`: Evidencia Adminer como capa de red abierta a base de datos.
- `app/services/langgraph/nodes/generate_llm.py:49`: Prompting directo mediante f-strings sin aislamiento, mostrando inyección y falta de JSON Mode.
- `app/services/vector_store.py:97`: Evidencia de `print` logging por doquier, carente de formato centralizado e impacto APM eventual.
- `app/main.py:18`: Allow Origins global ("*").
- `app/config.py`: Ausencia de configuraciones paramétricas para definir dominios admitidos de CORS o URL específicas.
- `requirements.txt`: Dependencias sin subversiones ancladas.

## 10. Final Scorecard
- Arquitectura: 7/10
- Código: 6/10
- Seguridad backend: 4/10
- Seguridad LLM/agentes: 5/10
- Operabilidad: 4/10
- Testing: 3/10
- Documentación: 8/10
- Preparación para producción: 3/10


**NOTA GLOBAL: 5.0 / 10**
**Justificación**: AULA+ demuestra una excelente concepción arquitectónica e intenciones fantásticas orientándose hacia RAG sobre agentes modulares con capas pre-validación (excelente idea PII). Sin embargo, está sumamente anclado a un "laboratorio POC" e infraestructura de desarrollo; salir a producción mañana con dependencias y arquitecturas frágiles ante concurrencia/transaccionalidad en red representaría un riesgo inaceptable para los datos del entorno docente. Necesita estabilizar sus barreras operativas urgentemente.

## 11. Hackathon Deployment Plan (PoC)

Para el despliegue inmediato del PoC y su conexión con el frontend, se recomienda el siguiente plan táctico:

### 11.1 Plataformas Recomendadas
| Plataforma | Ventajas | Desventajas |
|------------|----------|-------------|
| **Render** | Tier gratuito de DB y Web Server. Muy simple. | RAM limitada (512MB). La DB gratuita expira en 90 días. |
| **Railway** | Excelente rendimiento, más RAM (~2GB+). | No es 100% gratis (usa créditos iniciales). |

### 11.2 Estrategia de Recursos (Critical)
Dado que usas `sentence-transformers` localmente:
1. **El Problema**: Cargar los modelos locales consume ~1.2GB de RAM. En Render Free (512MB) el servidor sufrirá un `Out Of Memory (OOM)` y se reiniciará constantemente.
2. **La Solución**: **Externalizar Embeddings**. Debemos cambiar `EmbeddingService` para llamar a la API de Hugging Face. Esto reduce el consumo de RAM del servidor a <300MB, permitiendo el uso de tiers gratuitos.

### 11.3 Checklist de Despliegue
- [ ] **Externalizar Embeddings**: Implementar llamadas a HF Inference API (ya planificado en `implementation_plan.md`).
- [ ] **Configurar Postgres**: Crear instancia gratuita en Render.
- [ ] **Environment Variables**:
  - `DATABASE_URL`: URL secreta de la DB en la nube.
  - `HF_API_KEY`: Tu token de Hugging Face.
- [ ] **Ajustar Dockerfile**: Eliminar la descarga de modelos pesados para aligerar la imagen.
- [ ] **CORS**: Configurar la URL de tu frontend (ej. `midominio.vercel.app`) en `app/main.py`.

### 11.4 Recomendación Final para el Hackathon
Utilizar **Render** con la base de datos gestionada incluída. Para que funcione, el primer paso técnico obligatorio antes de subir nada es completar la **Fase de Externalización de Embeddings**.
