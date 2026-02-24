# Integración con Raíces (Madrid) y Séneca (Andalucía)

## 1. Por qué NO reemplazamos estos sistemas

**AULA+ es un complemento de IA, no un reemplazo.**

- **Raíces y Séneca** son sistemas administrativos y de gestión completos que los docentes ya conocen y usan diariamente.
- **AULA+** añade una capa de inteligencia artificial que analiza los datos que ya existen en estos sistemas.
- **No requiere cambiar** el flujo de trabajo del docente: sigue usando Raíces/Séneca como siempre.
- **Añade valor** sin complicar: las recomendaciones aparecen donde el docente ya trabaja.

**Principio clave:** Integración, no sustitución. Trabajamos con lo que ya existe.

---

## 2. Cómo obtenemos los datos

### Opción A: Exportación CSV (Implementación inicial)

**Flujo:**
1. El docente exporta eventos desde Raíces/Séneca en formato CSV.
2. El CSV contiene: tipo de evento, descripción, momento del día, apoyos usados, resultado, observaciones.
3. AULA+ importa el CSV mediante un script o interfaz web.
4. El sistema procesa, normaliza y genera embeddings.

**Ejemplo de CSV desde Raíces:**
```csv
fecha,evento_tipo,descripcion,momento_dia,apoyos,resultado,observaciones
2024-02-10,TRANSICION,Transición de patio a aula,mediodia,"Anticipación visual;Mediación verbal",EXITOSO,Funcionó bien con pictogramas
2024-02-10,APRENDIZAJE,Actividad de comunicación,tarde,"Panel pictogramas;Apoyo individual",PARCIAL,Algunos estudiantes necesitaron más tiempo
```

**Ventajas:**
- ✅ Implementación rápida
- ✅ No requiere cambios en Raíces/Séneca
- ✅ El docente controla qué datos exporta
- ✅ Compatible con privacidad (datos anonimizados)

### Opción B: API REST (Implementación futura)

**Flujo:**
1. Raíces/Séneca expone un endpoint API para eventos anonimizados.
2. AULA+ consume la API periódicamente (ej: cada noche).
3. Sincronización automática de nuevos eventos.
4. Webhook opcional para actualizaciones en tiempo real.

**Ejemplo de API desde Raíces:**
```http
GET /api/v1/events?classroom_id=123&start_date=2024-02-01&end_date=2024-02-10
Authorization: Bearer <token>

Response:
{
  "events": [
    {
      "id": "evt_001",
      "event_type": "TRANSICION",
      "description": "Transición de patio a aula",
      "moment_of_day": "mediodia",
      "supports": ["Anticipación visual", "Mediación verbal"],
      "result": "EXITOSO",
      "observations": "Funcionó bien con pictogramas",
      "timestamp": "2024-02-10T12:30:00Z"
    }
  ]
}
```

**Ventajas:**
- ✅ Automatización completa
- ✅ Datos siempre actualizados
- ✅ Integración transparente para el docente

---

## 3. Cómo devolvemos las recomendaciones

### Opción A: Widget embebido (Recomendado)

**Flujo:**
1. AULA+ expone un endpoint API REST con recomendaciones.
2. Raíces/Séneca muestra un widget (iframe o componente) en su interfaz.
3. El widget consume la API de AULA+ y muestra recomendaciones en tiempo real.
4. El docente ve las recomendaciones directamente en Raíces/Séneca.

**Ejemplo de API de AULA+:**
```http
GET /api/v1/recommendations?classroom_id=123
Authorization: Bearer <token>

Response:
{
  "recommendations": [
    {
      "id": "rec_001",
      "title": "Priorizar uso de Anticipación visual",
      "description": "El apoyo 'Anticipación visual' ha mostrado 71% de éxito...",
      "confidence": "ALTA",
      "detected_pattern": "Análisis de 59 eventos muestra alta efectividad...",
      "applicable_context": "Considerar en situaciones similares, especialmente por la tarde"
    }
  ]
}
```

**Ejemplo de widget en Raíces:**
```html
<!-- Widget embebido en la interfaz de Raíces -->
<div id="aula-plus-recommendations">
  <h3>💡 Recomendaciones IA</h3>
  <div class="recommendation-card">
    <h4>Priorizar uso de Anticipación visual</h4>
    <p>El apoyo 'Anticipación visual' ha mostrado 71% de éxito...</p>
    <span class="confidence-badge alta">Confianza: ALTA</span>
  </div>
</div>
```

### Opción B: API REST para integración completa

**Flujo:**
1. Raíces/Séneca consume la API de AULA+ directamente.
2. Integra las recomendaciones en su propio sistema de notificaciones.
3. Puede combinar recomendaciones con otras funcionalidades (alertas, recordatorios).

**Ventajas:**
- ✅ Integración nativa en la interfaz existente
- ✅ El docente no sale de su sistema habitual
- ✅ Experiencia de usuario fluida

---

## 4. Diagrama de arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMAS EXISTENTES                           │
│                                                                   │
│  ┌──────────────┐              ┌──────────────┐                 │
│  │   RAÍCES     │              │   SÉNECA     │                 │
│  │   (Madrid)   │              │  (Andalucía) │                 │
│  └──────┬───────┘              └──────┬───────┘                 │
│         │                              │                          │
│         │  Exporta CSV / API           │                          │
│         │  (eventos anonimizados)      │                          │
│         └──────────────┬───────────────┘                          │
└────────────────────────┼─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AULA+ (Sistema IA)                           │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Importación y Normalización                              │  │
│  │  - Valida formato CSV/API                                 │  │
│  │  - Normaliza textos                                       │  │
│  │  - Valida PII (sin datos personales)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Generación de Embeddings                                │  │
│  │  - Modelo: mpnet (calidad) / distiluse (velocidad)       │  │
│  │  - Almacenamiento: ChromaDB (vector database)             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Análisis de Patrones                                    │  │
│  │  - Clustering semántico (DBSCAN)                         │  │
│  │  - Patrones temporales                                    │  │
│  │  - Efectividad de apoyos                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Generación de Recomendaciones                           │  │
│  │  - Basadas en patrones detectados                         │  │
│  │  - Con nivel de confianza                                │  │
│  │  - Explicables (muestra el patrón detectado)             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API REST de Recomendaciones                             │  │
│  │  GET /api/v1/recommendations?classroom_id=123            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │  API REST / Widget
                          │  (recomendaciones)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMAS EXISTENTES                           │
│                                                                   │
│  ┌──────────────┐              ┌──────────────┐                 │
│  │   RAÍCES     │              │   SÉNECA     │                 │
│  │   (Madrid)   │              │  (Andalucía) │                 │
│  │              │              │              │                 │
│  │  [Widget]    │              │  [Widget]    │                 │
│  │  Muestra     │              │  Muestra     │                 │
│  │  recomenda-  │              │  recomenda-  │                 │
│  │  ciones      │              │  ciones      │                 │
│  └──────────────┘              └──────────────┘                 │
│                                                                   │
│  👨‍🏫 El docente ve las recomendaciones en su sistema habitual    │
└─────────────────────────────────────────────────────────────────┘
```

**Flujo de datos:**
1. **Entrada:** Raíces/Séneca → CSV/API → AULA+
2. **Procesamiento:** AULA+ analiza y genera recomendaciones
3. **Salida:** AULA+ → API REST → Widget en Raíces/Séneca
4. **Resultado:** Docente ve recomendaciones en su sistema habitual

---

## 5. Ventajas para docentes que ya usan Raíces/Séneca

### ✅ Sin curva de aprendizaje
- No necesitan aprender un sistema nuevo
- Siguen usando Raíces/Séneca como siempre
- Las recomendaciones aparecen donde ya trabajan

### ✅ Datos que ya tienen
- No necesitan registrar eventos adicionales
- Usan los datos que ya están en Raíces/Séneca
- Exportación simple (un clic)

### ✅ Recomendaciones contextuales
- Basadas en su propio aula
- Aprenden de sus propios datos
- Cada aula tiene su propio modelo

### ✅ Explicables y accionables
- Cada recomendación explica por qué se genera
- Muestra el patrón detectado
- Indica cuándo y cómo aplicarla

### ✅ Privacidad garantizada
- Solo datos anonimizados
- No se almacenan datos personales
- Cumple con RGPD

---

## 6. Ejemplo concreto: Flujo completo Raíces → AULA+ → Raíces

### Paso 1: Docente exporta desde Raíces

**En Raíces:**
```
Menú: "Eventos del aula" → "Exportar" → "CSV"
```

**CSV generado:**
```csv
fecha,evento_tipo,descripcion,momento_dia,apoyos,resultado,observaciones
2024-02-10,TRANSICION,Transición de patio a aula después del recreo,mediodia,"Anticipación visual;Mediación verbal",EXITOSO,La anticipación visual facilitó la transición
2024-02-10,APRENDIZAJE,Actividad de comunicación con panel de pictogramas,tarde,"Panel pictogramas;Apoyo individual",EXITOSO,Se observó mejora en participación
2024-02-11,REGULACION,Momento de sobrecarga sensorial en el aula,mañana,"Pausa sensorial;Adaptación del entorno",PARCIAL,Algunos estudiantes necesitaron más tiempo
```

### Paso 2: AULA+ procesa el CSV

**Script de importación:**
```bash
python scripts/import_events_from_csv.py eventos_raices.csv --classroom-id=123
```

**Procesamiento:**
1. ✅ Valida formato CSV
2. ✅ Normaliza textos (espacios, mayúsculas)
3. ✅ Valida PII (asegura que no hay datos personales)
4. ✅ Genera embeddings semánticos
5. ✅ Almacena en ChromaDB

**Resultado:**
- 3 eventos importados
- 3 embeddings generados
- Listo para análisis

### Paso 3: AULA+ genera recomendaciones

**Análisis automático:**
- Detecta que "Anticipación visual" tiene 100% de éxito en transiciones
- Identifica que "Pausa sensorial + Adaptación del entorno" funciona bien en regulación
- Genera recomendaciones con confianza ALTA

**API de recomendaciones:**
```http
GET https://aula-plus.api/recommendations?classroom_id=123

Response:
{
  "recommendations": [
    {
      "title": "Priorizar uso de Anticipación visual en transiciones",
      "description": "El apoyo 'Anticipación visual' ha mostrado 100% de éxito en transiciones...",
      "confidence": "ALTA",
      "detected_pattern": "Análisis de eventos muestra que todas las transiciones con anticipación visual fueron exitosas",
      "applicable_context": "Usar especialmente en transiciones de patio a aula por la tarde"
    }
  ]
}
```

### Paso 4: Raíces muestra recomendaciones

**Widget en la interfaz de Raíces:**
```html
<!-- Sección de recomendaciones IA en el dashboard del docente -->
<section class="recommendations-panel">
  <h2>💡 Recomendaciones IA para tu aula</h2>
  
  <div class="recommendation-card high-confidence">
    <div class="recommendation-header">
      <h3>Priorizar uso de Anticipación visual en transiciones</h3>
      <span class="confidence-badge alta">Confianza: ALTA</span>
    </div>
    
    <p class="recommendation-description">
      El apoyo 'Anticipación visual' ha mostrado 100% de éxito en transiciones 
      analizadas. Se recomienda considerarlo como opción preferente.
    </p>
    
    <div class="recommendation-pattern">
      <strong>🔍 Por qué se recomienda:</strong>
      <p>Análisis de eventos muestra que todas las transiciones con anticipación 
      visual fueron exitosas. Este patrón sugiere que es una estrategia efectiva.</p>
    </div>
    
    <div class="recommendation-context">
      <strong>💡 Cuándo aplicar:</strong>
      <p>Usar especialmente en transiciones de patio a aula por la tarde. Los datos 
      históricos del aula muestran que este apoyo ha funcionado de manera consistente.</p>
    </div>
  </div>
</section>
```

**Vista del docente en Raíces:**
```
┌─────────────────────────────────────────────────────────┐
│  RAÍCES - Dashboard del Aula                            │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  [Eventos del día]  [Calendario]  [Estudiantes]         │
│                                                           │
│  ┌───────────────────────────────────────────────────┐ │
│  │ 💡 Recomendaciones IA para tu aula                │ │
│  ├───────────────────────────────────────────────────┤ │
│  │                                                    │ │
│  │ 🟢 ALTA CONFIANZA                                 │ │
│  │ Priorizar uso de Anticipación visual...           │ │
│  │                                                    │ │
│  │ [Ver detalles] [Marcar como aplicada]             │ │
│  └───────────────────────────────────────────────────┘ │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Consideraciones técnicas

### Privacidad y seguridad
- ✅ Solo datos anonimizados (sin nombres, DNI, etc.)
- ✅ Validación automática de PII antes de procesar
- ✅ Datos encriptados en tránsito (HTTPS)
- ✅ Cumplimiento RGPD

### Escalabilidad
- ✅ Un sistema AULA+ puede servir múltiples aulas
- ✅ Cada aula tiene su propia base de datos de embeddings
- ✅ Recomendaciones personalizadas por aula

### Mantenimiento
- ✅ Sistema independiente (no afecta a Raíces/Séneca)
- ✅ Actualizaciones sin interrumpir sistemas existentes
- ✅ Monitoreo y logs separados

---

## 8. Plan de implementación

### Fase 1: Prueba de concepto (Actual)
- ✅ Sistema funcional con datos sintéticos
- ✅ API REST operativa
- ✅ Integración CSV funcionando

### Fase 2: Piloto con un centro (Próximo paso)
- Integración con exportación CSV desde Raíces/Séneca
- Validación con datos reales (anonimizados)
- Feedback de docentes

### Fase 3: Integración API (Futuro)
- Desarrollo de API de integración
- Widget embebido en Raíces/Séneca
- Sincronización automática

### Fase 4: Escalado
- Múltiples centros educativos
- Optimizaciones de rendimiento
- Dashboard de administración

---

## Conclusión

**AULA+ se integra con Raíces y Séneca sin reemplazarlos.**

- **Aporta:** Inteligencia artificial y recomendaciones accionables
- **No cambia:** El flujo de trabajo del docente
- **Funciona con:** Los datos que ya existen
- **Se muestra en:** La interfaz que el docente ya usa

**Resultado:** Docentes más apoyados, sin complicaciones adicionales.

