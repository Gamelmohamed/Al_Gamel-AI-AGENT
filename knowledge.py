from pathlib import Path

from config import BASE_DIR, KNOWLEDGE_DIR


def load_knowledge_base():
    if not KNOWLEDGE_DIR.exists():
        return ""

    sections = []

    for file_path in sorted(KNOWLEDGE_DIR.rglob("*.md")):
        try:
            content = file_path.read_text(encoding="utf-8").strip()
        except OSError as error:
            print(f"Warning: Could not read {file_path.name}: {error}")
            continue

        if not content:
            continue

        relative_path = file_path.relative_to(BASE_DIR)
        sections.append(
            f"\n===== {relative_path} =====\n\n{content}\n"
        )

    return "\n".join(sections)


def knowledge_status():
    exists = KNOWLEDGE_DIR.exists()
    files = list(KNOWLEDGE_DIR.rglob("*.md")) if exists else []
    return {
        "directory": str(KNOWLEDGE_DIR),
        "exists": exists,
        "markdown_files": len(files),
    }
