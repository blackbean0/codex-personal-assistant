# 남은 개인 설정

Windows·Codex 전환과 가상 데이터 검증은 완료했다. 이 문서는 배포용 일반 준비 목록이다.
현재 사용자의 로그인·시간표·학생 정보와 진행 상태는 Git 밖의 개인 설정과 `bin\pa.cmd doctor`로 확인한다.
실제 계정 연동은 아래 순서로 진행한다.

1. 제주대학교 계정 사용 여부를 확인한다. 다른 학교면 주소와 LearningX 호환성을 먼저 조정한다.
2. 본인 Canvas 토큰을 `.env`에 직접 저장한다. 채팅에 보내지 않는다.
3. `config/courses.yaml`을 실제 과목으로 채운다. 학교 로그인 후 `bin\pa.cmd portal-timetable --year <연도> --term 20 --apply`로 2학기 날짜별 시간표를 가져올 수 있다.
4. 보고서가 필요하면 `config/assistant.yaml`의 `student`를 직접 채운다.
5. Google Calendar 앱 설정 파일을 준비하고 `bin\pa.cmd google-login`으로 본인이 인증한다.
6. 시간표 dry-run을 확인한 뒤 실제 동기화한다.

선택: 기존 퀴즈 앱 연결, LearningX 로그인, Windows 자동 시작 등록, 휴대폰 화면 게시.
기본 설치가 만드는 퀴즈 지침 폴더는 완성된 퀴즈 앱이 아니다.
모바일 게시와 자동 시작은 일반 코드 변경 시 자동으로 켜지지 않는다.

## 완료된 전환

- `AGENTS.md`·`.agents/skills/` 단일 원본, Codex 전용 실행
- 공통 프로젝트 경로·개인 학생 정보 설정, 기존 설정과 DB 보존
- PDF·문서 본문 추출, 구조화된 공지 출력, 작업 취소·중단 처리
- 기존 보고서 보존 후 교체, 오류 내용 보호
- Windows 설치·진단·Chromium 검증·개인용 워크스페이스
- 실제 Codex로 가상 공지·PDF 요약·보고서 초안 전체 경로 검증
