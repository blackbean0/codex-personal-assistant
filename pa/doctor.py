"""Safe diagnostics: report readiness, never credential contents."""
import importlib.util
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

from pa import ai, settings
from pa.config import ROOT, load_env

_auth = {"at": 0, "value": None}


def readiness():
    load_env()
    if time.monotonic() - _auth["at"] > 60 or _auth["value"] is None:
        _auth.update(at=time.monotonic(), value=ai.status(auth=True))
    missing = []
    if not os.environ.get("CANVAS_TOKEN"):
        missing.append("Canvas 토큰 입력 필요 (.env)")
    if not (ROOT / "credentials.json").exists() or not (ROOT / "token.json").exists():
        missing.append("Google Calendar 본인 인증 필요")
    try:
        settings.student()
    except ValueError:
        missing.append("보고서 학번·이름 입력 필요 (config/assistant.yaml)")
    for n in ("timetable", "courses"):
        p = ROOT / "config" / f"{n}.yaml"
        if not p.exists() or "예시과목" in p.read_text(encoding="utf-8"):
            missing.append(f"실제 과목·시간표 설정 필요 ({n}.yaml)")
    return {"ai": _auth["value"], "missing": missing}


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", action="store_true", help="임시 DB로 Chromium 대시보드 확인")
    parser.add_argument("--ai", action="store_true", help="가상 자료로 실제 Codex 호출 (구독 사용)")
    args = parser.parse_args(argv)
    print(f"Python {platform.python_version()} / {platform.system()}")
    missing = [name for name in ("yaml", "pytest", "playwright", "pypdf", "jsonschema", "google.auth")
               if importlib.util.find_spec(name) is None]
    print("Python dependencies: " + ("MISSING " + ", ".join(missing) if missing else "PASS"))
    state = readiness()
    print("Codex CLI: " + ("PASS" if state["ai"]["installed"] else "MISSING"))
    print("Codex authentication: " + ("PASS" if state["ai"].get("authenticated") else "NEEDS LOGIN / HOME ACCESS"))
    for name in settings.DEFAULTS:
        p = settings.project(name)
        print(f"Project {name}: " + ("guidance ready" if (p / "AGENTS.md").is_file() else "needs setup"))
    for item in state["missing"]:
        print("준비 필요: " + item)
    if args.ai or args.browser:
        from pa.smoke import run
        run(with_ai=args.ai, with_browser=args.browser)
    return 1 if missing or not state["ai"]["installed"] else 0
