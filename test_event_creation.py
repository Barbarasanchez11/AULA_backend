#!/usr/bin/env python3
"""
Test script to verify the event creation endpoint format.
This helps debug 422 validation errors.
"""

import requests
import json
from uuid import UUID

# Base URL
BASE_URL = "http://127.0.0.1:8000"

# Example classroom ID (replace with a real one from your DB)
CLASSROOM_ID = "a2a9d9dd-70d8-40d6-82dd-cda1c6062bba"

# Example event data in the CORRECT format
# Note: Use actual enum values from app/schemas/enums.py
correct_event = {
    "classroom_id": CLASSROOM_ID,
    "event_type": "TRANSICION",  # Options: TRANSICION, CAMBIO_DE_RUTINA, APRENDIZAJE, REGULACION
    "description": "El estudiante tuvo dificultades al cambiar de actividad de matemáticas a recreo. Mostró resistencia y necesitó apoyo visual.",
    "context": {
        "moment_of_day": "mañana",  # Options: mañana, mediodia, tarde
        "day_of_week": "lunes",  # Options: lunes, martes, miercoles, jueves, viernes, sabado, domingo
        "duration_minutes": 15
    },
    "supports": ["Anticipación visual", "Mediación verbal"],  # Must use exact SupportType values
    "additional_supports": None,
    "result": "EXITOSO",  # Options: EXITOSO, PARCIAL, DIFICULTAD
    "observations": "Se calmó después de usar la agenda visual",
    "is_planned": False,
    "timestamp": None
}

print("=" * 60)
print("TEST: Creating event with correct format")
print("=" * 60)
print(f"\nRequest URL: {BASE_URL}/events/")
print(f"Request body:")
print(json.dumps(correct_event, indent=2, ensure_ascii=False))

try:
    response = requests.post(
        f"{BASE_URL}/events/",
        json=correct_event,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:")
    
    if response.status_code == 201:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print("\n✅ Event created successfully!")
    else:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print(f"\n❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")

print("\n" + "=" * 60)
print("Common validation errors:")
print("=" * 60)
print("""
1. Missing required fields:
   - classroom_id (UUID)
   - event_type (enum: TRANSICION, CAMBIO_DE_RUTINA, APRENDIZAJE, REGULACION)
   - description (string, min 10 chars)
   - context (object with moment_of_day)
   - supports (array, min 1 item)
   - result (enum: EXITOSO, PARCIAL, DIFICULTAD)

2. Invalid enum values:
   - event_type: must be one of TRANSICION, CAMBIO_DE_RUTINA, APRENDIZAJE, REGULACION
   - moment_of_day: must be one of mañana, mediodia, tarde
   - day_of_week: must be one of lunes, martes, miercoles, jueves, viernes, sabado, domingo
   - supports: must be exact SupportType values: "Anticipación visual", "Adaptación del entorno", "Mediación verbal", "Pausa sensorial", "Apoyo individual del adulto"
   - result: must be one of EXITOSO, PARCIAL, DIFICULTAD

3. Invalid types:
   - classroom_id must be a valid UUID string
   - description must be a string with at least 10 characters
   - supports must be an array
   - context must be an object

4. Common frontend mistakes:
   - Sending moment_of_day, day_of_week, duration_minutes at root level instead of inside context
   - Sending support strings instead of array
   - Missing .value for enums (backend expects strings, not enum objects)
""")

