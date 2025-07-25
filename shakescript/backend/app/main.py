from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.routes import (
    stories_routes,
    episodes_routes,
    auth_routes,
    dashboard_routes,
)

# Initialize the FastAPI application
app = FastAPI(
    title="Shakescript API",
    description="Backend services for the Shakescript application.",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include all the different API routers
app.include_router(auth_routes.router, prefix="/api/v1" ,tags=["authentication"])
app.include_router(stories_routes.router, prefix="/api/v1",tags=["stories"])
app.include_router(episodes_routes.router, prefix="/api/v1",tags=["episodes"])
app.include_router(dashboard_routes.router, prefix="/api/v1",tags=["dashboard"])


@app.get("/", tags=["Root"])
def read_root():
    """
    A simple root endpoint to confirm that the API is running.
    """
    return {"message": "Welcome to the Shakescript API!"}
