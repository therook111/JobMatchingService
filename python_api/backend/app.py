from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import filtering, recommendations, static_sites
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER 

app = FastAPI()

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    
    return RedirectResponse(url="/fallback", status_code=HTTP_303_SEE_OTHER)


# Add routers
app.include_router(static_sites.router)
app.include_router(recommendations.router)
app.include_router(filtering.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)