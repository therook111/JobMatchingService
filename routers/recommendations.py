from fastapi import APIRouter, File, UploadFile, Depends
from fastapi.responses import HTMLResponse, FileResponse
from utils.misc import process_cv
from search_engine.service import PersonalizedEngine
from routers.dependencies import inject_engine
from utils.logging import system_logger

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/", response_class=HTMLResponse)
async def get_recommendations(CV: UploadFile = File(...), engine=Depends(inject_engine)):
    try:
        CV = process_cv(CV)
        
        recommendations, cv_id = engine.GetBestJobs(CV)

        with open('assets/result_table_template.html', 'r', encoding='utf-8') as f:
            result_template = f.read()

        final_html = result_template.replace(
            '<div id="resultContainer">',
            f'<div id="resultContainer">{recommendations}'
        )
        return HTMLResponse(content=final_html)
    except Exception as e:
        extra_info = {"service": "recommendations", "request_id": cv_id}
        system_logger.error(f"Error occurred while recommending jobs: {e}", exc_info=True, extra=extra_info)
        raise Exception("An error occurred while processing the request.")
