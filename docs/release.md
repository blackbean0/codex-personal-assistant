# 코드 공개와 변경 점검

작업 지침은 `AGENTS.md`를 따른다. 완료하고 검증한 작업 단위마다 본인 `origin`에 커밋·push한다.
`upstream`은 원본 참고용이며 push하지 않는다. force push는 사용하지 않는다.

## 공개 전

1. `.venv\Scripts\python.exe -X utf8 scripts/test.py`
2. 화면 변경이 있으면 `bin\pa.cmd doctor --browser`
3. AI 계약 변경이 있으면 필요에 따라 `bin\pa.cmd doctor --ai --browser` (실제 구독 사용)
4. 개인 값을 제외하고 필요한 파일만 스테이징한다.
5. `.venv\Scripts\python.exe scripts/check_public.py`
6. `git diff --cached --stat`과 변경 내용을 검토하고 커밋·push한다.

검사 스크립트는 비밀 파일 경로와 일부 인증 패턴을 검사하며 모든 개인정보를 탐지하는 보장은 없다.
견본에는 개인 계정·학번·이름·개인 절대 경로를 넣지 않는다.
인증·실제 설정·학습 자료·DB·생성 워크스페이스는 Git 밖에 둔다.
DB를 바꿀 때 기존 기록 자동 이전과 반복 실행 안전성을 검증한다.
UTF-8, 한글·공백 경로, Windows 프로세스 종료, Python 3.10 문법을 유지한다.

웹사이트·GitHub Pages·모바일 일정 게시, Google 일정 쓰기, 자동 시작 등록은 코드 push와 별개다.
사용자 요청과 개인 설정을 갖춘 뒤 해당 기능을 실행한다. 원본 배포용 `bin/release`는 이 저장소에 없다.
