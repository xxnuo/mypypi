from fastapi import APIRouter

utils_router = APIRouter()


@utils_router.get("/health")
def health():
    return {"status": "ok"}
