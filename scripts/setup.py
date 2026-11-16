"""Windows-first setup, preserving existing configuration and project guidance."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-install", action="store_true")
    parser.add_argument("--skip-browser", action="store_true")
    parser.add_argument("--skip-extension", action="store_true")
    args = parser.parse_args()
    os.chdir(ROOT)
    if sys.version_info < (3, 10):
        sys.exit("Python 3.10 이상이 필요합니다")
    if not PYTHON.exists():
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
    if not args.skip_install:
        subprocess.run([str(PYTHON), "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    if not args.skip_browser:
        subprocess.run([str(PYTHON), "-m", "playwright", "install", "chromium"], check=True)
    subprocess.run([str(PYTHON), "-X", "utf8", "-c", "from pa.bootstrap import prepare; prepare(); print('개인 설정·연결 지침·로컬 워크스페이스 준비 완료')"], check=True)
    if not args.skip_extension:
        subprocess.run([str(PYTHON), "-X", "utf8", "-m", "pa", "vscode-ext"], check=False)
    # Missing personal authentication is an actionable setup state, not a failed install.
    subprocess.run([str(PYTHON), "-X", "utf8", "-m", "pa", "doctor"], check=False)


if __name__ == "__main__":
    main()
