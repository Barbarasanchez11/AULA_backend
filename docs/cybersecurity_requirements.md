# Requisitos de Ciberseguridad - AULA+

## Resumen Ejecutivo

Este documento describe los requisitos de ciberseguridad para AULA+, con especial énfasis en la protección de datos personales (PII) y la prevención de que información sensible llegue a servidores de LLMs externos.

---

## Principio Fundamental

**Los datos originales (incluso potencialmente anonimizados) NUNCA deben llegar a servidores de LLMs externos.**

---

## Puntos de Entrada de Datos

### 1. Endpoint `POST /events/`
**Campos a validar:**
- `description` (String, 10-500 caracteres)
- `additional_supports` (String opcional, hasta 200 caracteres)
- `observations` (String opcional, hasta 1000 caracteres)

**Riesgo**: Estos campos son texto libre y podrían contener:
- Nombres propios de menores
- Iniciales
- DNI o números de identificación
- Fechas de nacimiento
- Descripciones físicas detalladas
- Información médica

### 2. Endpoint `PUT /events/{id}`
**Mismos campos que POST**, pero en actualización parcial.

### 3. Generación de Embeddings (Futuro)
**Riesgo**: Antes de generar embeddings, el texto debe estar completamente anonimizado.

### 4. Envío a LLMs (Futuro, con LangGraph)
**Riesgo crítico**: Los datos NO deben enviarse a servidores de LLMs sin anonimización previa.

---

## PII Scanner - Requisitos

### Funcionalidad Requerida

1. **Detección de PII en texto**
   - Nombres propios (patrones en español)
   - Iniciales seguidas de punto (ej: "J.P.")
   - DNI/NIE (formato español: 8 dígitos + letra)
   - Fechas de nacimiento
   - Direcciones
   - Números de teléfono
   - Emails

2. **Validación en tiempo real**
   - Validar antes de almacenar en base de datos
   - Validar antes de generar embeddings
   - Validar antes de enviar a LLMs

3. **Logging y auditoría**
   - Registrar intentos de inserción con PII detectado
   - No almacenar el texto original con PII
   - Alertar al administrador (futuro)

### Herramientas Sugeridas

1. **Presidio** (Microsoft)
   - Biblioteca Python para detección y anonimización de PII
   - Soporta múltiples idiomas (incluido español)
   - Modelos pre-entrenados disponibles
   - URL: https://github.com/microsoft/presidio

2. **spaCy con NER**
   - Modelos NER en español (`es_core_news_lg`)
   - Detección de entidades nombradas
   - Customizable

3. **Validación custom con regex**
   - Patrones específicos para nombres españoles
   - Detección de DNI/NIE
   - Validación de fechas

### Implementación Propuesta

```python
# app/services/pii_scanner.py (estructura propuesta)

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class PIIScanner:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
    
    def detect_pii(self, text: str) -> List[Dict]:
        """Detecta PII en el texto sin modificarlo"""
        results = self.analyzer.analyze(
            text=text,
            language='es',
            entities=['PERSON', 'EMAIL_ADDRESS', 'PHONE_NUMBER', 'LOCATION']
        )
        return results
    
    def anonymize(self, text: str) -> str:
        """Anonimiza el texto reemplazando PII con placeholders"""
        results = self.detect_pii(text)
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results
        )
        return anonymized.text
    
    def validate_no_pii(self, text: str) -> bool:
        """Valida que el texto no contenga PII. Lanza excepción si encuentra."""
        results = self.detect_pii(text)
        if results:
            raise ValueError(f"PII detectado en el texto: {[r.entity_type for r in results]}")
        return True
```

---

## MCP (Model Context Protocol) - Requisitos

### Cuándo Implementar

- Cuando se integren agentes de IA (LangGraph)
- Cuando se envíen datos a LLMs externos
- Cuando se procesen recomendaciones con modelos generativos

### Propósito

Garantizar que **solo datos completamente anonimizados** lleguen a los servidores de LLMs, y que el contexto enviado no contenga información que pueda quedar almacenada en los servidores externos.

### Flujo Propuesto

```
┌─────────────────┐
│  Evento llega   │
│  (POST /events) │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  PII Scanner        │
│  Detecta PII        │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Agente de          │
│  Anonimización      │
│  (MCP)              │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Texto Anonimizado  │
│  (sin PII)          │
└────────┬────────────┘
         │
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Embeddings  │  │  Vector DB   │  │  LLM (solo   │
│  (local)     │  │  (local)     │  │   contexto   │
│              │  │              │  │   anonimizado│
└──────────────┘  └──────────────┘  └──────────────┘
```

### Requisitos de MCP

1. **Validación de contexto antes de envío**
   - Escanear todo el contexto que se enviará al LLM
   - Asegurar que no hay PII
   - Rechazar envío si se detecta PII

2. **Logging de interacciones**
   - Registrar qué contexto se envió (anonimizado)
   - Registrar respuesta del LLM
   - No almacenar datos originales en logs

3. **Aislamiento de datos**
   - Los datos originales nunca salen del servidor local
   - Solo embeddings y texto anonimizado se procesan externamente

---

## Agentes de Anonimización

### Responsabilidad

Procesar y anonimizar cualquier texto antes de:
- Generar embeddings
- Enviar a LLMs
- Almacenar en Vector DB
- Cualquier procesamiento con IA

### Estrategia de Anonimización

1. **Nombres propios**
   - Detectar: "Juan", "María", "Pedro", etc.
   - Reemplazar con: `[ESTUDIANTE_1]`, `[ESTUDIANTE_2]`, etc.
   - Mantener consistencia: mismo nombre → mismo placeholder

2. **DNI/NIE**
   - Detectar: `12345678A`, `X1234567L`
   - Reemplazar con: `[ID_1]`, `[ID_2]`, etc.

3. **Fechas de nacimiento**
   - Detectar: "nació el 15/03/2015"
   - Reemplazar con: `[FECHA_NACIMIENTO]`

4. **Direcciones**
   - Detectar: "Calle Mayor 5"
   - Reemplazar con: `[DIRECCION]`

5. **Mantener estructura semántica**
   - El texto anonimizado debe mantener el significado
   - Los embeddings deben ser útiles a pesar de la anonimización
   - Ejemplo:
     - Original: "Juan tuvo dificultades en la transición"
     - Anonimizado: "[ESTUDIANTE_1] tuvo dificultades en la transición"
     - ✅ Mantiene el significado semántico

### Implementación Propuesta

```python
# app/agents/anonymization_agent.py (estructura propuesta)

class AnonymizationAgent:
    def __init__(self, pii_scanner: PIIScanner):
        self.pii_scanner = pii_scanner
        self.entity_mapping = {}  # Mapeo de entidades a placeholders
    
    def anonymize_event(self, event: Event) -> Event:
        """Anonimiza todos los campos de texto de un evento"""
        anonymized = event.copy()
        
        # Anonimizar description
        anonymized.description = self.anonymize_text(event.description)
        
        # Anonimizar additional_supports si existe
        if event.additional_supports:
            anonymized.additional_supports = self.anonymize_text(event.additional_supports)
        
        # Anonimizar observations si existe
        if event.observations:
            anonymized.observations = self.anonymize_text(event.observations)
        
        return anonymized
    
    def anonymize_text(self, text: str) -> str:
        """Anonimiza un texto manteniendo estructura semántica"""
        # Usar PII scanner para detectar
        # Reemplazar con placeholders consistentes
        # Retornar texto anonimizado
        pass
```

---

## Protección de Servidores LLM

### Principios

1. **Anonimización obligatoria**
   - Todo texto que vaya a un LLM debe estar anonimizado
   - Validación automática antes de cada llamada

2. **Sin datos originales**
   - Los datos originales nunca salen del servidor
   - Solo se procesan embeddings y texto anonimizado

3. **Logging seguro**
   - No almacenar datos originales en logs
   - Solo registrar metadatos (tipo de evento, timestamps, etc.)

4. **Aislamiento por aula**
   - Los datos de un aula no deben mezclarse con otros
   - Los embeddings se generan por aula

### Validación en Cada Punto

```python
# Pseudocódigo de validación

def send_to_llm(context: str, event_data: Dict):
    # 1. Anonimizar contexto
    anonymized_context = anonymization_agent.anonymize_text(context)
    
    # 2. Validar que no hay PII
    pii_scanner.validate_no_pii(anonymized_context)
    
    # 3. Enviar a LLM (solo contexto anonimizado)
    response = llm_client.generate(anonymized_context)
    
    # 4. Logging (sin datos originales)
    log_interaction(
        event_type=event_data['event_type'],
        timestamp=event_data['timestamp'],
        # NO incluir description, observations, etc.
    )
    
    return response
```

---

## Checklist de Implementación

### Fase 1: PII Scanner (Prioridad Alta)
- [ ] Instalar y configurar Presidio o herramienta equivalente
- [ ] Implementar `PIIScanner` en `app/services/pii_scanner.py`
- [ ] Integrar validación en `POST /events/`
- [ ] Integrar validación en `PUT /events/{id}`
- [ ] Probar con ejemplos de texto con y sin PII
- [ ] Documentar uso y configuración

### Fase 2: Anonimización (Prioridad Media)
- [ ] Implementar `AnonymizationAgent` en `app/agents/anonymization_agent.py`
- [ ] Integrar anonimización antes de generar embeddings
- [ ] Probar que los embeddings funcionan con texto anonimizado
- [ ] Documentar estrategia de anonimización

### Fase 3: MCP y Protección LLM (Prioridad Baja, Futuro)
- [ ] Implementar validación de contexto antes de envío a LLM
- [ ] Integrar MCP cuando se implemente LangGraph
- [ ] Implementar logging seguro de interacciones
- [ ] Probar que no hay fuga de datos a servidores externos

---

## Coordinación con Equipo

### Responsabilidades

- **Compañero de ciberseguridad**:
  - Implementar PII Scanner
  - Implementar MCP cuando haya agentes
  - Validar que no hay fuga de datos

- **Equipo de desarrollo**:
  - Proporcionar puntos de entrada de datos
  - Integrar validaciones en endpoints
  - Probar que los embeddings funcionan con texto anonimizado

### Puntos de Integración

1. **Endpoints de eventos**
   - Validación antes de almacenar
   - Anonimización antes de procesar

2. **Servicio de embeddings**
   - Anonimización antes de generar embeddings
   - Validación de que no hay PII

3. **Servicio de recomendaciones** (futuro)
   - Validación antes de enviar a LLM
   - Logging seguro

---

## Referencias

- [Presidio - Microsoft](https://github.com/microsoft/presidio)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [RGPD - Protección de Datos](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32016R0679)
- [OWASP Top 10 - Privacy Risks](https://owasp.org/www-project-top-ten/)

---

**Última actualización**: 5 de febrero de 2026  
**Responsable**: Equipo de ciberseguridad + Equipo de desarrollo  
**Estado**: Pendiente de implementación

