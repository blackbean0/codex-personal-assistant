import json

import yaml

from pa import bootstrap, settings


def test_setup_preserves_legacy_paths_rules_and_student_values(tmp_path, monkeypatch):
    (tmp_path / "config").mkdir()
    (tmp_path / "templates").mkdir()
    for name in ("study", "report", "quiz"):
        (tmp_path / "templates" / f"{name}-AGENTS.md").write_text("template", encoding="utf-8")
    cfg = {"projects": {}, "student": {"id": "", "name": ""}}
    (tmp_path / "config/assistant.example.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")
    paths = {name: str(tmp_path / name) for name in settings.DEFAULTS}
    legacy = {"root": paths["study"], "quiz": {"dir": paths["quiz"]}}
    (tmp_path / "config/courses.yaml").write_text(yaml.safe_dump(legacy), encoding="utf-8")
    report = tmp_path / "report"
    report.mkdir()
    (report / "CLAUDE.md").write_text("학번은 123, 이름은 Example다", encoding="utf-8")
    (tmp_path / ".env").write_text("KEEP=1", encoding="utf-8")
    monkeypatch.setattr(bootstrap, "ROOT", tmp_path)
    monkeypatch.setattr(settings, "ROOT", tmp_path)
    monkeypatch.setattr(settings, "DEFAULTS", {"study": paths["study"], "report": paths["report"], "quiz": paths["quiz"]})

    def load(name):
        p = tmp_path / "config" / f"{name}.yaml"
        if not p.exists():
            p = p.with_name(f"{name}.example.yaml")
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}

    monkeypatch.setattr(settings, "load_yaml", load)
    for _ in range(2):
        bootstrap.prepare()
        actual = yaml.safe_load((tmp_path / "config/assistant.yaml").read_text(encoding="utf-8"))
        assert actual["projects"] == paths
        assert actual["student"] == {"id": "123", "name": "Example"}
        assert (report / "AGENTS.md").read_text(encoding="utf-8") == (report / "CLAUDE.md").read_text(encoding="utf-8")
        assert (tmp_path / ".env").read_text(encoding="utf-8") == "KEEP=1"
        workspace = json.loads((tmp_path / "assistant.local.code-workspace").read_text(encoding="utf-8"))
        assert workspace["folders"][2]["path"] == paths["report"]
