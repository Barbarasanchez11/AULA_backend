from fastapi import APIRouter

router = APIRouter(
    prefix="/eventos",
    tags=["eventos"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_eventos():
    return [{"name": "Evento 1"}]
