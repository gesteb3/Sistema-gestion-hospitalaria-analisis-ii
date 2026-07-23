METHOD_ACTIONS = {
    "GET": "CONSULTAR",
    "POST": "CREAR",
    "PUT": "ACTUALIZAR",
    "PATCH": "ACTUALIZAR",
    "DELETE": "ELIMINAR",
}


def action_from_method(method: str) -> str:
    return METHOD_ACTIONS.get(
        method.strip().upper(),
        "EJECUTAR",
    )


def module_from_path(
    path: str,
    api_prefix: str = "/api/v1",
) -> str:
    normalized = path

    if normalized.startswith(api_prefix):
        normalized = normalized[len(api_prefix):]

    segments = [
        segment
        for segment in normalized.strip("/").split("/")
        if segment
    ]

    if not segments:
        return "SISTEMA"

    return segments[0].upper().replace("-", "_")


def should_audit_path(path: str) -> bool:
    excluded_paths = {
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/health",
        "/api/v1/health/database",
    }

    return path not in excluded_paths
