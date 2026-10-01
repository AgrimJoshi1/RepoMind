from google import genai

from app.core.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)

from app.models.repository import RepositorySummary


client = genai.Client(api_key=GEMINI_API_KEY)


def generate_repository_summary(
    repository_context: str,
) -> RepositorySummary:

    prompt = f"""
You are analyzing a GitHub repository.

Based on the repository information below, generate a concise
developer-friendly summary.

Repository information:
{repository_context}

Focus on:
- what the repository does
- how the architecture is organized
- the main components
- technologies used
- important entry points

Do not invent information that is not supported by the repository.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": RepositorySummary,
        },
    )

    return RepositorySummary.model_validate_json(response.text)