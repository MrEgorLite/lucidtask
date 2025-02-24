from contextlib import asynccontextmanager

import redis
import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from routes import (
    accounts_router,
    posts_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.asyncio.Redis(host="localhost", port=6379, db=0)
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")

    yield

    await redis_client.close()

app = FastAPI(
    title="Lucid Task",
    description="description",
    lifespan=lifespan
)

api_version_prefix = "/api/v1"


app.include_router(accounts_router, prefix=f"{api_version_prefix}/accounts", tags=["accounts"])
app.include_router(posts_router, prefix=f"{api_version_prefix}/posts", tags=["posts"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
