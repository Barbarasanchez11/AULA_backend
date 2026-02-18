# Arquitectura: Concepto de ContextService

## 1. ¿Qué es un "Service" en nuestra arquitectura?
En el desarrollo de software moderno (especialmente con FastAPI y LangGraph), un **Service** es una capa intermedia que contiene la "lógica de negocio". Su misión es realizar tareas complejas para que el resto del sistema (como los Nodos de LangGraph) se mantenga limpio y fácil de leer.

## 2. El ContextService: El Cerebro de la Memoria
El **ContextService** es un servicio especializado cuya única misión es **reunir toda la información relevante sobre el pasado** para que la IA tome mejores decisiones en el presente.

En lugar de que el Nodo 2 haga todo el trabajo sucio, el Nodo 2 simplemente dirá: *"Oye, ContextService, aquí tienes este evento. Búscame todo lo que sepas sobre situaciones parecidas"*.

### Responsabilidades del ContextService:
1.  **Búsqueda Vectorial (Similitud):** Se conecta a ChromaDB para encontrar eventos que "semánticamente" se parecen al actual (no solo por palabras, sino por significado).
2.  **Análisis de Patrones:** Consulta el `PatternAnalysisService` para ver si este comportamiento se repite (ej: "Siempre pasa después del recreo" o "Los apoyos visuales siempre funcionan con este tipo de crisis").
3.  **Filtrado de Relevancia:** Descarta información irrelevante o duplicada para no saturar a la IA.
4.  **Generación de Contexto (Context Building):** Toma todos los datos anteriores y los redacta en un formato que la IA entienda perfectamente.

---

## 3. ¿Por qué usar un Service en lugar de meterlo en el Nodo?

| Característica | En el Nodo (Mal) | Con ContextService (Bien) |
| :--- | :--- | :--- |
| **Legibilidad** | El archivo del nodo crece hasta 500+ líneas. | El nodo tiene 50 líneas, el service tiene su propio espacio. |
| **Reutilización** | Si queremos buscar eventos similares en un Dashboard, tendríamos que copiar código. | El Dashboard simplemente llama al `ContextService`. |
| **Testing** | Difícil de testear sin ejecutar todo el Grafo. | Podemos crear tests específicos para el `ContextService` en segundos. |
| **Evolución** | Si cambiamos ChromaDB por otra base de datos, rompemos el Grafo. | Solo cambiamos una línea dentro del `ContextService`. |

---

## 4. Ejemplo del Flujo de Trabajo

1.  **Nodo 1 (Recibe):** *"Tengo un evento de 'Crisis en el comedor'"*.
2.  **Nodo 2 (Nodo Contexto):** Llama a `ContextService.get_full_context(event_data)`.
3.  **ContextService (Trabaja):**
    *   Busca en la memoria: *"Encontré 3 crisis similares el mes pasado"*.
    *   Busca patrones: *"Suele ocurrir cuando hay mucho ruido"*.
    *   Formatea: *"Contexto para IA: El alumno ha tenido 3 crisis similares. Los apoyos visuales funcionaron en 2 de ellas."*
4.  **Nodo 2 (Devuelve):** Guarda ese texto en el `state["context_for_llm"]`.

---

## 5. Conclusión para el Equipo
Usar un **ContextService** es como contratar a un bibliotecario experto. El Nodo (el investigador) no tiene que perder tiempo buscando libros en las estanterías (bases de datos); simplemente le pide la información al bibliotecario (Service) y este le entrega un resumen listo para ser usado.
