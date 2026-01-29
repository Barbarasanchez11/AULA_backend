from fastapi import FastAPI
from .routers import aulas, eventos

app = FastAPI(title="Aula Plus Backend")

app.include_router(aulas.router)
app.include_router(eventos.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Aula Plus Backend"}
