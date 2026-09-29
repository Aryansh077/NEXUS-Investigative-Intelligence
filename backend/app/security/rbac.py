ROLES = {
    "admin": {"*"},
    "investigator": {
        "cases:read", "cases:write",
        "complaints:read", "complaints:write",
        "predictions:read", "predictions:run",
        "alerts:read", "alerts:write",
        "evidence:read", "evidence:write",
        "graph:read", "moneyflow:read",
        "rag:use", "audit:read",
        "feedback:write"
    },
    "analyst": {
        "cases:read",
        "complaints:read",
        "predictions:read", "predictions:run",
        "alerts:read",
        "evidence:read",
        "graph:read", "moneyflow:read",
        "rag:use",
        "model:evaluate"
    },
    "viewer": {
        "cases:read",
        "complaints:read",
        "predictions:read",
        "alerts:read",
        "evidence:read",
        "graph:read", "moneyflow:read"
    }
}

def has_permission(role: str, permission: str) -> bool:
    perms = ROLES.get(role, set())
    return "*" in perms or permission in perms
