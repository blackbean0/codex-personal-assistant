from types import SimpleNamespace

from pa import engine


def test_supervisor_restarts_on_75_and_keeps_private_logs(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "ROOT", tmp_path)
    codes = iter([75, 0])
    calls = []

    def run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        assert kwargs["env"]["PA_ENGINE_CHILD"] == "1"
        assert kwargs["stdout"] is kwargs["stderr"]
        assert not kwargs["stdout"].closed
        return SimpleNamespace(returncode=next(codes))

    monkeypatch.setattr(engine.subprocess, "run", run)
    assert engine.main() == 0
    assert len(calls) == 2
    assert calls[0][0][-2:] == ["pa", "watch"]
    assert calls[0][1]["stdout"].closed
