# Plan Semanal - AULA+ Backend

## Estado Actual (Miércoles 5 de Febrero)

### ✅ Completado

#### Lunes 3 Feb - Backend Base Funcional
- ✅ Proyecto FastAPI limpio
- ✅ Configuración de entorno (env, requirements)
- ✅ Endpoint /health
- ✅ Endpoints de aulas (classrooms)
- ✅ Endpoints de eventos (events)
- ✅ Modelo de datos mínimo (SQLAlchemy)

#### Martes 4 Feb - Persistencia Sólida
- ✅ PostgreSQL funcionando
- ✅ Esquema definitivo: aula, evento, recomendación
- ✅ Seed de datos de prueba (manual)
- ✅ Adminer configurado

#### Miércoles 5 Feb (Hasta ahora)
- ✅ Documentación de arquitectura técnica detallada
- ✅ Confirmación de que NO hay datos personales
- ✅ Documento de protección de datos y privacidad

---

## Tareas Pendientes

### 🎯 Miércoles 5 Feb (Resto del día)

#### 1. Base IA (sin LangGraph aún)
- [ ] **Elegir modelo de embeddings**
  - Evaluar `sentence-transformers` (modelos en español)
  - Opciones: `paraphrase-multilingual-MiniLM-L12-v2` o `distiluse-base-multilingual-cased-v2`
  - Decidir modelo final y documentar elección

- [ ] **Generar embeddings de eventos**
  - Crear servicio `app/services/embeddings.py`
  - Función para generar embedding de un evento (descripción + contexto)
  - Función para generar embeddings en batch
  - Probar con eventos de ejemplo

- [ ] **Montar FAISS o Chroma**
  - Decidir entre FAISS (local, rápido) o Chroma (persistente, más features)
  - Instalar dependencias necesarias
  - Crear servicio `app/services/vector_store.py`
  - Configurar almacenamiento de embeddings por aula

- [ ] **Buscar eventos similares por similitud**
  - Implementar función de búsqueda semántica
  - Endpoint opcional: `GET /events/similar?event_id={id}&classroom_id={id}`
  - Retornar eventos similares con score de similitud
  - Probar con datos de ejemplo

**Resultado esperado**: "Dado un evento, encuentro otros parecidos"

---

### 🎯 Jueves 6 Feb

#### 1. Cerrar Fase 1
- [ ] **Escribir pseudoflujo IA**
  - Documentar cómo funcionará el sistema de recomendaciones
  - Flujo desde evento → embedding → búsqueda de patrones → recomendación
  - Diagrama de flujo del proceso de IA
  - Documentar en `docs/ai_workflow.md`

- [ ] **Revisión final de arquitectura**
  - Verificar que todo está documentado
  - Actualizar README con estado final
  - Revisar que no hay deuda técnica

- [ ] **Preparar para ciberseguridad** (coordinación con compañero)
  - Documentar puntos de entrada de datos
  - Identificar dónde se necesita PII scanner
  - Preparar estructura para MCP (Model Context Protocol)
  - Documentar flujo de anonimización antes de LLMs

**Resultado esperado**: Proyecto estable, sin deuda conceptual, listo para integración de ciberseguridad

---

## Consideraciones de Ciberseguridad

### PII Scanner
- **Ubicación**: Antes de que los datos entren al sistema de IA
- **Puntos de entrada**:
  1. `POST /events/` - Validar `description`, `additional_supports`, `observations`
  2. `PUT /events/{id}` - Validar campos actualizados
  3. Cualquier texto que vaya a generar embeddings

- **Herramientas sugeridas**:
  - `presidio` (Microsoft) - Detección y anonimización de PII
  - `spacy` con modelos NER en español
  - Validación custom con regex (nombres, DNI, etc.)

### MCP (Model Context Protocol)
- **Cuándo**: Cuando se implementen agentes de IA (LangGraph)
- **Propósito**: Garantizar que los datos anonimizados no se envíen a servidores de LLMs
- **Flujo propuesto**:
  ```
  1. Evento llega → PII Scanner detecta PII
  2. Agente de anonimización procesa texto
  3. Texto anonimizado → Generación de embeddings (local)
  4. Embeddings → Vector DB (local)
  5. Búsqueda de patrones (local, sin LLM)
  6. Generación de recomendaciones (con LLM, pero sin datos originales)
  ```

### Agentes de Anonimización
- **Responsabilidad**: Procesar y anonimizar cualquier texto antes de:
  - Generar embeddings
  - Enviar a LLMs
  - Almacenar en Vector DB

- **Estrategia**:
  - Reemplazar nombres propios con placeholders (`[ESTUDIANTE_1]`, `[ESTUDIANTE_2]`)
  - Eliminar DNI, fechas de nacimiento, direcciones
  - Mantener estructura semántica del texto
  - Log de anonimizaciones para auditoría

### Protección de Servidores LLM
- **Principio**: Los datos originales NUNCA deben llegar a servidores de LLMs externos
- **Medidas**:
  1. Anonimización obligatoria antes de cualquier llamada a LLM
  2. Validación de que no hay PII en el contexto enviado
  3. Uso de embeddings locales (no enviar texto original)
  4. Logging de todas las interacciones con LLMs

---

## Estructura de Archivos Pendientes

```
app/
├── services/
│   ├── embeddings.py          # Generación de embeddings
│   ├── vector_store.py        # Gestión de Vector DB (FAISS/Chroma)
│   ├── pattern_analysis.py    # Análisis de patrones (futuro)
│   └── pii_scanner.py         # Detección de PII (coordinación con compañero)
├── agents/                    # (Futuro, cuando se implemente LangGraph)
│   └── anonymization_agent.py # Agente de anonimización
└── utils/
    └── text_processing.py     # Utilidades de procesamiento de texto

docs/
├── ai_workflow.md             # Pseudoflujo de IA
├── cybersecurity_plan.md     # Plan de ciberseguridad (coordinación)
└── embeddings_guide.md        # Guía de uso de embeddings
```

---

## Prioridades

### Alta Prioridad (Hacer hoy)
1. Elegir modelo de embeddings
2. Generar embeddings de eventos
3. Montar Vector DB básico
4. Implementar búsqueda de eventos similares

### Media Prioridad (Jueves)
1. Documentar pseudoflujo IA
2. Preparar estructura para ciberseguridad
3. Revisión final de arquitectura

### Baja Prioridad (Futuro)
1. Integración completa de PII scanner
2. Implementación de agentes de anonimización
3. Integración de MCP
4. Sistema de recomendaciones automáticas

---

## Notas

- **Ciberseguridad**: El compañero se encargará de implementar PII scanner y MCP cuando tengamos agentes
- **Enfoque**: Primero hacer que funcione la búsqueda semántica básica, luego integrar ciberseguridad
- **Principio**: Los datos anonimizados NO deben llegar a servidores de LLMs externos
- **Validación**: Cada paso debe probarse con datos de ejemplo antes de continuar

---

**Última actualización**: 5 de febrero de 2026  
**Estado**: En progreso - Miércoles 5 Feb

