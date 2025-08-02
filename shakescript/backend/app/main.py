from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from app.api.routes import (
    stories_routes,
    episodes_routes,
    auth_routes,
    dashboard_routes,
)

# Define the security scheme for the Authorization header.
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

# Initialize the FastAPI application
app = FastAPI(
    title="Shakescript API",
    description="API for generating and managing stories.",
    version="1.0.0",
    dependencies=[Depends(api_key_header)],
)

# Configure CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shakescriptai.tech", "http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
)

# Include all the different API routers
app.include_router(auth_routes.router, prefix="/api/v1", tags=["authentication"])
app.include_router(stories_routes.router, prefix="/api/v1", tags=["stories"])
app.include_router(episodes_routes.router, prefix="/api/v1", tags=["episodes"])
app.include_router(dashboard_routes.router, prefix="/api/v1", tags=["dashboard"])

@app.get("/", tags=["Root"])
def read_root():
    """
    A simple root endpoint to confirm that the API is running.
    """
    return {"message": "Welcome to the Shakescript API!"}
