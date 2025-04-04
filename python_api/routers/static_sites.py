from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter(tags=["pages"])

@router.get("/", response_class=HTMLResponse)
async def serve_homepage():
    return FileResponse("python_api/assets/FE.html")

@router.get("/fallback", response_class=HTMLResponse)
async def serve_fallback():
    return FileResponse("python_api/assets/fallback.html")