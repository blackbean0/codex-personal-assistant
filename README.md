# Codex Personal Assistant

Windows에서 실행하는 Codex 중심 개인 비서. Canvas 과제·강의·공지, 개인 할 일과 시간표를 모아
학습 계획과 대시보드를 만든다. AI 버튼으로 자료 요약·공지 정리·보고서 초안을 생성한다.

## 설치와 실행

Python 3.10 이상, Git, Codex CLI가 필요하다. VS Code는 선택이다. WSL은 필요하지 않다.

```powershell
git clone https://github.com/blackbean0/codex-personal-assistant.git
cd codex-personal-assistant
bin\setup.cmd
codex login
bin\pa.cmd doctor
bin\pa.cmd watch
```

대시보드는 http://localhost:8765 이다. 학교·Google 설정이 없어도 준비 상태를 보여 준다.
학교 연동은 현재 **제주대학교 Canvas·LearningX 전용**이다. 다른 학교면 먼저 연동 코드를 조정해야 한다.
전체 절차는 [Windows 설치 안내](docs/LOCAL_SETUP_GUIDE.ko.md)를 따른다.

학교 로그인 후 `bin\pa.cmd portal-timetable --year 2026 --term 20 --apply`로 본인 시간표를 가져올 수 있다.
포털의 실제 날짜·시각을 사용하고 휴강은 제외하며 보강은 실제 날짜에 둔다. 시각이 없는 과목은 임의로 배치하지 않는다.
Google Calendar 시간표 동기화도 이 날짜별 기록을 사용한다.
가져온 시간표는 전체 동기화 때 포털에서 다시 조회한다. Google 인증이 준비되면 수업 캘린더도
변경분을 반영하며, 취소된 미래 수업만 제거하고 과거 수업과 사용자가 만든 일정은 보존한다.
학교 시간표만 주 1회 읽으려면 개인 설정의 `portal_import.refresh_weekday: sun`을 사용한다.
엔진이 켜져 있는 일요일에 한 번 성공적으로 조회하며, 나머지 날에는 저장한 시간표를 사용한다.
Google Calendar의 계획·마감 갱신 주기는 이 설정의 영향을 받지 않는다.

## 개인 설정

설치 프로그램은 기존 설정과 자료를 보존한다. 다음 파일은 Git에서 제외한다.

| 파일 | 용도 |
|---|---|
| `config/assistant.yaml` | 공부·보고서·퀴즈 프로젝트 위치, 보고서 학번·이름 |
| `config/profile.md` | Codex가 읽는 사용자 소개와 선호 |
| `config/timetable.yaml` | 학기·수업·학습 시간·알림 |
| `config/courses.yaml` | 실제 과목과 자료·노트 폴더 대응 |
| `config/materials.yaml` | 자료 검색 범위·연결 규칙 |
| `.env` | `PA_AI=codex`, Canvas 토큰, 선택적 연동 비밀 값 |
| `credentials.json`, `token.json` | Google Calendar 앱 설정·본인 인증 |

프로젝트 경로의 기준은 `assistant.yaml`이다. 기존 `courses.yaml`의 경로는 최초 이전 시 보존한다.
기본값은 사용자 홈의 `study_system`, `report`, `quiz_system_project/pharmacy`다.
`assistant.local.code-workspace`는 실제 경로로 생성되는 개인용 VS Code 워크스페이스다.
퀴즈 프로젝트의 기본 지침만 설치되며 퀴즈 앱 자체는 별도로 연결해야 한다.

## Codex와 프로그램의 역할

- 채팅 비서는 `AGENTS.md`와 `.agents/skills/`를 사용한다. `CODEX.md`나 Claude 설치는 필요하지 않다.
- `.codex/config.toml`에는 저장소 실행 기본값만 둔다. Codex 인증은 사용자 홈에 유지한다.
- 일정 계산·파일 저장은 Python이 수행한다. AI는 버튼을 눌렀을 때 `codex exec`로 별도 호출한다.
- AI 실행은 읽기 전용·임시 세션이다. 파일 읽기 제한이나 비밀 격리를 완전히 보장하는 옵션은 아니다.
- 선택한 PDF·TXT·MD·CSV·DOCX·PPTX의 본문을 추출해 전달한다. 스캔 PDF는 OCR 처리가 필요하다.
- 공지 응답은 JSON Schema로 검증한다. 과제 제외 후보는 사용자가 결정한다.
- 보고서 교체는 정상 응답을 검증한 후 진행하며 기존 파일은 `_old1` 등의 이름으로 보존한다.
- 진행 중·대기 중 작업을 취소할 수 있다. 엔진 중단으로 끊긴 AI 작업을 자동 재호출하지 않는다.
- 과제 제출·강의 재생·출석 처리는 사용자가 직접 한다.

## 진단과 개발

```powershell
bin\pa.cmd doctor                          # 설치·인증·개인 설정, 비밀 값 출력 없음
bin\pa.cmd doctor --browser                # 가상 DB로 대시보드 화면 검증
bin\pa.cmd doctor --ai --browser           # 가상 자료로 실제 Codex 3회 호출
.venv\Scripts\python.exe -X utf8 scripts/test.py
.venv\Scripts\python.exe scripts/check_public.py  # 스테이징한 파일의 공개 전 검사
```

AI 검증은 구독 사용량을 소비한다. 테스트는 실제 학교·Google 로그인과 실제 Codex 호출을 하지 않는다.
테스트 실행기는 Windows 사용자와 제한된 실행 도구가 서로의 임시 폴더 권한을 공유하지 않도록 매번 새 임시 폴더를 사용한다.
업데이트 후 `bin\setup.cmd`를 다시 실행하고 엔진을 재시작한다. DB 기록은 자동 이전한다.
개발 검증: Python 3.10 문법 검사, Windows 자동 시작 설정 검증,
실제 Codex를 통한 가상 공지·PDF·보고서 처리와 Chromium 대시보드 검증을 수행했다.
Windows 백그라운드 엔진은 전용 감독 프로세스가 로그와 코드 재시작(종료 코드 75)을 처리한다.
OneDrive 경로에서도 검증했으나 여러 PC가 같은 SQLite DB를 동시에 실행하지 않도록 한다.

사용법은 [docs/usage.md](docs/usage.md), 현재 남은 설정은 [docs/TODO.md](docs/TODO.md),
공개 전 점검은 [docs/release.md](docs/release.md)를 참고한다.
기존 설계 문서는 과거 배경 자료이며 현재 실행 기준은 이 README·AGENTS·설정 견본이다.

원본은 [Rhombusbork/personal_assistant_release](https://github.com/Rhombusbork/personal_assistant_release)다.
개인 설정·자료·인증은 코드 저장소와 별도로 보관한다. 일반 코드 push는 모바일 게시·외부 배포와 별개다.
