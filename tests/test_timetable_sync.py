from datetime import timedelta

from pa import sync_timetable
from pa.model import now


class Call:
    def __init__(self, value):
        self.value = value

    def execute(self):
        return self.value


class Calendar:
    def __init__(self):
        self.data = {"user-event": {"id": "user-event", "summary": "private appointment"}}
        self.sequence = 0

    def events(self):
        return self

    def list(self, **kwargs):
        return Call({"items": [e for e in self.data.values() if e.get("extendedProperties", {}).get("private", {}).get("pa_source") == "timetable"]})

    def insert(self, calendarId, body):
        self.sequence += 1
        key = str(self.sequence)
        self.data[key] = dict(body, id=key)
        return Call(self.data[key])

    def update(self, calendarId, eventId, body):
        self.data[eventId] = dict(body, id=eventId)
        return Call(self.data[eventId])

    def delete(self, calendarId, eventId):
        return Call(self.data.pop(eventId))


def test_dated_sync_is_idempotent_and_preserves_user_events_and_history(monkeypatch):
    monkeypatch.setattr(sync_timetable, "get_or_create_calendar", lambda *args: "cal")
    today = now().date()
    lessons = [{"name": "Example", "date": (today + timedelta(days=n)).isoformat(), "start": "09:00", "end": "09:50"}
               for n in (-1, 1, 2)]
    cfg = {"semester_start": (today-timedelta(days=30)).isoformat(), "semester_end": (today+timedelta(days=30)).isoformat(),
           "class_dates": lessons}
    service = Calendar()
    assert sync_timetable.sync(service, cfg) == (3, 0, 0)
    assert sync_timetable.sync(service, cfg) == (0, 0, 0)
    cfg["class_dates"] = [lessons[-1]]
    assert sync_timetable.sync(service, cfg) == (0, 0, 1)
    assert "user-event" in service.data
    assert len(service.data) == 3  # Past lesson, retained future lesson and unrelated user appointment.
