from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings
from api.core.init import run as init_data
from api.sys.router import router as sys_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_data()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sys_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
