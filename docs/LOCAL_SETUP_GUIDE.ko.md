# Windows · Codex 설치와 개인 설정

Windows PowerShell에서 저장소 폴더를 연다. WSL은 필요하지 않다.
Python 3.10 이상·Git·Codex CLI가 필요하며, 본인 인증은 직접 한다.

```powershell
bin\setup.cmd
codex login status
bin\pa.cmd doctor
```

인증이 없으면 `codex login`을 실행한다. 인증 파일이나 토큰을 출력하거나 채팅에 붙이지 않는다.
제한된 실행 도구에서 홈 접근 오류가 나더라도 실제 사용자 PowerShell에서는 정상일 수 있다.
`CODEX_BIN`으로 실행 파일을 지정할 수 있고 `.env`의 `PA_AI`는 `codex`다.

설치는 가상환경·의존성·Chromium, 기존 파일을 보존하는 개인 설정, 연결 프로젝트의 AGENTS와
`assistant.local.code-workspace`를 준비한다. 기존 규칙이 있으면 임의로 덮어쓰지 않는다.
이전 안내 파일만 있으면 원문을 새 AGENTS로 복사하며 기존 원문도 보존한다.

## 하나씩 채우기

1. 학교를 확인한다. 현재 구현은 제주대 전용이다.
2. Canvas에서 본인 액세스 토큰을 발급하고 `.env`의 `CANVAS_TOKEN`에 직접 저장한다.
3. `config/timetable.yaml`에 학기·시간표, `courses.yaml`에 실제 과목명을 입력한다.
4. `config/assistant.yaml`의 `projects`에 실제 공부·보고서·퀴즈 경로를 설정한다.
   보고서 학번·이름은 `student.id`, `student.name`에 직접 저장한다.
5. [Google 안내](google-calendar-setup.md)에 따라 `credentials.json`을 준비하고
   `bin\pa.cmd google-login`으로 본인 계정을 인증한다.
6. `bin\pa.cmd sync-timetable --dry-run`을 확인한다. 실제 등록 명령은 `bin\pa.cmd sync-timetable`이다.
7. 준비 후 `bin\pa.cmd run --full`, `bin\pa.cmd watch`를 실행한다.

대시보드는 http://localhost:8765 이며 설정이 부족하면 남은 준비를 표시한다.
기본 설치의 과목과 학습 한도는 견본이다. 생활 패턴을 임의로 추정해 바꾸지 않는다.
프로젝트 경로를 변경한 뒤에는 엔진을 재시작하고 setup으로 개인 워크스페이스를 갱신한다.
학교·Google 인증이 완료되기 전에는 실제 학사 일정 연동을 완료로 보지 않는다.

## 검증

```powershell
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -X utf8 scripts/test.py
bin\pa.cmd doctor --browser
bin\pa.cmd doctor --ai --browser
```

마지막 명령은 가상 공지·PDF·과제로 실제 Codex를 세 번 호출한다. 개인 DB·실제 학교는 사용하지 않는다.
스캔 PDF·HWP 등은 OCR 처리 또는 PDF 변환이 필요하다. 읽을 수 없는 자료를 읽었다고 간주하지 않는다.

## 선택 기능

LearningX는 `bin\pa.cmd browser login`으로 별도 인증한다. 평소 학교 브라우저 로그인이 끊길 수 있다.
퀴즈 앱은 별도로 준비하고 실제 경로를 연결한다.
Windows 자동 시작은 `scripts/windows/register-task.ps1`을 먼저 `-ValidateOnly`로 점검한다.
등록은 사용자가 원할 때 실행한다. PC 로그인 계정의 Codex 인증과 실행 경로를 사용한다.
휴대폰 게시·GitHub Pages는 별도 선택 기능이며 일반 코드 push와 함께 켜지지 않는다.

이전 WSL 준비 파일은 역사 자료로 보관하며 현재 설치에 사용하지 않는다.
