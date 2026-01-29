from fastapi import APIRouter

router = APIRouter(
    prefix="/aulas",
    tags=["aulas"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_aulas():
    return [{"name": "Aula 1"}]
