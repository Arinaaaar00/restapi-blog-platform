from fastapi import FastAPI

from app.routers import posts, users
from app.storage.database import init_sample_data

app = FastAPI(title="Blog API", description="Базовый REST API для ведения блога")

app.include_router(users.router, prefix="/api/v1")
app.include_router(posts.router)


@app.on_event("startup")
async def startup_event() -> None:
    init_sample_data()


@app.get("/health")
async def health_check() -> dict:
    from app.storage.database import posts_db, users_db

    return {"status": "ok", "users_count": len(users_db), "posts_count": len(posts_db)}
