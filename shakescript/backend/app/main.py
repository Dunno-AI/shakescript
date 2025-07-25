# app/main.py

from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from app.api.routes import auth_routes, stories_routes, episodes_routes

# Define the security scheme for the Authorization header.
# This tells FastAPI how to create the "Authorize" button in the docs.
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

# Pass the dependency to the main app instance to apply it globally for the docs.
app = FastAPI(
    title="Shakescript API",
    description="API for generating and managing stories.",
    version="1.0.0",
    dependencies=[Depends(api_key_header)],
)

# Enable CORS - It's better practice to list specific frontend origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your router setup remains the same.
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(stories_routes.router, tags=["stories"])
api_router.include_router(episodes_routes.router, tags=["episodes"])
api_router.include_router(auth_routes.router, tags=["authentication"])

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Shakescript API"}
