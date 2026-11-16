# Google Calendar 연결 — Windows

이 비서는 본인 Google Cloud 프로젝트의 데스크톱 OAuth 클라이언트를 사용한다.
로그인 비밀번호와 JSON 파일 내용은 채팅·GitHub에 공유하지 않는다.
공식 절차: https://developers.google.com/workspace/calendar/api/quickstart/python

## 1. Google Cloud 프로젝트

1. https://console.cloud.google.com/projectcreate 를 연다.
2. 연결할 Google 계정으로 로그인한다.
3. 프로젝트 이름은 `codex-personal-assistant`처럼 정하고 **만들기**를 누른다.
4. 상단 프로젝트 선택에서 방금 만든 프로젝트가 선택됐는지 확인한다.

## 2. Calendar API 사용 설정

1. 왼쪽 메뉴 **API 및 서비스 → 라이브러리**를 연다.
2. **Google Calendar API**를 검색해 선택한다.
3. **사용**을 누른다. **관리**가 보이면 이미 켜진 상태다.

## 3. OAuth 앱 설정

1. **Google Auth Platform → 브랜딩(Branding)**을 연다.
2. **시작하기(Get started)**가 나오면 누른다.
3. 앱 이름을 `Codex 개인 비서`로 입력하고 지원 이메일에 본인 계정을 선택한다.
4. 개인 Google 계정에서 쓰는 경우 대상(Audience)은 **외부(External)**를 선택한다.
5. 연락처 이메일에 본인 이메일을 입력하고 약관을 확인한 후 생성한다.
6. **대상(Audience)**에서 앱이 테스트 상태라면 **테스트 사용자 추가**로
   실제 Calendar를 연결할 본인 Google 이메일을 추가한다.

학교·회사 계정 정책으로 앱 생성이나 동의가 제한되면 관리자 정책을 확인한다.
테스트 상태에서 Calendar 같은 범위를 요청한 OAuth 인증은 갱신 토큰이 만료될 수 있다.
앱 게시 상태 변경은 별도로 판단하며 자동 게시하지 않는다.

## 4. 데스크톱 OAuth JSON 만들기

1. **Google Auth Platform → 클라이언트(Clients)**를 연다.
2. **클라이언트 만들기(Create client)**를 누른다.
3. 애플리케이션 유형은 **데스크톱 앱(Desktop app)**을 선택한다.
4. 이름은 `Windows 개인 비서`처럼 지정하고 생성한다.
5. **JSON 다운로드**를 누른다. 클라이언트 상세 화면에서 다운로드할 수도 있다.
   상세 화면에서는 **클라이언트 보안 비밀번호** 행의 복사 아이콘 오른쪽에 있는
   **아래쪽 화살표(↓)**를 확인한다. `Add secret`은 다운로드 버튼이 아니다.
   화면·클라이언트 상태에 따라 생성 직후에만 비밀 값을 내려받을 수 있다.
   기존 비밀 값을 다시 받을 수 없다는 안내가 나오면 새 비밀 값 또는 새 데스크톱 클라이언트가 필요하므로 안내 문구를 확인한다.
6. 다운로드한 파일을 이 저장소 루트의 `credentials.json`으로 저장한다.
   파일 내용을 복사해 채팅에 붙이지 않는다. 다운로드 위치만 알려주면 로컬에서 옮길 수 있다.

## 5. 본인 로그인과 연결 확인

```powershell
bin\pa.cmd google-login
```

평소 브라우저가 열리면 Calendar를 연결할 계정을 선택하고 요청 권한을 확인해 허용한다.
본인이 만든 테스트 앱의 경고 화면이 나오면 앱 이름과 프로젝트를 먼저 확인한다.
성공하면 `token.json`이 로컬에 생성된다. 인증 URL과 토큰은 출력하지 않는다.

### 403 access_denied가 표시될 때

테스트 앱에서 로그인한 계정이 테스트 사용자로 등록되지 않은 경우에 발생할 수 있다.
같은 Google Cloud 프로젝트의 **Google Auth Platform → 대상(Audience) → 테스트 사용자 → 사용자 추가**에서
실제로 Calendar를 연결할 Google 이메일을 추가하고 저장한다. 프로젝트 소유자도 목록을 확인한다.
그다음 `bin\pa.cmd google-login`으로 새 인증을 시도한다. 이 설정만 바꿨다면 OAuth JSON을 다시 만들 필요는 없다.
이미 등록한 동일 계정에서도 거절되면 화면의 오류 설명과 학교·회사 계정의 관리자 정책을 확인한다.

연결 후 실제 시간표가 맞는지 확인하고 동기화한다.

```powershell
bin\pa.cmd sync-timetable --dry-run
bin\pa.cmd sync-timetable
bin\pa.cmd run --full
```

시간표 동기화는 Google에 **수업 시간표** 캘린더를 만들거나 갱신한다.
전체 동기화는 **학습 계획**, **마감**, **마감 알림** 캘린더를 사용할 수 있다.
등록한 Windows 감시 엔진은 저장된 인증을 사용하며 Google 로그인 화면을 자동으로 기다리지 않는다.
