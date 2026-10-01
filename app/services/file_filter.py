from pathlib import PurePosixPath


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    "coverage",
    ".next",
    ".nuxt",
}

IGNORED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".svg",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".zip",
    ".tar",
    ".gz",
    ".rar",
    ".7z",
    ".exe",
    ".dll",
    ".so",
    ".bin",
}
IMPORTANT_FILES = {
    "README.md",
    "README",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "Dockerfile",
    "docker-compose.yml",
    ".env.example",
}

MAX_FILE_SIZE = 500 * 1024


def should_include_file(file: dict) -> bool:
    path = file.get("path", "")
    size = file.get("size", 0)

    path_object = PurePosixPath(path)

    if file.get("type") != "blob":
        return False

    if any(
        directory in IGNORED_DIRECTORIES
        for directory in path_object.parts
    ):
        return False

    if path_object.suffix.lower() in IGNORED_EXTENSIONS:
        return False

    if size > MAX_FILE_SIZE:
        return False

    return True

def filter_repository_tree(tree: list[dict]) -> list[dict]:
    return [
        file
        for file in tree
        if should_include_file(file)
    ]

def is_important_file(path: str) -> bool:
    filename = PurePosixPath(path).name

    return filename in IMPORTANT_FILES