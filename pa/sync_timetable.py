"""config/timetable.yaml 의 수업을 Google Calendar 의 매주 반복 일정으로 동기화.

여러 번 실행해도 중복 생성되지 않고, 기존 일정은 갱신된다.
사용법: python -m pa.sync_timetable [--dry-run]
"""
import argparse
from datetime import date, datetime, timedelta

from pa.config import load_timetable
from pa.gcal import get_or_create_calendar, get_service
from pa.model import now, parse_dt

TZ = "Asia/Seoul"
CALENDAR_NAME = "수업 시간표"
DAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
RRULE_DAYS = {"mon": "MO", "tue": "TU", "wed": "WE", "thu": "TH", "fri": "FR", "sat": "SA", "sun": "SU"}


def build_event(c, sem_start, sem_end):
    if c.get("date"):
        day = date.fromisoformat(c["date"]).isoformat()
        key = f"{c['name']}|{day}|{c['start']}"
        return key, {"summary": c["name"], "location": c.get("location", ""),
                     "start": {"dateTime": f"{day}T{c['start']}:00", "timeZone": TZ},
                     "end": {"dateTime": f"{day}T{c['end']}:00", "timeZone": TZ},
                     "extendedProperties": {"private": {"pa_source": "timetable", "pa_key": key}}}
    first = sem_start + timedelta(days=(DAYS[c["day"]] - sem_start.weekday()) % 7)
    # 종강일 23:59:59 KST = 14:59:59 UTC
    until = sem_end.strftime("%Y%m%dT145959Z")
    key = f"{c['name']}|{c['day']}|{c['start']}"
    return key, {
        "summary": c["name"],
        "start": {"dateTime": f"{first.isoformat()}T{c['start']}:00", "timeZone": TZ},
        "end": {"dateTime": f"{first.isoformat()}T{c['end']}:00", "timeZone": TZ},
        "recurrence": [f"RRULE:FREQ=WEEKLY;BYDAY={RRULE_DAYS[c['day']]};UNTIL={until}"],
        "extendedProperties": {"private": {"pa_source": "timetable", "pa_key": key}},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Google 에 쓰지 않고 출력만")
    args = parser.parse_args()

    cfg = load_timetable()
    sem_start = date.fromisoformat(cfg["semester_start"])
    sem_end = date.fromisoformat(cfg["semester_end"])
    events = [build_event(c, sem_start, sem_end) for c in cfg.get("class_dates", cfg.get("classes", []))]

    if args.dry_run:
        for key, ev in events:
            print(key, ev["start"]["dateTime"], (ev.get("recurrence") or ["날짜별 수업"])[0])
        return
    created, updated, removed = sync(get_service(), cfg)
    print(f"시간표 동기화: 새로 {created} · 갱신 {updated} · 취소 반영 {removed}")


def sync(service, cfg=None):
    cfg = cfg or load_timetable()
    sem_start, sem_end = (date.fromisoformat(cfg[k]) for k in ("semester_start", "semester_end"))
    events = dict(build_event(c, sem_start, sem_end) for c in cfg.get("class_dates", cfg.get("classes", [])))
    cal_id = get_or_create_calendar(service, CALENDAR_NAME, TZ)
    existing, token = {}, None
    while True:
        result = service.events().list(calendarId=cal_id, privateExtendedProperty="pa_source=timetable",
                                       singleEvents=False, maxResults=2500, **({"pageToken": token} if token else {})).execute()
        for event in result.get("items", []):
            key = event.get("extendedProperties", {}).get("private", {}).get("pa_key")
            if key:
                existing[key] = event
        token = result.get("nextPageToken")
        if not token:
            break
    created = updated = removed = 0
    for key, ev in events.items():
        previous = existing.get(key)
        if previous:
            same = all(previous.get(k, "") == ev.get(k, "") for k in ("summary", "location", "recurrence"))
            same = same and all(parse_dt(previous[k]["dateTime"]) == parse_dt(ev[k]["dateTime"]) for k in ("start", "end"))
            if not same:
                service.events().update(calendarId=cal_id, eventId=previous["id"], body=ev).execute()
                updated += 1
        else:
            service.events().insert(calendarId=cal_id, body=ev).execute()
            created += 1
    # Reconcile only this application's future dated lessons. Never remove user events or past lessons.
    if "class_dates" in cfg:
        for key, previous in existing.items():
            if key not in events and not previous.get("recurrence") and previous.get("start", {}).get("dateTime", "")[:10] >= now().date().isoformat():
                service.events().delete(calendarId=cal_id, eventId=previous["id"]).execute()
                removed += 1
    return created, updated, removed


if __name__ == "__main__":
    main()
