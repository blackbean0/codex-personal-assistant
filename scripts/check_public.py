"""Check staged changes before publishing; never print matched secret contents."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    result = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"], cwd=ROOT, capture_output=True, check=True)
    paths = [p for p in result.stdout.decode("utf-8").split("\0") if p]
    failures = []
    secrets = re.compile(r"gh[pousr]_[A-Za-z0-9]{25,}|sk-(?:proj-)?[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
    for name in paths:
        p = Path(name)
        private = (name == ".env" or (name.startswith(".env.") and name != ".env.example")
                   or name.startswith(("data/", "추가자료/")) or name in ("config/profile.md", "inbox.md", "TODAY.md", "assistant.local.code-workspace", "dashboard/data.js")
                   or (name.startswith("config/") and p.suffix == ".yaml" and ".example." not in name)
                   or p.name.startswith(("credentials", "token", "client_secret")) and p.suffix == ".json"
                   or name.startswith(".codex/") and name != ".codex/config.toml")
        if private:
            failures.append(name + ": private file")
            continue
        blob = subprocess.run(["git", "show", ":" + name], cwd=ROOT, capture_output=True, check=True).stdout
        if secrets.search(blob.decode("utf-8", errors="replace")):
            failures.append(name + ": credential pattern (value hidden)")
    for failure in failures:
        print(failure)
    print(f"Public staging check: {len(paths)} files, {len(failures)} failures")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
