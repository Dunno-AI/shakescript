from fastapi import FastAPI
from .api.routes import stories

app = FastAPI()

app.include_router(stories.router , prefix="/api")
@app.get("/")
def root():
    return {"message":"FASTAPI + Supabase is running"}



