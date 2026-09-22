from fastapi import APIRouter, HTTPException

from app.models.repository import RepositoryRequest
from app.services.github_service import(
    parse_github_url,
    get_repository_metadata,
    get_repository_tree
)

router= APIRouter()

@router.post("/analyze")
def analyze_repository(request: RepositoryRequest):
    try:
        owner,repository = parse_github_url(
            str(request.github_url)
        )
        
        metadata = get_repository_metadata(
            owner,
            repository
        )
        
        tree = get_repository_tree(
            owner,
            repository,
            metadata["default_branch"]
        )
        return{
            "repository" : metadata,
            "file_count": len(tree),
            "files": tree
        }
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )