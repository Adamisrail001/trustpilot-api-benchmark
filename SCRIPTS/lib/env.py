"""Ported 1:1 from scripts/lib/env.js. Minimal .env loader (no dependency on
python-dotenv). Reads KEY=VALUE lines from a .env file at the project root
and applies any not already set in os.environ. Blank lines and lines
starting with # are ignored."""
import os
from pathlib import Path

_DEFAULT_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


def load_env(env_path=None):
    path = Path(env_path) if env_path else _DEFAULT_ENV_PATH
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").split("\n"):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        eq = line.find("=")
        if eq == -1:
            continue
        key = line[:eq].strip()
        value = line[eq + 1 :].strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if key not in os.environ:
            os.environ[key] = value


def require_env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable {name}. Add it to a .env file "
            "at the project root (see .env.example) - never hardcode it in this script."
        )
    return value
