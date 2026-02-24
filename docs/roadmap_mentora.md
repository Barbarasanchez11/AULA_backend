# Roadmap AULA+ - Presentación para Mentora

**Fecha**: 5 de febrero de 2026  
**Estado**: Fase 1 completada, iniciando Fase 2 (Análisis de Patrones)

---

## Resumen Ejecutivo

AULA+ es un sistema backend de apoyo pedagógico para aulas TEA que registra eventos anonimizados, analiza patrones históricos y genera recomendaciones pedagógicas bajo demanda, respetando estrictamente la privacidad y protección de datos.

**Principios fundamentales:**
- NO recopila datos personales de menores
- NO usa biometría
- NO diagnostica ni evalúa clínicamente
- Control humano siempre prioritario
- IA explicable y responsable

---

## Estado Actual del Proyecto

### ✅ Fase 1: Fundamentos (COMPLETADA)

**Backend Base:**
- ✅ FastAPI con 13 endpoints funcionales
- ✅ PostgreSQL con esquema completo (classrooms, events, recommendations)
- ✅ Validación Pydantic en todos los endpoints
- ✅ Aislamiento de datos por aula
- ✅ Documentación técnica completa

**Endpoints implementados:**
- 5 endpoints de Classrooms (CRUD completo)
- 5 endpoints de Events (CRUD completo)
- 3 endpoints de Recommendations (GET list, GET by ID, POST)

**Protección de Datos:**
- ✅ Análisis completo de privacidad (todos los campos verificados)
- ✅ Documentación de medidas de protección
- ✅ Checklist de cumplimiento RGPD
- ✅ Plan de ciberseguridad (PII scanner, MCP) coordinado con compañero

---

## Fase 2: Análisis de Patrones (EN PROGRESO)

### Decisión Técnica: Sistema Híbrido de Embeddings

**Análisis realizado:**
- Comparación de 3 modelos: MiniLM, distiluse, mpnet
- Evaluación de velocidad vs calidad semántica
- Pruebas con eventos reales del aula TEA

**Decisión tomada:**
Implementar sistema híbrido con dos modelos:

1. **distiluse-base-multilingual-cased-v2** (rápido)
   - Velocidad: 0.09s por evento
   - Dimensiones: 512
   - Uso: Búsquedas rápidas, previews, sugerencias inmediatas

2. **paraphrase-multilingual-mpnet-base-v2** (calidad)
   - Velocidad: 0.58s por evento
   - Dimensiones: 768
   - Uso: Clustering, análisis histórico, generación de recomendaciones
   - Calidad semántica: 0.85 de similitud en eventos similares (vs 0.52 del rápido)

**Justificación:**
- Priorizamos calidad semántica sobre velocidad extrema
- El sistema no opera en tiempo real (registro humano, no sensores)
- Volumen bajo: 5-10 eventos/día = 3-6 segundos totales
- La confianza del docente depende de la coherencia semántica

---

### Subtareas de Fase 2 (En curso)

#### 1. Servicio de Embeddings Híbrido ⏳
- **Estado**: Diseño completado, implementación iniciada
- **Archivo**: `app/services/embeddingService.py`
- **Funcionalidades**:
  - Carga lazy de ambos modelos
  - Generación de embeddings (rápido y calidad)
  - Batch processing para múltiples eventos
  - Combinación de texto de eventos para embeddings

#### 2. Vector Database (Chroma) ⏳
- **Estado**: Pendiente
- **Decisión**: Chroma (persistencia automática, búsqueda por metadata)
- **Estructura**: Una colección por aula (aislamiento de datos)
- **Funcionalidades**:
  - Almacenamiento de embeddings
  - Búsqueda semántica con filtros (classroom_id, event_type)
  - Persistencia automática

#### 3. Integración con Eventos ⏳
- **Estado**: Pendiente
- **Funcionalidades**:
  - Generar embeddings al crear evento (ambos modelos)
  - Almacenar en Vector DB
  - Regenerar embeddings al actualizar evento

#### 4. Búsqueda Semántica ⏳
- **Estado**: Pendiente
- **Funcionalidades**:
  - Búsqueda rápida (distiluse) para previews
  - Búsqueda de calidad (mpnet) para análisis
  - Filtrado por umbral de similitud (≥0.75)
  - Endpoint: `GET /events/similar`

---

## Fase 3: Recomendaciones Automáticas (PENDIENTE)

### Integración de LangGraph
- Orquestación de agentes de IA
- Flujo: Evento → Embedding → Búsqueda de patrones → Generación de recomendación
- Validación humana progresiva (3 niveles)

### Sistema de Patrones
- Clustering de eventos similares (DBSCAN/HDBSCAN)
- Detección de correlaciones temporales
- Análisis de efectividad de apoyos
- Generación de recomendaciones basadas en patrones

### Protección de Datos en IA
- **PII Scanner**: Validación antes de generar embeddings
- **Agentes de Anonimización**: Procesar texto antes de LLMs
- **MCP (Model Context Protocol)**: Garantizar que datos anonimizados no lleguen a servidores externos
- **Principio**: Los datos originales NUNCA salen del servidor local

---

## Consideraciones de Gobernanza e IA

### Principios de IA Responsable

1. **Explicabilidad**
   - Las recomendaciones incluyen el patrón detectado que las sustenta
   - El docente puede ver eventos similares que generaron la recomendación
   - No hay "cajas negras"

2. **Control Humano**
   - Recomendaciones bajo demanda (no automáticas)
   - El docente decide qué aplicar
   - Feedback del docente mejora el sistema progresivamente

3. **Transparencia**
   - Documentación completa de decisiones técnicas
   - Justificación de elección de modelos
   - Métricas de calidad visibles

4. **Privacidad por Diseño**
   - Anonimización desde el registro
   - Aislamiento por aula
   - Sin datos personales en embeddings ni LLMs

### Cumplimiento Normativo

- ✅ RGPD: Minimización de datos, limitación de propósito
- ✅ LOPD-GDD: Protección de datos de menores
- ✅ Sin biometría: Explícitamente excluido
- ✅ Sin diagnóstico clínico: Solo apoyo pedagógico

### Validación Progresiva

**Nivel 1 (Actual):**
- Recomendaciones basadas en patrones observados
- Literatura pedagógica general
- Etiquetado: "Sugerencia basada en experiencias previas del aula"

**Nivel 2 (Futuro):**
- Feedback del docente ("útil / no útil")
- Selección manual de recomendaciones aplicadas
- Ajuste de priorización

**Nivel 3 (Futuro):**
- Curaduría por expertos pedagógicos
- Validación de patrones detectados
- Refinamiento de recomendaciones

---

## Roadmap Temporal

### Esta Semana (5-7 Feb)

**Miércoles 5 Feb:**
- ✅ Análisis de modelos de embeddings
- ✅ Decisión técnica: sistema híbrido
- ⏳ Implementación servicio de embeddings

**Jueves 6 Feb:**
- ⏳ Vector DB (Chroma)
- ⏳ Integración con eventos
- ⏳ Búsqueda semántica
- ⏳ Endpoint de búsqueda

**Viernes 7 Feb:**
- ⏳ Testing y ajustes
- ⏳ Documentación de arquitectura IA
- ⏳ Pseudoflujo de recomendaciones

### Próxima Semana (10-14 Feb)

- Integración de LangGraph (si tiempo)
- Sistema de clustering
- Generación básica de recomendaciones
- Testing con datos reales

---

## Métricas de Éxito

### Técnicas
- ✅ 13 endpoints funcionales
- ⏳ Embeddings generados en <1s por evento
- ⏳ Búsqueda semántica con similitud ≥0.75
- ⏳ Sistema híbrido operativo

### Pedagógicas
- Recomendaciones coherentes con eventos históricos
- Explicabilidad de patrones detectados
- Confianza del docente en el sistema

### Gobernanza
- ✅ Sin datos personales en el sistema
- ✅ Documentación completa de privacidad
- ⏳ PII Scanner implementado
- ⏳ Validación humana en todas las recomendaciones

---

## Riesgos y Mitigaciones

### Riesgo 1: Calidad de Embeddings Insuficiente
**Mitigación**: Sistema híbrido permite usar mpnet para análisis críticos

### Riesgo 2: Fuga de Datos a LLMs Externos
**Mitigación**: MCP + Agentes de anonimización + Validación previa

### Riesgo 3: Recomendaciones Incoherentes
**Mitigación**: Umbrales de similitud altos (≥0.75) + Validación humana

### Riesgo 4: Complejidad del Sistema Híbrido
**Mitigación**: Documentación clara + Testing exhaustivo + Arquitectura modular

---

## Preguntas para la Mentora

1. **IA y Gobernanza:**
   - ¿La estrategia de validación progresiva (3 niveles) es adecuada?
   - ¿Hay consideraciones adicionales de gobernanza que deberíamos incluir?

2. **Técnicas:**
   - ¿El sistema híbrido es la mejor opción o deberíamos simplificar?
   - ¿Recomendaciones sobre la implementación de MCP y anonimización?

3. **Pedagógicas:**
   - ¿Cómo podemos mejorar la explicabilidad de las recomendaciones?
   - ¿Qué métricas de calidad pedagógica deberíamos rastrear?

---

## Conclusión

AULA+ está en una fase sólida de desarrollo, con fundamentos técnicos completos y decisiones arquitectónicas bien justificadas. El sistema híbrido de embeddings balancea calidad semántica y velocidad, priorizando la coherencia pedagógica sobre la latencia extrema.

**Próximos pasos críticos:**
1. Completar servicio de embeddings híbrido
2. Integrar Vector DB
3. Implementar búsqueda semántica
4. Preparar para integración de LangGraph

**Principio rector:** IA responsable, explicable y al servicio del docente, nunca sustituyéndolo.

---

**Contacto:**  
**Equipo:** Desarrollo AULA+  
**Repositorio:** [GitHub]  
**Documentación:** `/docs/`

