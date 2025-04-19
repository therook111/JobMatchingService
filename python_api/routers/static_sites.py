from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from utils.misc import BASE_DIR

router = APIRouter(tags=["pages"])

@router.get("/", response_class=HTMLResponse)
async def serve_homepage():
    return FileResponse(f"{BASE_DIR}/assets/FE.html")

@router.get("/fallback", response_class=HTMLResponse)
async def serve_fallback():
    return FileResponse(f"{BASE_DIR}/assets/fallback.html")