from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.responses import Response

from src.config import get_settings
from src.public.api.v1 import endpoints

settings = get_settings()

app = FastAPI(
    title="MemesPublicAPI",
    docs_url="/api/swagger-ui",
    openapi_url="/api/openapi.json"
)
add_pagination(app)

app.include_router(endpoints.router, prefix="/api/v1", tags=["memes"])


@app.get(settings.web_app.HEALTHCHECK_PATH, include_in_schema=False)
async def get_health():
    return Response(status_code=200)
