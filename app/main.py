from fastapi import FastAPI
from .routers import events, classrooms, recommendations

app = FastAPI(title="Aula Plus Backend")

app.include_router(events.router)
app.include_router(classrooms.router)
app.include_router(recommendations.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Aula Plus Backend"}
