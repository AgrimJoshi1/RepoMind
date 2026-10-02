import httpx
from urllib.parse import urlparse
import base64

import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_API_URL = "https://api.github.com"
HEADERS = {}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

def parse_github_url(github_url:str)->tuple[str,str]:
    parsed_url = urlparse(github_url)

    if parsed_url.netloc.lower() != "github.com":
        raise ValueError("URL must be a GitHub repository URL")

    parts = parsed_url.path.strip("/").split("/")

    if len(parts) !=2:
        raise ValueError(
            "GitHub URL must have the format: https://github.com/owner/repository"

        )
    owner,repository = parts

    if not owner or not repository:
        raise ValueError("Github owner and repository are required")

    if repository.endswith(".git"):
        repository = repository[:-4]

    return owner,repository

def get_repository_metadata(owner:str,repository:str)->dict:
    url = f"{GITHUB_API_URL}/repos/{owner}/{repository}"

    response = httpx.get(url, headers=HEADERS, timeout=10)
    
    if response.status_code == 403:
        raise ValueError(
        "GitHub API rate limit exceeded. Please try again later."
        )
    
    if response.status_code == 404:
        raise ValueError("Github repository not found")

    response.raise_for_status()

    data = response.json()

    return {
        "name":data["name"],
        "full_name":data["full_name"],
        "description":data["description"],
        "default_branch":data["default_branch"],
        "language":data["language"]
    }

def get_repository_tree(owner: str,repository: str,branch: str) -> list[dict]:
    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repository}/git/trees/{branch}"
        "?recursive=1"
    )
    respone = httpx.get(url, headers=HEADERS, timeout=20)

    if respone.status_code == 404:
        raise ValueError("Repository tree not found")

    respone.raise_for_status()

    data = respone.json()

    return data.get("tree",[])


def get_file_content(url: str) -> str:
    response = httpx.get(url, headers=HEADERS, timeout=10)

    response.raise_for_status()

    data = response.json()

    if data.get("encoding") != "base64":
        raise ValueError("Unsupported GitHub file encoding")

    content = base64.b64decode(data["content"])

    return content.decode("utf-8", errors="replace")
    