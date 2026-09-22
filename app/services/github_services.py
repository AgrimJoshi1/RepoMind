from urllib.parse import urlparse

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