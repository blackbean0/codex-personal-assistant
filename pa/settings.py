"""Personal values and project paths, shared by CLI, dashboard and setup."""
import os
from pathlib import Path

from pa.config import ROOT, load_yaml

DEFAULTS = {"study": "~/study_system", "report": "~/report", "quiz": "~/quiz_system_project/pharmacy"}


def project(name):
    central_exists = (ROOT / "config/assistant.yaml").exists()
    cfg = load_yaml("assistant").get("projects", {}) if central_exists else {}
    value = cfg.get(name)
    if not value and not central_exists:
        legacy = load_yaml("courses")
        value = legacy.get("root") if name == "study" else legacy.get("quiz", {}).get("dir") if name == "quiz" else None
    return resolve(value or DEFAULTS[name])


def resolve(value):
    p = Path(os.path.expandvars(os.path.expanduser(str(value))))
    return (p if p.is_absolute() else ROOT / p).resolve()


def material_path(value):
    """Redirect old default roots through the central project configuration."""
    text = str(value).replace("\\", "/")
    for name, default in DEFAULTS.items():
        if text == default or text.startswith(default + "/"):
            return project(name) / text[len(default):].lstrip("/")
    return resolve(value)


def student():
    values = load_yaml("assistant").get("student", {})
    sid, name = str(values.get("id") or "").strip(), str(values.get("name") or "").strip()
    if not sid or not name:
        raise ValueError("config/assistant.yaml 의 student.id 와 student.name 을 직접 입력하세요")
    for value in (sid, name):
        if any(ch in value for ch in '<>:"/\\|?*') or any(ord(ch) < 32 for ch in value) or value.endswith((".", " ")):
            raise ValueError("학번·이름에 Windows 파일명으로 쓸 수 없는 문자가 있습니다")
    return sid, name
