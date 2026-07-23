from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import engine
from app.api.routes import router as api_router
from app.db.engine import init_db
from app.db.redis import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(engine)
    yield
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(title="Sync Player", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "https://sync-player-ashen.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

