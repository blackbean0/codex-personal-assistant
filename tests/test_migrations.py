import sqlite3

import pytest

from pa import db, jobs, settings


def test_legacy_call_counts_survive_repeated_connects(tmp_path, monkeypatch):
    path = tmp_path / "old.db"
    c = sqlite3.connect(path)
    c.executescript(db.SCHEMA.replace("ai_calls INTEGER NOT NULL DEFAULT 0,\n  ai_backend TEXT NOT NULL DEFAULT 'codex',", "claude INTEGER NOT NULL DEFAULT 0,"))
    c.execute("INSERT INTO jobs (kind, title, claude, created_at, updated_at) VALUES ('notices','old',7,'a','b')")
    c.commit()
    c.close()
    monkeypatch.setattr(db, "PATH", path)
    for _ in range(2):
        c = db.connect()
        assert dict(c.execute("SELECT ai_calls, ai_backend FROM jobs").fetchone()) == {"ai_calls": 7, "ai_backend": "unknown"}
        c.close()


def test_cancelled_queue_is_not_executed(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "PATH", tmp_path / "pa.db")
    c = db.connect()
    id_ = jobs.enqueue(c, "notices", "n", "test")
    assert jobs.cancel(c, id_)
    assert not jobs.run_next(c)
    assert jobs.recent(c)[0]["status"] == "cancelled"
    c.close()


def test_report_failure_preserves_existing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "PATH", tmp_path / "pa.db")
    monkeypatch.setattr(jobs, "REPORT_DIR", tmp_path)
    monkeypatch.setattr(jobs, "student", lambda: ("123", "Example"))
    monkeypatch.setattr(jobs.materials, "course_dirs", lambda _: None)
    monkeypatch.setattr(jobs.links, "paths", lambda *args: [])
    monkeypatch.setattr(jobs.ai, "ask", lambda *args, **kwargs: "invalid response")
    c = db.connect()
    db.sync_source(c, "inbox", [{"key": "x", "kind": "assignment", "course": "", "title": "Report", "due": None,
                              "earliest": None, "minutes": 20, "url": ""}])
    task = dict(c.execute("SELECT * FROM tasks WHERE key='x'").fetchone())
    file = jobs.report_path(task, c)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text("original user content", encoding="utf-8")
    jobs.enqueue(c, "report-force", "x", "Report")
    jobs.run_next(c)
    assert jobs.recent(c)[0]["status"] == "failed"
    assert file.read_text(encoding="utf-8") == "original user content"
    assert not list(file.parent.glob("*_old*.md"))
    c.close()


def test_central_paths_drive_default_material_roots(tmp_path, monkeypatch):
    (tmp_path / "config").mkdir()
    (tmp_path / "config/assistant.yaml").write_text("projects: {}", encoding="utf-8")
    monkeypatch.setattr(settings, "ROOT", tmp_path)
    monkeypatch.setattr(settings, "load_yaml", lambda _: {"projects": {"study": str(tmp_path / "한글 자료")}})
    assert settings.material_path("~/study_system/materials") == tmp_path / "한글 자료" / "materials"


def test_legacy_custom_paths_are_used_before_central_migration(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ROOT", tmp_path)
    monkeypatch.setattr(settings, "load_yaml", lambda name: {"root": str(tmp_path / "old study"), "quiz": {"dir": str(tmp_path / "old quiz")}})
    assert settings.project("study") == tmp_path / "old study"
    assert settings.project("quiz") == tmp_path / "old quiz"


def test_invalid_windows_student_filename_rejected(monkeypatch):
    monkeypatch.setattr(settings, "load_yaml", lambda _: {"student": {"id": "123", "name": "a/b"}})
    with pytest.raises(ValueError):
        settings.student()
