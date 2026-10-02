from pathlib import PurePosixPath

from app.models.repository import RepositoryRepresentation


ENTRY_POINT_NAMES = {
    "main.py",
    "app.py",
    "server.py",
    "index.py",
    "main.js",
    "app.js",
    "server.js",
    "index.js",
    "main.ts",
    "app.ts",
    "server.ts",
    "index.ts",
}


COMPONENT_DIRECTORIES = {
    "api": "API",
    "routes": "Routes",
    "services": "Services",
    "models": "Models",
    "controllers": "Controllers",
    "components": "Components",
    "utils": "Utilities",
    "database": "Database",
    "db": "Database",
    "middleware": "Middleware",
    "config": "Configuration",
    "data": "Data",
}


def find_entry_points(files: list) -> list[str]:
    entry_points = []

    for file in files:
        path = file.path
        filename = PurePosixPath(path).name

        if filename in ENTRY_POINT_NAMES:
            entry_points.append(path)

    return entry_points


def find_components(files: list) -> list[str]:
    components = set()

    for file in files:
        parts = PurePosixPath(file.path).parts

        for part in parts:
            component = COMPONENT_DIRECTORIES.get(part.lower())

            if component:
                components.add(component)

    return sorted(components)


def find_relationships(files: list) -> list[str]:
    relationships = set()
    components = set()

    for file in files:
        for part in PurePosixPath(file.path).parts:
            component = COMPONENT_DIRECTORIES.get(part.lower())

            if component:
                components.add(component)

    if "Routes" in components and "Services" in components:
        relationships.add("Routes → Services")

    if "Services" in components and "Database" in components:
        relationships.add("Services → Database")

    if "Services" in components and "Utilities" in components:
        relationships.add("Services → Utilities")

    if "Routes" in components and "Middleware" in components:
        relationships.add("Routes → Middleware")

    return sorted(relationships)


def build_data_flow(
    components: list[str],
    relationships: list[str],
) -> list[str]:

    flow = []

    if "Routes" in components:
        flow.append("Client → Routes")

    if "Routes" in components and "Middleware" in components:
        flow.append("Routes → Middleware")

    if "Routes" in components and "Services" in components:
        flow.append("Routes → Services")

    if "Services" in components and "Database" in components:
        flow.append("Services → Database")

    if "Services" in components and "Utilities" in components:
        flow.append("Services → Utilities")

    return flow


def analyze_architecture(
    repository: RepositoryRepresentation,
) -> dict:

    entry_points = find_entry_points(repository.files)

    components = find_components(repository.files)

    relationships = find_relationships(repository.files)

    data_flow = build_data_flow(
        components,
        relationships,
    )

    return {
        "entry_points": entry_points,
        "components": components,
        "relationships": relationships,
        "data_flow": data_flow,
    }