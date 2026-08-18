from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database.database import init_db
from app.api.jobs_router import router as jobs_router

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI ICP Qualification Engine API", lifespan=lifespan)

# L'inclusion du routeur API DOIT précéder le mount statique "/" ci-dessous :
# un mount catch-all enregistré en premier intercepterait aussi /api/*.
app.include_router(jobs_router, prefix="/api")

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
