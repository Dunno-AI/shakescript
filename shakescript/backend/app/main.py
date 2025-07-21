from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth_routes, stories_routes, episodes_routes

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(stories_routes.router, tags=["stories"])
api_router.include_router(episodes_routes.router, tags=["episodes"])
api_router.include_router(auth_routes.router, tags=["authentication"])
# api_router.include_router(embeddings.router, prefix="/embeddings", tags=["embeddings"])
# api_router.include_router(search.router, prefix="/search", tags=["search"])

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Shakyscript API"}
