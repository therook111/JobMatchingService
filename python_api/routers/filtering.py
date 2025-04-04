from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from routers.dependencies import inject_engine
from search_engine.service import PersonalizedEngine
from fastapi.responses import RedirectResponse
from utils.schema import UserFilterQuery
from utils.misc import parse_query
import uuid 
from utils.logging import system_logger



router = APIRouter(prefix="/filtering", tags=["filtering"])
@router.post('/', response_class=HTMLResponse)

async def get_request(user: UserFilterQuery, engine: PersonalizedEngine = Depends(inject_engine)):
    extra_info = {'service': 'filtering', 'request_id': user.cv_id}
    try:
        es_query = parse_query(user.model_dump())
        system_logger.info(f"Received a request for filtering jobs with query: {user.model_dump()}", extra=extra_info)

        CV = engine.cache.get(uuid.UUID(user.cv_id))

        filtered = engine.GetFilteredJobs(CV, query=es_query)
        system_logger.info("Finished filtering jobs", extra=extra_info)
    except Exception as e:
        system_logger.error(f"An error occurred while filtering jobs: {e}", extra=extra_info, exc_info=True)
        return RedirectResponse(url="/", status_code=302)

    return HTMLResponse(content=filtered[0])

