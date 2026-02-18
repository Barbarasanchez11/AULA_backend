# Resumen Ejecutivo - Reunión con Mentora

## Estado Actual

✅ **Fase 1 Completada:**
- Backend FastAPI con 13 endpoints
- PostgreSQL con esquema completo
- Protección de datos verificada
- Documentación técnica completa

⏳ **Fase 2 En Progreso:**
- Análisis de modelos de embeddings completado
- Decisión: Sistema híbrido (distiluse + mpnet)
- Implementación iniciada

---

## Decisión Técnica Clave: Sistema Híbrido

**Dos modelos:**
1. **distiluse** (rápido): Búsquedas, previews → 0.09s/evento
2. **mpnet** (calidad): Clustering, recomendaciones → 0.58s/evento, similitud 0.85

**Justificación:**
- Priorizamos calidad semántica sobre velocidad
- Volumen bajo (5-10 eventos/día)
- La confianza del docente depende de coherencia

---

## Principios de IA y Gobernanza

✅ **IA Responsable:**
- Explicabilidad: Patrones detectados visibles
- Control humano: Recomendaciones bajo demanda
- Transparencia: Decisiones técnicas documentadas

✅ **Privacidad:**
- Anonimización desde el registro
- Aislamiento por aula
- PII Scanner + MCP (coordinado con compañero)

✅ **Validación Progresiva:**
- Nivel 1: Patrones observados (actual)
- Nivel 2: Feedback docente (futuro)
- Nivel 3: Curaduría expertos (futuro)

---

## Próximos Pasos (Esta Semana)

1. Completar servicio de embeddings híbrido
2. Integrar Vector DB (Chroma)
3. Implementar búsqueda semántica
4. Endpoint de búsqueda de eventos similares

---

## Preguntas para la Mentora

1. ¿Estrategia de validación progresiva adecuada?
2. ¿Consideraciones adicionales de gobernanza?
3. ¿Recomendaciones sobre MCP y anonimización?
4. ¿Cómo mejorar explicabilidad de recomendaciones?

---

**Principio rector:** IA responsable, explicable y al servicio del docente.




