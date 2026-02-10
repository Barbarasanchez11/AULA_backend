# Scripts de Importación - AULA+

Este directorio contiene scripts para importar datos en el sistema AULA+.

## Script de Importación desde CSV

### Archivo: `import_events_from_csv.py`

Script para importar eventos desde un archivo CSV a la base de datos.

### Formato del CSV

El CSV debe tener las siguientes columnas:

| Columna | Requerido | Descripción | Valores Válidos |
|---------|-----------|-------------|-----------------|
| `classroom_id` | ✅ Sí | UUID del aula | UUID válido |
| `event_type` | ✅ Sí | Tipo de evento | `TRANSICION`, `CAMBIO_DE_RUTINA`, `APRENDIZAJE`, `REGULACION` |
| `description` | ✅ Sí | Descripción del evento | Mínimo 10 caracteres |
| `moment_of_day` | ✅ Sí | Momento del día | `mañana`, `mediodia`, `tarde` |
| `day_of_week` | ❌ No | Día de la semana | `lunes`, `martes`, `miercoles`, `jueves`, `viernes`, `sabado`, `domingo` |
| `duration_minutes` | ❌ No | Duración en minutos | Número entero >= 1 |
| `supports` | ✅ Sí | Apoyos utilizados | Lista separada por `;` o `,` de: `Anticipación visual`, `Adaptación del entorno`, `Mediación verbal`, `Pausa sensorial`, `Apoyo individual del adulto` |
| `additional_supports` | ❌ No | Apoyos adicionales | Texto libre (máx 200 caracteres) |
| `result` | ✅ Sí | Resultado del evento | `EXITOSO`, `PARCIAL`, `DIFICULTAD` |
| `observations` | ❌ No | Observaciones | Texto libre (máx 1000 caracteres) |

### Ejemplo de CSV

Ver `example_events.csv` para un ejemplo completo.

### Uso

```bash
# Desde el directorio raíz del proyecto
python3 scripts/import_events_from_csv.py scripts/example_events.csv

# Continuar aunque haya errores (por defecto)
python3 scripts/import_events_from_csv.py scripts/example_events.csv --skip-errors

# Detener en el primer error
python3 scripts/import_events_from_csv.py scripts/example_events.csv --no-skip-errors
```

### Proceso de Importación

El script realiza los siguientes pasos para cada evento:

1. **Validación de esquema**: Verifica que los datos cumplan el formato requerido
2. **Normalización de texto**: Limpia espacios extra y caracteres de control
3. **Validación de PII**: Detecta datos personales (nombres, DNI, teléfonos, etc.)
4. **Validación de aula**: Verifica que el aula existe
5. **Guardado en PostgreSQL**: Guarda el evento en la base de datos
6. **Generación de embeddings**: Genera embeddings automáticamente (fast + quality)

### Salida

El script muestra:
- ✅ Eventos importados correctamente (con ID)
- ❌ Eventos que fallaron (con razón del error)
- Resumen final con estadísticas

### Errores Comunes

1. **"Invalid classroom_id"**: El UUID del aula no es válido o no existe
2. **"PII detected"**: El evento contiene datos personales (nombres, DNI, etc.)
3. **"Invalid event_type"**: El tipo de evento no es uno de los valores válidos
4. **"Invalid supports"**: Los apoyos no son válidos (ver lista de valores válidos)
5. **"Description must be at least 10 characters"**: La descripción es muy corta

### Notas Importantes

- **PII**: El script rechazará automáticamente eventos con datos personales
- **Normalización**: Los textos se normalizan automáticamente (espacios, caracteres de control)
- **Embeddings**: Se generan automáticamente para búsqueda semántica
- **Encoding**: El CSV debe estar en UTF-8

