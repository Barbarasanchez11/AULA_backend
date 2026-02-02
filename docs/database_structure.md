# Estructura de Base de Datos - AULA+

## Descripción General

La base de datos de AULA+ está diseñada para almacenar eventos pedagógicos anonimizados y recomendaciones generadas por el sistema. Cada aula es una unidad independiente con sus propios eventos y recomendaciones.

**Motor de base de datos:** PostgreSQL 16  
**ORM:** SQLAlchemy (async)  
**Visor recomendado:** Adminer (puerto 8080)

---

## Diagrama de Relaciones

```
┌─────────────────┐
│   classrooms    │
│─────────────────│
│ id (PK)         │
│ name            │
│ type            │
│ extra_metadata  │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         ├──────────────────┬──────────────────┐
         │                  │                  │
         │                  │                  │
┌────────▼────────┐  ┌──────▼──────────┐  ┌───▼──────────────┐
│     events      │  │ recommendations │  │                 │
│─────────────────│  │─────────────────│  │                 │
│ id (PK)         │  │ id (PK)         │  │                 │
│ classroom_id(FK)│  │ classroom_id(FK)│  │                 │
│ event_type      │  │ recommendation_  │  │                 │
│ description     │  │   type          │  │                 │
│ moment_of_day   │  │ title           │  │                 │
│ day_of_week     │  │ description     │  │                 │
│ duration_minutes│  │ applicable_     │  │                 │
│ supports        │  │   context       │  │                 │
│ additional_      │  │ detected_pattern│  │                 │
│   supports      │  │ confidence      │  │                 │
│ result          │  │ generated_at    │  │                 │
│ observations    │  │                 │  │                 │
│ timestamp       │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Tabla: `classrooms`

Almacena información de las aulas TEA.

### Campos

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PK, NOT NULL, Default: uuid4() | Identificador único del aula |
| `name` | VARCHAR(100) | NOT NULL | Nombre del aula |
| `type` | VARCHAR(50) | NOT NULL, Default: "TEA" | Tipo de aula (actualmente solo "TEA") |
| `extra_metadata` | JSON | Default: {} | Metadatos adicionales en formato JSON |
| `created_at` | TIMESTAMP | Default: utcnow() | Fecha de creación del registro |

### Relaciones

- **1:N** con `events` (cascade delete)
- **1:N** con `recommendations` (cascade delete)

### Índices

- Primary Key: `id`

---

## Tabla: `events`

Almacena eventos pedagógicos anonimizados registrados por el docente.

### Campos

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PK, NOT NULL, Default: uuid4() | Identificador único del evento |
| `classroom_id` | UUID | FK → classrooms.id, NOT NULL | Referencia al aula |
| `event_type` | VARCHAR(50) | NOT NULL | Tipo de evento (ver valores permitidos) |
| `description` | VARCHAR(500) | NOT NULL | Descripción breve y objetiva |
| `moment_of_day` | VARCHAR(20) | NOT NULL | Momento del día (mañana/mediodía/tarde) |
| `day_of_week` | VARCHAR(20) | NULL | Día de la semana (opcional) |
| `duration_minutes` | INTEGER | NULL | Duración en minutos (opcional) |
| `supports` | JSON | Default: [] | Lista de apoyos utilizados (array JSON) |
| `additional_supports` | TEXT | NULL | Apoyos adicionales en texto libre |
| `result` | VARCHAR(50) | NOT NULL | Resultado del evento (ver valores permitidos) |
| `observations` | TEXT | NULL | Observaciones adicionales |
| `timestamp` | TIMESTAMP | Default: utcnow() | Fecha y hora del evento |

### Valores Permitidos

#### `event_type`
- `TRANSICION`
- `CAMBIO_DE_RUTINA`
- `APRENDIZAJE`
- `REGULACION`

#### `moment_of_day`
- `mañana`
- `mediodia`
- `tarde`

#### `day_of_week` (opcional)
- `lunes`
- `martes`
- `miercoles`
- `jueves`
- `viernes`
- `sabado`
- `domingo`

#### `result`
- `EXITOSO`
- `PARCIAL`
- `DIFICULTAD`

#### `supports` (valores en el array JSON)
- `"Anticipación visual"`
- `"Adaptación del entorno"`
- `"Mediación verbal"`
- `"Pausa sensorial"`
- `"Apoyo individual del adulto"`

### Relaciones

- **N:1** con `classrooms` (muchos eventos pertenecen a un aula)

### Índices

- Primary Key: `id`
- Foreign Key: `classroom_id` → `classrooms.id`

---

## Tabla: `recommendations`

Almacena recomendaciones pedagógicas generadas por el sistema basadas en patrones históricos.

### Campos

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id` | UUID | PK, NOT NULL, Default: uuid4() | Identificador único de la recomendación |
| `classroom_id` | UUID | FK → classrooms.id, NOT NULL | Referencia al aula |
| `recommendation_type` | VARCHAR(50) | NOT NULL | Tipo de recomendación (ver valores permitidos) |
| `title` | VARCHAR(200) | NOT NULL | Título descriptivo y accionable |
| `description` | TEXT | NOT NULL | Explicación clara de la recomendación |
| `applicable_context` | TEXT | NOT NULL | Cuándo y cómo aplicar esta recomendación |
| `detected_pattern` | TEXT | NOT NULL | Breve explicación del patrón histórico detectado |
| `confidence` | VARCHAR(20) | NOT NULL | Nivel de confianza (ver valores permitidos) |
| `generated_at` | TIMESTAMP | Default: utcnow() | Fecha y hora de generación |

### Valores Permitidos

#### `recommendation_type`
- `ANTICIPACION`
- `ESTRATEGIA`
- `ADAPTACION`

#### `confidence`
- `ALTA`
- `MEDIA`
- `BAJA`

### Relaciones

- **N:1** con `classrooms` (muchas recomendaciones pertenecen a un aula)

### Índices

- Primary Key: `id`
- Foreign Key: `classroom_id` → `classrooms.id`

---

## Relaciones y Constraints

### Foreign Keys

1. `events.classroom_id` → `classrooms.id`
   - ON DELETE: CASCADE (si se elimina un aula, se eliminan sus eventos)

2. `recommendations.classroom_id` → `classrooms.id`
   - ON DELETE: CASCADE (si se elimina un aula, se eliminan sus recomendaciones)

### Cascade Delete

- Al eliminar un registro en `classrooms`, se eliminan automáticamente:
  - Todos los registros relacionados en `events`
  - Todos los registros relacionados en `recommendations`

---

## Consideraciones de Diseño

### Aislamiento por Aula

- Cada aula es completamente independiente
- No hay compartición de datos entre aulas
- Los eventos y recomendaciones están siempre asociados a un aula específica

### Anonimización

- No se almacenan datos personales de menores
- Los eventos son completamente anonimizados
- No hay campos que permitan identificar estudiantes individuales

### Validación

- La validación de valores permitidos (enums) se realiza a nivel de aplicación (Pydantic)
- La base de datos almacena los valores como strings para flexibilidad

### Timestamps

- Todos los timestamps usan `datetime.utcnow()` para consistencia
- Se almacenan sin zona horaria (TIMESTAMP WITHOUT TIME ZONE)

---

## Inicialización de la Base de Datos

Para crear las tablas en la base de datos, ejecutar:

```bash
python -m app.models.init_db
```

**⚠️ Advertencia:** Este script elimina todas las tablas existentes antes de crearlas. Solo usar en desarrollo.

---

## Acceso a la Base de Datos

### Adminer

- **URL:** http://localhost:8080
- **Sistema:** PostgreSQL
- **Servidor:** `postgres` (nombre del servicio en docker-compose)
- **Usuario:** `aulaplus`
- **Contraseña:** `dev_password_2024`
- **Base de datos:** `aulaplus_db`

### Conexión Directa

```bash
# Desde el contenedor
docker exec -it aula_plus_db psql -U aulaplus -d aulaplus_db

# Desde el host (si el puerto está expuesto)
psql -h localhost -p 5432 -U aulaplus -d aulaplus_db
```

---

## Próximas Mejoras

- [ ] Índices adicionales para optimizar consultas frecuentes
- [ ] Tabla `recommendation_feedback` para feedback del docente
- [ ] Migraciones con Alembic para versionado de esquema
- [ ] Soft delete (marcar como eliminado en lugar de borrar)

---

**Última actualización:** 2026-02-02

