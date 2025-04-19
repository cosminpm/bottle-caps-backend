from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyinstrument import Profiler
from starlette import status
from starlette.requests import Request

from app.config import LIMIT_PERIOD, Settings
from app.services.detect.router import detect_router
from app.services.identify.router import identify_router
from app.services.limiter import request_limiter
from app.services.saver.router import saver_router

settings = Settings()

if settings.is_sentry:
    import sentry_sdk
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0,
        _experiments={
            "continuous_profiling_auto_start": True,
        },
    )


app = FastAPI()

# Add routers
app.include_router(detect_router)
app.include_router(identify_router)
app.include_router(saver_router)


origins = [
    "*",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Profiling
if settings.profiling_time:

    @app.middleware("http")
    async def profile_time_request(request: Request, call_next: Any) -> Any:
        """Profile the request."""
        profiler = Profiler(interval=0.01, async_mode="enabled")
        profiler.start()
        response = await call_next(request)
        profiler.stop()
        profiler.open_in_browser()
        return response


@app.get("/health")
@request_limiter.limit(LIMIT_PERIOD)
def health_check(request: Request):
    """Healthcheck."""
    return status.HTTP_200_OK


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
