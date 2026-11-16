"""Idempotent personal setup and migration. Never prints personal values."""
import json
import re
import shutil

import yaml

from pa import settings
from pa.config import ROOT


def prepare():
    config = ROOT / "config"
    new_central = not (config / "assistant.yaml").exists()
    # Resolve legacy locations before creating the central configuration.
    projects = {n: str(settings.project(n)) for n in settings.DEFAULTS}
    for example in sorted(config.glob("*.example.*")):
        target = example.with_name(example.name.replace(".example", ""))
        if not target.exists():
            shutil.copy2(example, target)
    env = ROOT / ".env"
    if not env.exists():
        shutil.copy2(ROOT / ".env.example", env)
    path = config / "assistant.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    values = data.setdefault("projects", {})
    if new_central:
        values.update(projects)
    for key, value in projects.items():
        values.setdefault(key, value)
    report = settings.resolve(values["report"])
    student = data.setdefault("student", {})
    for file in (report / "AGENTS.md", report / "CLAUDE.md"):
        if file.exists() and not all(student.get(k) for k in ("id", "name")):
            match = re.search(r"학번은\s*(\d+),\s*이름은\s*(\S+?)다", file.read_text(encoding="utf-8"))
            if match:
                student["id"], student["name"] = match.groups()
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for name in settings.DEFAULTS:
        folder = settings.project(name)
        folder.mkdir(parents=True, exist_ok=True)
        rules = folder / "AGENTS.md"
        old = folder / "CLAUDE.md"
        if rules.exists():
            text = rules.read_text(encoding="utf-8")
            # Replace only the exact wrapper made by our previous setup.
            if text.strip() == "이 폴더의 규칙 원본은 CLAUDE.md 다. 작업 전에 CLAUDE.md 를 읽고 그대로 따른다." and old.exists():
                shutil.copy2(rules, folder / "AGENTS.before-codex.md")
                rules.write_text(old.read_text(encoding="utf-8"), encoding="utf-8")
        elif old.exists():
            rules.write_text(old.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            shutil.copy2(ROOT / "templates" / f"{name}-AGENTS.md", rules)
        if name == "study":
            for part in ("materials", "notes"):
                (folder / part).mkdir(exist_ok=True)
    (ROOT / "data").mkdir(exist_ok=True)
    folders = [{"name": "비서", "path": str(ROOT)}] + [
        {"name": n, "path": str(settings.project(n))} for n in settings.DEFAULTS]
    (ROOT / "assistant.local.code-workspace").write_text(json.dumps(
        {"folders": folders, "settings": {"files.exclude": {"**/.venv": True, "**/__pycache__": True}}},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return {"configured": True}
