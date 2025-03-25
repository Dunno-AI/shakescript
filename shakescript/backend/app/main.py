from fastapi import FastAPI, APIRouter
from app.api.routes import stories, episodes, embeddings, search

app = FastAPI()
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(stories.router, tags=["stories"])
api_router.include_router(episodes.router, tags=["episodes"])
# api_router.include_router(embeddings.router, prefix="/embeddings", tags=["embeddings"])
# api_router.include_router(search.router, prefix="/search", tags=["search"])

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Shakyscript API"}
