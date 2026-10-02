from app.models.repository import (
    FileRepresentation,
    RepositoryRepresentation,
)

from app.services.file_filter import is_important_file
from app.services.github_service import get_file_content
from app.services.language_service import detect_language


MAX_CONTENT_FILES = 50


def build_repository_representation(
    metadata: dict,
    tree: list[dict],
) -> RepositoryRepresentation:

    important_files = [
        file
        for file in tree
        if is_important_file(file["path"])
    ]

    remaining_files = [
        file
        for file in tree
        if not is_important_file(file["path"])
    ]

    selected_files = (
        important_files + remaining_files
    )[:MAX_CONTENT_FILES]

    selected_paths = {
        file["path"]
        for file in selected_files
    }

    files = []

    for file in tree:
        path = file["path"]

        content = None

        if path in selected_paths:
            try:
                content = get_file_content(file["url"])
            except Exception:
                content = None

        files.append(
            FileRepresentation(
                path=path,
                language=detect_language(path),
                size=file.get("size", 0),
                important=is_important_file(path),
                content=content,
            )
        )

    return RepositoryRepresentation(
        name=metadata["name"],
        full_name=metadata["full_name"],
        description=metadata["description"],
        default_branch=metadata["default_branch"],
        language=metadata["language"],
        files=files,
    )