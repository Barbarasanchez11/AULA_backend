# Protección de Datos y Privacidad - AULA+

## Resumen Ejecutivo

AULA+ está diseñado desde el principio con **privacidad por diseño** (Privacy by Design). El sistema **NO recopila, almacena ni procesa datos personales de menores**. Todos los datos son anonimizados y agregados a nivel de aula.

---

## Análisis de Campos por Modelo

### 1. Modelo `Classroom` (Aula)

| Campo | Tipo | ¿Identifica menores? | Observaciones |
|-------|------|---------------------|---------------|
| `id` | UUID | ❌ NO | Identificador único del aula, no de personas |
| `name` | String(100) | ❌ NO | Nombre del aula (ej: "Aula TEA 1"), no nombres de menores |
| `type` | String(50) | ❌ NO | Tipo de aula (ej: "TEA"), no identifica menores |
| `extra_metadata` | JSON | ⚠️ RIESGO POTENCIAL | Campo flexible que podría usarse incorrectamente |
| `created_at` | DateTime | ❌ NO | Fecha de creación del aula, no identifica menores |

**⚠️ Medidas de protección para `extra_metadata`:**
- Este campo está destinado únicamente a metadatos técnicos del aula (ej: número de plazas, recursos disponibles)
- **NO debe contener**: nombres de menores, DNI, fechas de nacimiento, información médica
- Se recomienda validar el contenido en futuras versiones o restringir su uso

---

### 2. Modelo `Event` (Evento)

| Campo | Tipo | ¿Identifica menores? | Observaciones |
|-------|------|---------------------|---------------|
| `id` | UUID | ❌ NO | Identificador único del evento |
| `classroom_id` | UUID | ❌ NO | Referencia al aula, no a menores |
| `event_type` | String(50) | ❌ NO | Tipo de evento (TRANSICION, CAMBIO_DE_RUTINA, etc.) |
| `description` | String(500) | ⚠️ RIESGO POTENCIAL | Texto libre que podría contener nombres si el docente no sigue las guías |
| `moment_of_day` | String(20) | ❌ NO | Momento del día (mañana, mediodía, tarde) |
| `day_of_week` | String(20) | ❌ NO | Día de la semana (opcional) |
| `duration_minutes` | Integer | ❌ NO | Duración en minutos |
| `supports` | JSON | ❌ NO | Lista predefinida de apoyos utilizados |
| `additional_supports` | Text | ⚠️ RIESGO POTENCIAL | Texto libre que podría contener información identificativa |
| `result` | String(50) | ❌ NO | Resultado del evento (EXITOSO, PARCIAL, DIFICULTAD) |
| `observations` | Text | ⚠️ RIESGO POTENCIAL | Texto libre que podría contener nombres o información identificativa |
| `timestamp` | DateTime | ❌ NO | Fecha y hora del evento (no identifica menores) |

**⚠️ Medidas de protección para campos de texto libre:**
- `description`, `additional_supports`, `observations` son campos de texto libre
- **NO deben contener**: nombres de menores, iniciales, apodos, descripciones físicas detalladas, información médica
- **Deben contener**: descripciones objetivas y anonimizadas de situaciones pedagógicas
- Se recomienda implementar validación automática en futuras versiones (detección de patrones de nombres)

**Ejemplos de uso correcto:**
- ✅ "Transición de juego libre a asamblea matutina. El grupo respondió positivamente a la anticipación visual."
- ❌ "Juan tuvo dificultades en la transición..." (contiene nombre)

---

### 3. Modelo `Recommendation` (Recomendación)

| Campo | Tipo | ¿Identifica menores? | Observaciones |
|-------|------|---------------------|---------------|
| `id` | UUID | ❌ NO | Identificador único de la recomendación |
| `classroom_id` | UUID | ❌ NO | Referencia al aula, no a menores |
| `recommendation_type` | String(50) | ❌ NO | Tipo de recomendación (ANTICIPACION, ESTRATEGIA, ADAPTACION) |
| `title` | String(200) | ❌ NO | Título de la recomendación |
| `description` | Text | ❌ NO | Descripción de la recomendación (genérica, no identifica menores) |
| `applicable_context` | Text | ❌ NO | Contexto de aplicación (genérico) |
| `detected_pattern` | Text | ❌ NO | Patrón detectado (agregado, no identifica menores) |
| `confidence` | String(20) | ❌ NO | Nivel de confianza (ALTA, MEDIA, BAJA) |
| `generated_at` | DateTime | ❌ NO | Fecha de generación |

**✅ Este modelo es seguro:** Todos los campos son genéricos y no pueden identificar menores.

---

## Medidas de Protección Implementadas

### 1. **Anonimización por Diseño**
- No hay campos específicos para nombres, DNI, fechas de nacimiento, o cualquier identificador personal
- Los eventos se registran a nivel de aula, no de individuo
- Los timestamps son genéricos (momento del día, no hora exacta)

### 2. **Aislamiento por Aula**
- Cada aula tiene su propio conjunto de eventos y recomendaciones
- No hay relaciones cruzadas entre aulas que permitan identificar menores
- Los datos están aislados por `classroom_id`

### 3. **Validación de Esquemas (Pydantic)**
- Validación de tipos de datos en todos los endpoints
- Longitud máxima de campos de texto para prevenir datos excesivos
- Validación de enums para campos predefinidos

### 4. **Sin Biometría**
- El sistema explícitamente NO usa:
  - Cámaras
  - Sensores de audio
  - Sensores biométricos
  - Cualquier tecnología de reconocimiento

### 5. **Sin Diagnóstico Clínico**
- El sistema NO genera diagnósticos
- NO evalúa menores individualmente
- NO sustituye evaluaciones profesionales
- Solo proporciona recomendaciones pedagógicas basadas en patrones agregados

---

## Medidas de Protección Recomendadas (Futuras)

### 1. **Validación Automática de Texto Libre**
Implementar validación que detecte y rechace:
- Patrones de nombres propios (mayúsculas seguidas de minúsculas)
- Iniciales seguidas de punto (ej: "J.P.")
- Números de identificación (DNI, pasaporte)
- Fechas de nacimiento

**Ejemplo de implementación futura:**
```python
def validate_no_personal_data(text: str) -> bool:
    """Valida que el texto no contenga datos personales"""
    # Detectar patrones de nombres
    name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    # Detectar iniciales
    initial_pattern = r'\b[A-Z]\.\s*[A-Z]\.'
    # Detectar DNI
    dni_pattern = r'\d{8}[A-Z]'
    
    if re.search(name_pattern, text) or re.search(initial_pattern, text) or re.search(dni_pattern, text):
        raise ValueError("El texto no puede contener datos personales")
    return True
```

### 2. **Política de Retención de Datos**
- Definir períodos de retención para eventos y recomendaciones
- Implementar eliminación automática de datos antiguos
- Documentar procedimientos de eliminación segura

### 3. **Auditoría de Accesos**
- Registrar quién accede a qué datos y cuándo
- Implementar logs de auditoría para cumplimiento RGPD
- Restringir accesos por roles (docente, administrador, etc.)

### 4. **Cifrado de Datos**
- Cifrado en tránsito (HTTPS/TLS)
- Cifrado en reposo (base de datos)
- Gestión segura de credenciales

### 5. **Restricción de `extra_metadata`**
- Definir esquema JSON estricto para `extra_metadata` en `Classroom`
- Validar que solo contenga campos técnicos permitidos
- Eliminar el campo si no es necesario

---

## Cumplimiento RGPD

### Principios Aplicados

1. **Minimización de Datos**: Solo se recopilan datos estrictamente necesarios para el propósito pedagógico
2. **Limitación de Propósito**: Los datos solo se usan para generar recomendaciones pedagógicas
3. **Limitación de Almacenamiento**: Los datos se mantienen solo mientras sean necesarios (definir política)
4. **Integridad y Confidencialidad**: Datos aislados por aula, sin acceso cruzado
5. **Transparencia**: Este documento explica qué datos se recopilan y cómo se usan

### Derechos de los Interesados

Aunque el sistema NO recopila datos personales directos, los docentes y centros educativos tienen derecho a:
- **Acceso**: Ver qué datos se almacenan sobre su aula
- **Rectificación**: Corregir eventos o recomendaciones incorrectas
- **Supresión**: Eliminar aulas y todos sus datos asociados (cascade delete)
- **Portabilidad**: Exportar datos del aula en formato estándar (futuro)

---

## Checklist de Verificación

### ✅ Campos que NO identifican menores
- [x] IDs (UUIDs)
- [x] Tipos de eventos (enums)
- [x] Momentos del día
- [x] Días de la semana
- [x] Duración en minutos
- [x] Tipos de apoyos (lista predefinida)
- [x] Resultados de eventos (enums)
- [x] Tipos de recomendaciones (enums)
- [x] Niveles de confianza (enums)
- [x] Timestamps genéricos

### ⚠️ Campos que requieren atención
- [ ] `description` (Event) - Texto libre, requiere guías de uso
- [ ] `additional_supports` (Event) - Texto libre, requiere guías de uso
- [ ] `observations` (Event) - Texto libre, requiere guías de uso
- [ ] `extra_metadata` (Classroom) - JSON flexible, requiere restricción

### ✅ Medidas implementadas
- [x] Sin campos de datos personales explícitos
- [x] Aislamiento por aula
- [x] Validación de esquemas (Pydantic)
- [x] Sin biometría
- [x] Sin diagnóstico clínico

### 🔄 Medidas recomendadas (futuro)
- [ ] Validación automática de texto libre (PII Scanner) - Ver [Requisitos de Ciberseguridad](./cybersecurity_requirements.md)
- [ ] Política de retención de datos
- [ ] Auditoría de accesos
- [ ] Cifrado de datos
- [ ] Restricción de `extra_metadata`
- [ ] Agentes de anonimización (MCP) - Ver [Requisitos de Ciberseguridad](./cybersecurity_requirements.md)

---

## Conclusión

**El sistema AULA+ está diseñado para NO recopilar datos personales de menores.** Todos los modelos y schemas han sido revisados y verificados. Los únicos riesgos potenciales provienen de campos de texto libre que podrían ser mal utilizados por los docentes, pero estos riesgos se mitigan mediante:

1. **Guías de uso claras** para los docentes
2. **Validación automática futura** de patrones de datos personales
3. **Aislamiento por aula** que previene identificación cruzada
4. **Diseño explícito** que no incluye campos para datos personales

**El sistema cumple con los principios de privacidad por diseño y minimización de datos del RGPD.**

---

## Referencias

- [RGPD - Reglamento General de Protección de Datos](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32016R0679)
- [Privacy by Design - 7 Principios Fundamentales](https://www.ipc.on.ca/wp-content/uploads/Resources/7foundationalprinciples.pdf)
- [LOPD-GDD - Ley Orgánica de Protección de Datos](https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673)

---

**Última actualización**: 5 de febrero de 2026  
**Versión del documento**: 1.0  
**Responsable**: Equipo de desarrollo AULA+

