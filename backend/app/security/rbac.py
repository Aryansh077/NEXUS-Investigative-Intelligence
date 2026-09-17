ROLES = {
    "investigator": {"cases:read", "cases:write", "evidence:read", "graph:read", "copilot:use"},
    "supervisor": {"cases:read", "cases:write", "evidence:read", "graph:read", "copilot:use", "audit:read"},
    "admin": {"*"},
}

def has_permission(role: str, permission: str) -> bool:
    perms = ROLES.get(role, set())
    return "*" in perms or permission in perms
