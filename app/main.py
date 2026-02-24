from fastapi import FastAPI, Request, status
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .routers import events, classrooms, recommendations, admin

from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .config import settings

app = FastAPI(title="Aula Plus Backend")

# Configuración de CORS ultra-permisiva para el Hackathon
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Endpoint de salud para monitoreo"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Exception handler for validation errors (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors to provide detailed error messages.
    This helps debug what fields are missing or invalid in the request.
    """
    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        error_msg = error["msg"]
        error_type = error["type"]
        errors.append({
            "field": field_path,
            "message": error_msg,
            "type": error_type
        })
    
    # Log the error for debugging
    logger.error(f"Validation error on {request.method} {request.url.path}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": errors,
            "message": "Validation error: Please check the required fields and their formats"
        }
    )

app.include_router(admin.router)
app.include_router(events.router)
app.include_router(classrooms.router)
app.include_router(recommendations.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Aula Plus Backend"}
