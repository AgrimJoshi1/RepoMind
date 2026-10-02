from fastapi import APIRouter, HTTPException

from app.models.repository import RepositoryRequest

from app.services.file_filter import filter_repository_tree

from app.services.github_service import (
    parse_github_url,
    get_repository_metadata,
    get_repository_tree,
)

from app.services.repository_service import (
    build_repository_representation,
)

from app.services.analysis_service import (
    analyze_repository as analyze_repository_service,
)

from app.services.architecture_service import (
    analyze_architecture,
)


router = APIRouter()


@router.post("/analyze")
def analyze_repository(request: RepositoryRequest):

    try:
        owner, repository_name = parse_github_url(
            str(request.github_url)
        )

        metadata = get_repository_metadata(
            owner,
            repository_name,
        )

        tree = get_repository_tree(
            owner,
            repository_name,
            metadata["default_branch"],
        )

        filtered_tree = filter_repository_tree(tree)

        repository = build_repository_representation(
            metadata,
            filtered_tree,
        )

        summary = analyze_repository_service(
            repository
        )

        architecture = analyze_architecture(
            repository
        )

        return {
            "summary": summary,
            "architecture": architecture,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )