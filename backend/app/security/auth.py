import os
import secrets

DEMO_USERNAME = os.getenv("NEXUS_DEMO_USERNAME", "investigator")
DEMO_PASSWORD = os.getenv("NEXUS_DEMO_PASSWORD", "nexus-demo")

def authenticate(username: str, password: str) -> bool:
    return secrets.compare_digest(username, DEMO_USERNAME) and secrets.compare_digest(password, DEMO_PASSWORD)
