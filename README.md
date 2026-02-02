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

- **Backend**: Python + FastAPI
- **Base de datos relacional**: PostgreSQL
- **Orquestación IA**: LangGraph
- **Embeddings semánticos**: Para análisis de similitud entre eventos
- **Vector DB**: FAISS o Chroma (para búsqueda semántica de patrones)
- **Despliegue**: Contenedores Docker, escalable por aula

### Flujo de Funcionamiento

```
1. REGISTRO DE EVENTO
   └─> Docente registra evento anonimizado
   └─> Sistema valida estructura y tipo
   └─> Almacena en BD relacional (PostgreSQL)

2. PROCESAMIENTO PERIÓDICO (ej: diario/nocturno)
   └─> Sistema analiza eventos históricos del aula
   └─> Genera embeddings semánticos de eventos similares
   └─> Identifica patrones recurrentes (clustering)
   └─> Detecta correlaciones temporales (día/hora)
   └─> Analiza efectividad de apoyos utilizados

3. GENERACIÓN DE RECOMENDACIONES
   └─> Basado en patrones detectados
   └─> Considera contexto temporal y situacional
   └─> Prioriza recomendaciones con mayor evidencia histórica
   └─> Almacena recomendaciones generadas

4. CONSULTA POR DOCENTE
   └─> Docente solicita recomendaciones (bajo demanda)
   └─> Sistema presenta recomendaciones más relevantes
   └─> Docente puede filtrar por tipo o contexto
   └─> Sistema registra qué recomendaciones se consultan (métricas)

5. RETROALIMENTACIÓN (opcional, futuro)
   └─> Docente puede marcar recomendaciones como útiles/no útiles
   └─> Sistema ajusta priorización (sin modificar recomendaciones existentes)
```

### Diagrama de Arquitectura

```
┌─────────────────┐
│   Docente       │
│   (API Client)  │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼─────────────────────────────────────┐
│         Backend FastAPI                      │
│  ┌──────────────────────────────────────┐   │
│  │  Routers:                             │   │
│  │  - /eventos (registro)                │   │
│  │  - /aulas (gestión)                   │   │
│  │  - /recomendaciones (consulta)        │   │
│  └──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────┐   │
│  │  Servicios:                           │   │
│  │  - EventoService                      │   │
│  │  - RecomendacionService               │   │
│  │  - AnalisisPatronesService            │   │
│  └──────────────────────────────────────┘   │
└────────┬─────────────────────────────────────┘
         │
         ├──────────────────┬──────────────────┐
         │                  │                  │
┌────────▼────────┐  ┌──────▼──────┐  ┌───────▼──────┐
│  PostgreSQL     │  │  Vector DB  │  │  LangGraph   │
│  (Eventos,      │  │  (FAISS/    │  │  (Orquestación│
│   Aulas,        │  │   Chroma)   │  │   IA)        │
│   Recomend.)    │  │             │  │              │
└─────────────────┘  └─────────────┘  └──────────────┘
```

## Protección de Datos y Privacidad

- **Anonimización completa**: Todos los eventos son anonimizados desde el registro
- **Aislamiento por aula**: Cada aula es una unidad independiente, sin compartición de datos
- **Minimización de datos**: Solo se recopila lo estrictamente necesario para el análisis de patrones
- **Control docente**: El docente tiene control total sobre qué eventos registrar y qué recomendaciones consultar
- **Cumplimiento RGPD**: Transparencia, minimización, limitación de propósito y control humano

## Uso en el Aula

1. El docente registra eventos pedagógicos anonimizados cuando ocurren o se planifican
2. El sistema procesa eventos históricos periódicamente para identificar patrones
3. El docente solicita recomendaciones bajo demanda cuando las necesita
4. El docente aplica las recomendaciones que considere apropiadas
5. El docente puede generar resúmenes interpretados para las familias
6. Los patrones se acumulan y ajustan gradualmente, manteniendo historial del aula sin identificar alumnos

## Beneficios Sociales

- Mejora la calidad educativa de aulas TEA y su integración
- Facilita decisiones pedagógicas basadas en datos, respetando autonomía docente
- Proporciona información útil a familias sin comprometer la privacidad
- Escalable: de un piloto a cientos de aulas, manteniendo costes controlados
- Cada aula aprende de su propia experiencia histórica

## Roadmap Inicial

### Fase 1: Fundamentos (Semana 1-2)
- Estructura de base de datos (PostgreSQL)
- Backend FastAPI con endpoints básicos
- Modelos de datos (Evento, Aula, Recomendación)
- Validación de esquemas

### Fase 2: Análisis de Patrones (Semana 3-4)
- Integración de embeddings semánticos
- Vector DB (FAISS o Chroma)
- Servicio de análisis de patrones
- Detección de correlaciones temporales

### Fase 3: Recomendaciones (Semana 5-6)
- Integración de LangGraph para orquestación IA
- Generación de recomendaciones basadas en patrones
- Sistema de priorización y confianza
- Endpoints de consulta bajo demanda

### Fase 4: Validación y Despliegue (Semana 7-8)
- Sistema de feedback del docente
- Contenedores Docker
- Despliegue en nube
- Prueba piloto con datos reales (anonimizados)

## Limitaciones Actuales

- No diagnostica ni sustituye decisiones pedagógicas
- No usa sensores biométricos ni identifica alumnos individuales
- Requiere supervisión humana constante para validar recomendaciones
- Las recomendaciones son sugerencias, no prescripciones
- El sistema aprende de patrones históricos, no de literatura clínica

## Contribuciones y Contacto

Este proyecto está en desarrollo activo. Para contribuciones o consultas, contactar con el equipo de desarrollo.

---

**Nota importante**: Este sistema está diseñado como herramienta de apoyo pedagógico, no como sistema de diagnóstico o evaluación clínica. Todas las decisiones finales recaen en el profesional docente.
