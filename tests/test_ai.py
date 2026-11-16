import sys
import threading

import pytest

from pa import ai


@pytest.fixture
def fake(monkeypatch):
    calls = []
    monkeypatch.setattr(ai, "load_env", lambda: None)
    monkeypatch.setenv("PA_AI", "codex")
    monkeypatch.setattr(ai, "executable", lambda: "/bin/codex")
    monkeypatch.setattr(ai, "_run", lambda cmd, cwd, timeout, stdin=None: calls.append((cmd, cwd, stdin)) or "답")
    return calls


def test_codex_uses_read_only_stdin_and_reference_text(fake, tmp_path):
    f = tmp_path / "notes.txt"
    f.write_text("reference fact", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("project rule", encoding="utf-8")
    assert ai.ask("draft", files=[f], cwd=tmp_path, schema={"type": "object"}) == "답"
    cmd, cwd, stdin = fake[0]
    assert cmd[:2] == ["/bin/codex", "exec"] and cmd[-1] == "-"
    assert cmd[cmd.index("--sandbox") + 1] == "read-only"
    assert "--output-schema" in cmd and "--ephemeral" in cmd and "--add-dir" not in cmd
    assert "reference fact" in stdin and "project rule" in stdin


def test_other_backend_is_not_silently_selected(fake, monkeypatch):
    monkeypatch.setenv("PA_AI", "claude")
    with pytest.raises(ai.AIError, match="PA_AI=codex"):
        ai.backend()


def test_missing_cli_is_actionable(monkeypatch):
    monkeypatch.setattr(ai, "load_env", lambda: None)
    monkeypatch.delenv("CODEX_BIN", raising=False)
    monkeypatch.setattr(ai.shutil, "which", lambda _: None)
    with pytest.raises(ai.AIError, match="CODEX_BIN"):
        ai.executable()


def test_raw_errors_are_not_exposed():
    assert "secret" not in ai.safe_error(RuntimeError("secret token=https://host/?key=secret"))
    assert "secret" not in ai.safe_error(RuntimeError("401 secret"))


def test_timeout_terminates_process(tmp_path):
    with pytest.raises(TimeoutError):
        ai._run([sys.executable, "-c", "import time; time.sleep(20)"], tmp_path, 0.1)


def test_cancel_terminates_process(tmp_path):
    event = threading.Event()
    ai._local.cancel = event
    event.set()
    try:
        with pytest.raises(ai.Cancelled):
            ai._run([sys.executable, "-c", "import time; time.sleep(20)"], tmp_path, 10)
    finally:
        ai._local.cancel = None
