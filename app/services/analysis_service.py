from app.models.repository import RepositoryRepresentation
from app.services.gemini_service import generate_repository_summary


def build_analysis_context(
    repository: RepositoryRepresentation,
) -> str:

    lines = [
        f"Repository: {repository.full_name}",
        f"Description: {repository.description}",
        f"Primary language: {repository.language}",
        f"Default branch: {repository.default_branch}",
        "",
        "Files:",
    ]

    for file in repository.files:
        line = (
            f"- {file.path} "
            f"(language: {file.language}, "
            f"size: {file.size} bytes"
        )

        if file.important:
            line += ", important"

        line += ")"

        if file.content:
            line += f"\n  Content:\n{file.content}"

        lines.append(line)

    return "\n".join(lines)


def analyze_repository(
    repository: RepositoryRepresentation,
):
    context = build_analysis_context(repository)

    return generate_repository_summary(context)