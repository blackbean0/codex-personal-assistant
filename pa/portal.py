"""Read-only timetable import from Jeju University's authenticated portal."""
import argparse
import html
import re
import shutil
from datetime import date, datetime

import yaml

from pa.config import ROOT, load_timetable
from pa.model import now

URL = "https://portal.jejunu.ac.kr/classwork/management/timetable.htm"


def parse_slots(rows):
    """Return exact dated lessons; cancelled and untimed records are never invented."""
    lessons, untimed, cancelled = {}, set(), 0
    for row in rows:
        if str(row.get("cclctYn", "N")).upper() == "Y":
            cancelled += 1
            continue
        name = html.unescape(str(row.get("sbjctNm") or "")).strip()
        if not name:
            continue
        raw_date = str(row.get("lsnYmd") or "")
        day = datetime.strptime(raw_date, "%Y%m%d").date().isoformat()
        start, end = row.get("bgngHr"), row.get("endHr")
        if not start or not end:
            untimed.add(name)
            continue
        if not all(re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", str(v)) for v in (start, end)) or start >= end:
            raise ValueError("포털 수업 시각을 해석할 수 없습니다. 설정은 변경하지 않았습니다")
        lesson = {"name": name, "date": day, "start": start, "end": end,
                  "location": str(row.get("lctrmNm") or row.get("roomNm") or "")}
        lessons[(day, name, start, end)] = lesson
    return sorted(lessons.values(), key=lambda x: (x["date"], x["start"], x["name"])), sorted(untimed), cancelled


def fetch(year, term):
    from playwright.sync_api import sync_playwright
    from pa import browser
    with sync_playwright() as p:
        ctx = browser._context(p, headless=True)
        try:
            response = ctx.request.get(URL, params={"act": "table", "_out": "json", "estblScyr": str(year),
                "estblSctm": str(term), "sttLsnYmd": f"{year}0101", "endLsnYmd": f"{year}1231"}, timeout=60000)
            if response.status != 200:
                raise RuntimeError("학교 포털 인증과 접속 상태를 확인하세요")
            try:
                rows = response.json()["classTables"]
            except (ValueError, KeyError):
                raise RuntimeError("포털 로그인이 필요하거나 시간표 응답 형식이 바뀌었습니다") from None
            if not isinstance(rows, list) or not rows:
                raise ValueError("선택한 학기에 시간표가 없습니다. 기존 설정을 보존합니다")
            return rows
        finally:
            ctx.close()


def apply(rows, year, term):
    lessons, untimed, cancelled = parse_slots(rows)
    if not lessons:
        raise ValueError("시각이 확인된 수업이 없어 기존 설정을 보존합니다")
    if any(date.fromisoformat(x["date"]).year != year for x in lessons):
        raise ValueError("조회 연도와 수업 날짜가 일치하지 않습니다")
    path = ROOT / "config/timetable.yaml"
    cfg = load_timetable()
    backup = ROOT / "data/config-backups" / ("timetable-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".yaml")
    backup.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, backup)
    cfg["classes"] = []  # Exact dates take precedence over repeated sample lessons.
    cfg["class_dates"] = lessons
    cfg["semester_start"] = min(x["date"] for x in lessons)
    cfg["semester_end"] = max(x["date"] for x in lessons)
    old_policy = cfg.get("portal_import") or {}
    cfg["portal_import"] = {"year": year, "term": term, "imported_at": now().isoformat(timespec="seconds"),
                            "cancelled_slots_skipped": cancelled, "untimed_courses": untimed,
                            "refresh_on_full_sync": True,
                            "source": URL}
    if old_policy.get("refresh_weekday") is not None:
        cfg["portal_import"]["refresh_weekday"] = old_policy["refresh_weekday"]
    path.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return len(lessons), len(untimed), cancelled


def refresh():
    cfg = load_timetable().get("portal_import") or {}
    if not cfg.get("refresh_on_full_sync"):
        return None
    weekday = cfg.get("refresh_weekday")
    if weekday is not None:
        days = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
        if weekday not in days:
            raise ValueError("포털 시간표 확인 요일 설정이 올바르지 않습니다")
        current = now()
        if current.weekday() != days.index(weekday) or str(cfg.get("imported_at", ""))[:10] == current.date().isoformat():
            return None
    return apply(fetch(int(cfg["year"]), int(cfg["term"])), int(cfg["year"]), int(cfg["term"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=date.today().year)
    parser.add_argument("--term", type=int, choices=(10, 11, 20, 21), required=True)
    parser.add_argument("--apply", action="store_true", help="백업 후 개인 시간표 설정에 저장")
    args = parser.parse_args(argv)
    rows = fetch(args.year, args.term)
    lessons, untimed, cancelled = parse_slots(rows)
    if args.apply:
        apply(rows, args.year, args.term)
    print(f"포털 시간표: 수업 {len(lessons)}교시 · 휴강 제외 {cancelled}교시 · 시각 미정 과목 {len(untimed)}개")
    print("개인 설정 저장 완료" if args.apply else "조회만 완료 (--apply로 저장)")
