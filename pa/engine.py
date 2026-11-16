"""Windows engine supervisor, including background stdout and code-restart handling."""
import os
import subprocess
import sys

from pa.config import ROOT


def main():
    env = os.environ.copy()
    env["PA_ENGINE_CHILD"] = "1"
    python = sys.executable
    if os.name == "nt" and python.lower().endswith("pythonw.exe"):
        python = str(__import__("pathlib").Path(python).with_name("python.exe"))
    log = ROOT / "data" / "engine.log"
    log.parent.mkdir(exist_ok=True)
    if log.exists() and log.stat().st_size > 2_000_000:
        log.write_bytes(log.read_bytes()[-1_000_000:])
    # A pythonw process has no console handles. Always provide real child streams.
    with log.open("a", encoding="utf-8") as out:
        while True:
            result = subprocess.run([python, "-X", "utf8", "-m", "pa", "watch"], cwd=ROOT, env=env,
                                    stdout=out, stderr=out,
                                    **({"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}))
            if result.returncode != 75:
                return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
