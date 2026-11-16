"""Run tests with fresh temporary storage, isolated from other Windows identities."""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    with tempfile.TemporaryDirectory(prefix="pa-tests-") as directory:
        return subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "tests", "-p", "no:cacheprovider",
                                "--basetemp", str(Path(directory) / "work"), *sys.argv[1:]], cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
