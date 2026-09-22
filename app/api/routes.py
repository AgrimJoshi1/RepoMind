from fastapi import APIRouter, HTTPException

from app.models.repository import RepositoryRequest
from app.services.github_service import parse_github_url

router= APIRouter()

@router.post("/analyze")
def analyze_repository(request: RepositoryRequest):
    try:
        owner,repository = parse_github_url(
            str(request.github_url)
        )
        
        return{
            "owner" : owner,
            "repository": repository
        }
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )