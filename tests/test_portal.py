from datetime import date

from pa.portal import parse_slots
from pa.sync_timetable import build_event


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
