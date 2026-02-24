Quiero que actúes como un Staff Engineer + Security Engineer especializado en backends de microservicios con agentes de IA.

Tu objetivo es analizar este repositorio de forma PROFUNDA y generar un informe técnico en Markdown que luego usaré para revisión externa.

## Contexto del proyecto
- Es un backend / microservicio de agentes
- Tecnologías principales: FastAPI, LangGraph, ChromaDB, PostgreSQL
- Quiero análisis de:
  1) estructura del proyecto
  2) buenas prácticas de ingeniería
  3) seguridad (tradicional + específica de agentes/LLMs)
  4) calidad de código y mantenibilidad
  5) arquitectura y flujos
  6) recomendaciones priorizadas
### Contexto adicional (importante para el análisis)
- Autenticación/autorización: [sí/no/parcial] (describe brevemente: JWT, API Key, OAuth, etc.)
- Proveedor LLM: [OpenAI / Bedrock / Anthropic / mixto]
- Despliegue/ejecución: [Docker / Docker Compose / Kubernetes / local]
- Tipo de sistema: [multiusuario / single-tenant / POC interna]
- Entorno principal: [dev / staging / prod / PoC]

## Instrucciones IMPORTANTES (modo de trabajo)
1. Haz un análisis exhaustivo del repo (archivos, carpetas, configuración, código, tests, Docker, CI/CD si existe, variables de entorno de ejemplo, etc.).
2. NO hagas cambios destructivos.
3. NO expongas secretos si encuentras `.env` o credenciales. Si aparecen, márcalo como hallazgo de seguridad y REDACTA valores sensibles.
4. Si necesitas ejecutar algo, hazlo en modo seguro (solo lectura cuando sea posible) y documenta qué ejecutaste.
5. Basa tus conclusiones en evidencia concreta del repositorio (rutas de archivos, funciones, clases, módulos, configs).
6. Si algo no puede determinarse con certeza, indícalo explícitamente como “No verificable con evidencia actual”.
7. Al final, genera UN archivo Markdown llamado:

`PROJECT_DEEP_ANALYSIS.md`

## Qué debes analizar (checklist mínimo)

### A. Estructura y arquitectura
- Estructura de carpetas y separación de responsabilidades (API, servicios, dominio, infraestructura, agentes, tools, prompts, persistence, etc.)
- Modularidad y acoplamiento
- Patrones arquitectónicos presentes (layered, hexagonal, clean architecture, service layer, repository pattern, etc.)
- Flujos principales del microservicio (entrada HTTP -> orquestación agente -> herramientas -> vector DB -> DB relacional -> respuesta)
- Gestión de estado de agentes (LangGraph): nodos, edges, memory/state, checkpoints, persistencia
- Uso de ChromaDB y PostgreSQL: propósito, responsabilidades, límites de cada uno
- Manejo de configuración (settings, env vars, profiles, secrets)
- Riesgos de deuda técnica estructural

### B. Calidad de código y buenas prácticas de ingeniería
- Legibilidad, naming, consistencia
- Tipado (type hints), Pydantic models, validaciones
- Manejo de errores/excepciones
- Logging/observabilidad (logs estructurados, trazabilidad, correlation IDs)
- Organización de routers/controllers/services
- Reutilización vs duplicación
- Configuración async/sync en FastAPI (posibles bloqueos de event loop)
- Gestión de dependencias, versiones y pinning (requirements/pyproject/poetry)
- Tests (unitarios/integración/e2e), cobertura, calidad de casos
- Documentación interna del código / README / runbooks
- Migraciones de PostgreSQL (Alembic u otro) y consistencia de esquema
- Robustez de acceso a datos (transacciones, pooling, retries, timeouts)

### C. Seguridad (backend clásico)
Revisa y reporta riesgos y controles relacionados con:
- Gestión de secretos (API keys, tokens, creds)
- Autenticación y autorización (si aplica)
- CORS, CSRF (si aplica), headers de seguridad
- Validación de input y sanitización
- SQL injection (PostgreSQL) / query safety
- SSRF, path traversal, command injection, unsafe deserialization, eval/exec
- Rate limiting / throttling
- Manejo de errores sin filtrar información sensible
- Logs con PII/secrets
- Dependencias vulnerables / prácticas inseguras en librerías
- Seguridad de Docker / contenedores (si hay Dockerfile/docker-compose)
- Configuración de despliegue (si existe) y hardening básico
- Exposición accidental de endpoints internos / debug mode

### D. Seguridad específica de agentes / LLM / RAG (MUY IMPORTANTE)
Analiza riesgos y controles en este backend de agentes:
- Prompt injection (directa/indirecta) y mitigaciones
- Tool abuse / over-permissioned tools (exceso de permisos)
- Exfiltración de datos por herramientas o prompts
- Separación entre instrucciones del sistema / usuario / herramientas
- Validación de outputs estructurados
- Guardrails (si existen): input/output moderation, policy checks, validators
- Control de acciones sensibles (confirmación humana / allowlists / deny lists)
- Auditoría de llamadas a herramientas (qué se ejecuta, con qué parámetros, quién lo pidió)
- Manejo de memoria/contexto del agente (riesgo de persistir datos sensibles)
- Riesgo de contaminación del vector store (RAG poisoning / prompt injection desde documentos)
- Tenant isolation / separación de datos entre usuarios (si aplica)
- Seguridad en ChromaDB (colecciones, metadatos, controles)
- Trazabilidad y forensics en flujos del agente
- Protección frente a secrets leakage desde entorno o ficheros
- Recomendaciones de hardening específicas para LangGraph/FastAPI/chains/tools

### E. Operación y mantenibilidad
- Preparación para producción
- Configuración por entornos (dev/staging/prod)
- Observabilidad (logs, métricas, tracing)
- Health checks / readiness / liveness
- Reintentos, circuit breakers, timeouts, idempotencia
- Escalabilidad básica del servicio
- Gestión de errores en integraciones externas (LLM APIs, DBs, vectordb)
- Backups / recuperación (si se puede inferir)

## Formato OBLIGATORIO del archivo `PROJECT_DEEP_ANALYSIS.md`

El informe debe tener esta estructura exacta (puedes añadir subsecciones):

# Project Deep Analysis Report

## 1. Executive Summary
- Resumen breve (máx 10-15 líneas)
- Estado general del proyecto (maturity snapshot)
- Top 5 hallazgos más importantes (mezcla de ingeniería + seguridad)

## 2. Repository Overview
- Stack detectado
- Estructura de carpetas (tabla)
- Componentes principales (tabla)
- Suposiciones y límites del análisis

## 3. Architecture & Core Flows
- Descripción de arquitectura actual
- Flujo principal de request (paso a paso)
- Flujo del agente (LangGraph)
- Diagrama textual (ASCII o Mermaid si procede)
- Riesgos arquitectónicos observados

## 4. Engineering Best Practices Review
### 4.1 Lo que está bien
### 4.2 Oportunidades de mejora
### 4.3 Anti-patterns detectados (si existen)

## 5. Security Review (Backend + Agentic/LLM)
### 5.1 Hallazgos de seguridad (tabla)
Usa una tabla con columnas:
- ID
- Severidad (Critical/High/Medium/Low/Info)
- Categoría
- Hallazgo
- Evidencia (archivo/ruta)
- Riesgo
- Recomendación

### 5.2 Hallazgos específicos de agentes/LLM
(igual de detallado)

### 5.3 Controles existentes identificados
- Qué controles ya existen y qué cubren
- Cobertura parcial / gaps

## 6. Code Quality & Maintainability
- Evaluación de calidad
- Mantenibilidad
- Testing
- Documentación
- Deuda técnica priorizada

## 7. Prioritized Remediation Plan
Crear roadmap por fases:
- Quick Wins (1-7 días)
- Corto plazo (2-4 semanas)
- Medio plazo (1-3 meses)

Para cada acción:
- Prioridad
- Impacto
- Esfuerzo
- Responsable sugerido (Backend/Security/DevOps)
- Dependencias

## 8. Skill Extraction for Future Review
Extrae una lista de skills/tópicos que se desprenden del proyecto para trabajar después:
- Skills de arquitectura
- Skills de FastAPI
- Skills de LangGraph/agentes
- Skills de seguridad backend
- Skills de seguridad IA/LLM
- Skills de datos (PostgreSQL/ChromaDB)
- Skills de DevOps/Operación
- Skills de testing/calidad

(Esto me servirá para convertirlo después en un plan de mejora)

## 9. Appendix: Evidence Map
Lista de evidencias usadas:
- archivo/ruta
- función/clase
- motivo de relevancia

## 10. Final Scorecard (opcional pero recomendado)
Incluye una puntuación 1-5 o 1-10 para:
- Arquitectura
- Código
- Seguridad backend
- Seguridad LLM/agentes
- Operabilidad
- Testing
- Documentación
- Preparación para producción

Y una nota global con justificación.

## Requisitos de calidad del informe
- Sé específico, no genérico.
- Cada recomendación debe estar conectada con evidencia.
- Evita frases vagas como “mejorar seguridad” sin decir cómo.
- Si detectas algo positivo, también documenta fortalezas.
- Priorización realista (no propongas reescribir todo).
- Tono profesional, técnico, directo.

## Entregable final
1. Crea el archivo `PROJECT_DEEP_ANALYSIS.md`
2. Muestra un breve resumen en consola/chat con:
   - Top 10 hallazgos
   - Riesgos críticos/altos
   - Quick wins principales