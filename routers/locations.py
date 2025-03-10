from fastapi import APIRouter, Depends
from routers.dependencies import inject_engine
from search_engine.service import PersonalizedEngine
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/locations", tags=["location"])

@router.get('/districts/{province_id}')
async def get_districts(province_id: str, engine: PersonalizedEngine = Depends(inject_engine)):
    response = engine.get_districts(province_id)
    if response:
        return response
    else:
        return RedirectResponse('/fallback', status_code=404)

@router.get('/provinces')
async def get_provinces(
    engine: PersonalizedEngine = Depends(inject_engine)
):
    response = engine.get_provinces()
    if response:
        return response 
    else:
        return RedirectResponse('/fallback', status_code=404)
