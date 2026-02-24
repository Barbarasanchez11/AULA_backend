# Arquitectura de Agentes: Sistema de Recomendaciones LangGraph

Este documento detalla la implementación del sistema de agentes inteligentes basado en **LangGraph** para AULA+. El objetivo de este sistema es transformar datos crudos de eventos pedagógicos en recomendaciones accionables integrando memoria histórica y análisis de patrones.

---

## 1. Visión General
El sistema utiliza una arquitectura de **Grafo de Estado (StateGraph)**. A diferencia de un flujo secuencial simple, LangGraph permite gestionar un estado compartido que evoluciona a medida que pasa por diferentes nodos especializados (agentes).

### Componentes Tecnológicos
- **Orquestador**: LangGraph
- **LLM**: Llama 3.1 (via ChatGroq)
- **Base de Datos Vectorial**: ChromaDB (para memoria semántica)
- **Lógica de Patrones**: Scikit-learn (DBSCAN para clustering)

---

## 2. El Estado del Grafo (`RecommendationState`)
Es la "memoria de trabajo" que viaja entre los agentes. Se define como un `TypedDict` con las siguientes secciones:

- **Inputs**: `classroom_id`, `event_id`, `event_data`.
- **Contexto**: `similar_events` (histórico), `patterns` (tendencias), `context_for_llm` (prompt fragment).
- **IA**: `llm_response`, `llm_metadata` (tokens, duración).
- **Output Final**: `recommendation` (objeto validado), `confidence` (ALTA/MEDIA/BAJA).
- **Control**: `errors` (lista de fallos por nodo) y `metadata`.

---

## 3. Flujo de Trabajo (Los 4 Nodos)

### Nodo 1: `receive_event` (El Validador)
**Responsabilidad**: Garantizar que los datos de entrada son íntegros antes de gastar recursos de IA.
- Verifica la existencia del aula en PostgreSQL.
- Si recibe un `event_id`, recupera el evento de la DB.
- Si recibe `event_data` manual, lo valida mediante esquemas de Pydantic.
- **Salida**: Estado con datos de evento limpios.

### Nodo 2: `search_context` (El Bibliotecario)
**Responsabilidad**: Enriquecer la petición con "experiencia del aula". Utiliza el `ContextService` para:
1.  **Búsqueda Semántica**: Encuentra los 5 eventos más similares en ChromaDB usando embeddings de calidad (`mpnet`).
2.  **Análisis de Patrones**: Consulta tendencias temporales (ej: "los lunes son críticos") y efectividad de apoyos (ej: "el pictograma tiene 90% de éxito").
3.  **Construcción de Contexto**: Genera un resumen en lenguaje natural para la IA.

### Nodo 3: `generate_llm` (El Consultor Experto)
**Responsabilidad**: Razonamiento y generación.
- **Configuración**: Usa Llama 3 con una temperatura de 0.7 para permitir creatividad pedagógica dentro de límites profesionales.
- **Prompt System**: Configurado como un "Experto en TEA", con instrucciones de ser breve, empático y responder obligatoriamente en español.
- **Proceso**: Combina el evento actual con el contexto histórico para generar una recomendación única.

### Nodo 4: `validate_format` (El Auditor)
**Responsabilidad**: Control de calidad y persistencia.
- Estructura la respuesta de la IA en los campos del esquema oficial.
- **Cálculo de Confianza**: Ejecuta una fórmula lógica basada en la fuerza del patrón (éxito histórico) y el tamaño de la muestra (eventos encontrados).
- **Salida**: Recomendación final lista para ser presentada al usuario.

---

## 4. Servicios Internos de Soporte

### `ContextService` & `ContextSearcher`
Actúan como la capa de abstracción para que los nodos no hablen directamente con las bases de datos. El `ContextSearcher` se encarga de la lógica vectorial, mientras que el `ContextService` orquesta la unión entre vectores y patrones estadísticos.

### `PatternAnalysisService`
El cerebro analítico. No usa IA sino estadística avanzada:
- **Clustering**: Agrupa eventos similares para detectar comportamientos recurrentes.
- **Efectividad**: Mide matemáticamente qué apoyos funcionan mejor en situaciones específicas.

---

## 5. Guía de Ejecución y Pruebas
Para testear el flujo completo de los agentes sin pasar por la API:

1.  **Asegurar entorno Docker**: Los agentes necesitan acceso a Postgres y ChromaDB.
2.  **Ejecutar script de validación**:
    ```bash
    docker compose exec web python3 scripts/test_langgraph_full.py
    ```

Este script simula un evento, lo pasa por el grafo y muestra en consola el razonamiento de la IA y el objeto final generado.

---

## 6. Consideraciones para el Equipo
- **Asincronía**: Los nodos de LangGraph son síncronos por diseño del grafo, pero llaman a servicios asíncronos de DB usando la utilidad `run_async`.
- **Evolución**: Para añadir nuevas reglas, basta con modificar el `system_prompt` en `node_generate_llm.py` o añadir un nodo de validación extra en `graph.py`.
- **Privacidad**: El sistema está diseñado para trabajar con datos anonimizados; no se envían nombres ni DNI a los servicios de LLM externos (Groq).
