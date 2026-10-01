from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title = "RepoMind",
    description = "Backend API for analyzing Github Repo",
    version = "0.1.0"
)

@app.get("/health")
def health_check():
    return{
        "status": "Working",
        "service":"RepoMind"

    }

app.include_router(router)