# Only commands starting with one of these prefixes are permitted.
ALLOWED_PREFIXES = [
    "git status",
    "git log",
    "git diff",
    "ls",
    "pytest",
    "python3 --version",
]

def is_allowed(command: str) -> bool:
    return any(command.strip().startswith(prefix) for prefix in ALLOWED_PREFIXES)