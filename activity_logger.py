import json
from datetime import datetime, timezone

from config import LOGS_DIR

LOG_FILE = LOGS_DIR / "agent_activity.jsonl"
BLOCKED_KEYS = {
    "api_key",
    "password",
    "token",
    "credentials",
    "secret",
    "refresh_token",
}


def log_event(action, **fields):
    safe_fields = {}

    for key, value in fields.items():
        if key.lower() in BLOCKED_KEYS:
            continue
        safe_fields[key] = value

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        **safe_fields,
    }

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry
