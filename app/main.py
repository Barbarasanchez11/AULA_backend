from fastapi import FastAPI
from .routers import events, classrooms, recommendations

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Aula Plus Backend")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En desarrollo permitimos todo, puedes cambiarlo a ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(events.router)
app.include_router(classrooms.router)
app.include_router(recommendations.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Aula Plus Backend"}
