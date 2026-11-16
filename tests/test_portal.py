from datetime import date
from datetime import datetime

from pa.portal import parse_slots
from pa.sync_timetable import build_event
from pa import portal
from pa.model import KST


def test_cancelled_and_untimed_slots_are_not_scheduled():
    base = {"sbjctNm": "Example", "lsnYmd": "20261116", "bgngHr": "09:00", "endHr": "09:50", "cclctYn": "N"}
    rows = [base, dict(base), {**base, "cclctYn": "Y"}, {**base, "sbjctNm": "Online", "bgngHr": None}]
    lessons, untimed, cancelled = parse_slots(rows)
    assert len(lessons) == 1 and untimed == ["Online"] and cancelled == 1
    _, event = build_event(lessons[0], date(2026,9,1), date(2026,12,21))
    assert "recurrence" not in event
    assert event["start"]["dateTime"] == "2026-11-16T09:00:00"


def test_makeup_lesson_keeps_actual_date():
    rows = [{"sbjctNm": "Example", "lsnYmd": "20261121", "bgngHr": "14:00", "endHr": "14:50", "splctYn": "Y"}]
    lessons, _, _ = parse_slots(rows)
    assert lessons[0]["date"] == "2026-11-21"


def test_sunday_policy_reads_once_and_never_on_other_days(monkeypatch):
    cfg = {"portal_import": {"year": 2026, "term": 20, "refresh_on_full_sync": True,
                             "refresh_weekday": "sun", "imported_at": "2026-11-16T12:00:00+09:00"}}
    monkeypatch.setattr(portal, "load_timetable", lambda: cfg)
    calls = []
    monkeypatch.setattr(portal, "fetch", lambda *args: calls.append(args) or [])
    monkeypatch.setattr(portal, "apply", lambda *args: (1, 0, 0))
    monkeypatch.setattr(portal, "now", lambda: datetime(2026,11,17,12,tzinfo=KST))
    assert portal.refresh() is None and not calls
    monkeypatch.setattr(portal, "now", lambda: datetime(2026,11,22,12,tzinfo=KST))
    assert portal.refresh() == (1,0,0) and len(calls) == 1
    cfg["portal_import"]["imported_at"] = "2026-11-22T12:00:00+09:00"
    assert portal.refresh() is None and len(calls) == 1
