# AI Software Development Project Guide (v1.0.0)

> **Domain:** 업무 자동화 · Python 데스크톱/웹 앱 개발 · 화학/분석 업무 도구  
> **Use Case:** 사용자가 프로그램을 개발할 때 Claude Code, ChatGPT, Cursor 등 AI 코딩 도구가 따라야 할 프로젝트 운영 규칙  
> **Example Project:** MSDS 경고표지 자동 생성 프로그램, 분석 데이터 처리 프로그램, 품질/연구소 업무 자동화 툴

---

## Project Configuration

**Project Name:** [INSERT PROJECT NAME]  
**Main Purpose:** [예: MSDS PDF에서 경고표지 자동 생성 / 유리 조성 예측 / 분석 데이터 자동 정리]  
**Target User:** [예: 연구소 분석 담당자 / 품질팀 / 현장 작업자 / 비전공 사무직 사용자]  
**Platform:** [Windows desktop / Web app / Internal shared-folder app / Mobile / etc.]  
**Main Language:** [Python / JavaScript / etc.]  
**Framework:** [Flet / Streamlit / PySide6 / FastAPI / etc.]  
**Distribution Method:** [EXE 배포 / 사내 공유폴더 / GitHub / 웹 배포 / etc.]  
**Current Version:** [v0.1.0 / v1.0.0 등]  

> ⚠️ 새 프로젝트를 시작할 때마다 이 영역을 먼저 채운다.

---

## Session Start Protocol

AI 코딩 도구를 다시 실행하면, 먼저 현재 프로젝트 상태를 파악한 뒤 작업을 시작한다.

### 동작 순서

1. 현재 폴더의 프로젝트 구조를 확인한다.
2. 다음 파일이 있으면 먼저 읽는다.
   - `README.md`
   - `CHANGELOG.md`
   - `TODO.md`
   - `PROJECT_PLAN.md`
   - `DEV_LOG.md`
   - `requirements.txt`
   - `pyproject.toml`
   - `main.py`
   - 주요 실행 파일
3. 현재 상태를 3~5줄로 요약한다.
   - 지금까지 구현된 기능
   - 최근 수정 사항
   - 현재 오류 또는 미완성 항목
   - 다음에 할 일
4. 사용자가 구체적인 작업을 지시했다면 바로 그 작업을 우선한다.
5. 사용자가 “이어서 하자”, “어디까지 했지”, “다음 단계”라고 말하면 위 파일을 읽고 현재 상황부터 정리한다.

---

## Recommended Project Structure

```text
project/
├── README.md                 # 프로젝트 소개, 실행 방법, 사용 방법
├── CLAUDE.md                 # AI 코딩 도구용 작업 규칙
├── PROJECT_PLAN.md           # 전체 개발 계획
├── TODO.md                   # 해야 할 일 목록
├── CHANGELOG.md              # 버전별 변경 이력
├── DEV_LOG.md                # 개발 중 문제/해결 기록
├── requirements.txt          # Python 패키지 목록
├── .gitignore                # Git 제외 파일
├── src/                      # 실제 소스코드
│   ├── main.py               # 실행 진입점
│   ├── app.py                # UI 구성
│   ├── config.py             # 설정값
│   ├── services/             # 핵심 로직
│   ├── utils/                # 공통 함수
│   └── assets/               # 이미지, 아이콘, 리소스
├── tests/                    # 테스트 코드
├── data/                     # 샘플 데이터
├── logs/                     # 오류 로그
├── docs/                     # 사용자 매뉴얼, 개발 문서
├── build/                    # 빌드 중간 파일
├── dist/                     # 빌드 결과물
└── release/                  # 사용자 배포용 파일
```

---

## File Roles

| File/Folder | Purpose |
|---|---|
| `README.md` | 사용자가 프로그램을 이해하고 실행할 수 있게 설명 |
| `CLAUDE.md` | AI가 개발할 때 지켜야 할 규칙 |
| `PROJECT_PLAN.md` | 기능, 개발 단계, 우선순위 정리 |
| `TODO.md` | 남은 작업 목록 |
| `CHANGELOG.md` | 버전별 변경 사항 기록 |
| `DEV_LOG.md` | 오류, 해결 과정, 의사결정 기록 |
| `src/` | 실제 프로그램 코드 |
| `tests/` | 테스트 코드 |
| `data/` | 테스트용 샘플 파일 |
| `logs/` | 실행 오류 및 실패 케이스 저장 |
| `docs/` | 사용자 설명서, 배포 가이드 |
| `release/` | 최종 배포 파일 |

---

## Critical Rules

### 1. 사용자의 현재 코드를 우선한다

- 새 코드를 마음대로 전체 재작성하지 않는다.
- 기존 구조와 변수명을 먼저 파악한다.
- 수정은 가능한 한 최소 범위로 한다.
- 전체 파일을 바꾸기보다 “어디를 어떻게 바꿀지”를 먼저 설명한다.
- 사용자가 초보자라면 복붙 가능한 코드 블록으로 제공한다.

### 2. 실행 가능한 코드만 제안한다

- 예시용 가짜 함수, 존재하지 않는 변수, 미완성 코드를 넣지 않는다.
- 코드를 제안하기 전 현재 파일에 해당 함수나 변수가 있는지 확인한다.
- 필요한 import가 있으면 함께 안내한다.
- 들여쓰기, 괄호, f-string 중괄호 오류를 특히 주의한다.

### 3. 오류 해결은 원인 → 수정 위치 → 수정 코드 순서로 설명한다

오류가 발생하면 항상 다음 순서로 답한다.

1. 오류 원인
2. 문제가 생긴 코드 위치
3. 수정 전 코드
4. 수정 후 코드
5. 다시 실행할 명령어
6. 정상 동작 확인 방법

### 4. 기능 추가 전 영향 범위를 확인한다

새 기능을 추가하기 전 다음을 확인한다.

- 기존 기능이 깨질 가능성
- UI에 표시되는 위치
- 저장 파일 형식 변경 여부
- 배포 파일에 추가 리소스가 필요한지
- Git에 포함해야 하는 파일과 제외해야 하는 파일

### 5. 버전 관리를 반드시 한다

기능 추가, 오류 수정, 배포 전에는 버전을 기록한다.

| 상황 | 예시 |
|---|---|
| 작은 수정 | `v1.3.1` |
| 기능 추가 | `v1.4.0` |
| 큰 구조 변경 | `v2.0.0` |
| 배포 파일 | `program_name_v1.4.0.exe` |

`CHANGELOG.md`에는 다음 형식으로 기록한다.

```md
## v1.4.0 - 2026-06-08

### Added
- 새 기능

### Fixed
- 수정한 오류

### Changed
- 변경된 동작
```

### 6. 배포 파일과 개발 파일을 분리한다

- 개발용 코드와 사용자 배포용 파일을 섞지 않는다.
- `build/`, `dist/`, `release/`, `*.exe`, `*.zip`은 기본적으로 Git에 올리지 않는다.
- 배포용 폴더에는 사용자가 실행해야 할 파일만 둔다.
- Python이 없는 사용자도 실행할 수 있는지 확인한다.

추천 `.gitignore`:

```gitignore
__pycache__/
*.pyc
.env
venv/
.venv/

build/
dist/
release/
*.exe
*.zip

logs/
temp/
*.log
```

### 7. 테스트 없는 수정은 완료로 보지 않는다

수정 후 최소한 다음을 확인한다.

- 프로그램 실행 여부
- 주요 버튼 클릭 여부
- 샘플 파일 처리 여부
- 오류 메시지 여부
- 결과 파일 생성 여부
- 배포 환경에서 실행 가능 여부

### 8. 사용자가 이해할 수 있는 언어로 설명한다

- 전문 용어는 쉽게 풀어서 설명한다.
- “이 코드는 무엇을 하는지”를 짧게 설명한다.
- 복붙 위치를 명확히 알려준다.
- 긴 코드를 줄 때는 “기존 코드 전체 교체”인지 “일부 추가”인지 분명히 말한다.

---

## Development Workflow

```text
Phase 1: 요구사항 정리
├── 사용 목적 확인
├── 사용자와 사용 환경 정의
├── 입력 파일과 출력 결과 정의
├── 필수 기능과 나중 기능 구분
└── PROJECT_PLAN.md 작성

Phase 2: 기본 구조 설계
├── 폴더 구조 생성
├── main 실행 파일 생성
├── UI 틀 구성
├── 핵심 로직 파일 분리
└── README.md 초안 작성

Phase 3: 핵심 기능 구현
├── 입력 파일 불러오기
├── 데이터 추출/분석/변환
├── 결과 미리보기
├── 결과 저장/출력
└── 오류 처리

Phase 4: 사용자 편의 기능
├── 버튼/입력창/선택 옵션 개선
├── 글자 크기, 레이아웃 조정
├── 설정값 저장
├── 실패 파일 로그 저장
└── 사용 가이드 표시

Phase 5: 테스트
├── 정상 파일 테스트
├── 실패 파일 테스트
├── 예외 상황 테스트
├── Windows 경로 테스트
└── 배포 환경 테스트

Phase 6: 배포
├── requirements 정리
├── PyInstaller/Flet 등으로 빌드
├── release 폴더 생성
├── 실행 방법 문서화
└── 사용자 피드백 수집

Phase 7: 유지보수
├── 실패 로그 분석
├── 사용자 요청 정리
├── 기능 개선
├── 버전 업데이트
└── CHANGELOG.md 기록
```

---

## Coding Standards

### Python 기본 규칙

- 함수는 하나의 역할만 하게 만든다.
- 긴 코드는 기능별 함수로 나눈다.
- 파일 경로는 `pathlib.Path` 사용을 우선한다.
- 오류 가능성이 있는 부분은 `try-except`로 처리한다.
- 사용자가 보는 오류 메시지는 쉽게 작성한다.

예시:

```python
from pathlib import Path

def load_text_file(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

    return path.read_text(encoding="utf-8")
```

### UI 개발 규칙

- 사용자가 가장 많이 쓰는 기능을 위쪽에 배치한다.
- 버튼 이름은 동작이 바로 이해되게 쓴다.
- 오류는 빨간 경고, 안내는 짧은 문장으로 표시한다.
- 개발자용 기능은 배포용에서 숨길 수 있게 한다.

예시:

```python
SHOW_ADMIN = False

if SHOW_ADMIN:
    show_admin_panel()
```

---

## Error Handling Rules

### 오류 메시지 작성 원칙

나쁜 예:

```text
Exception occurred.
```

좋은 예:

```text
PDF에서 제품명을 찾지 못했습니다. 제품명을 직접 입력한 뒤 다시 생성하세요.
```

### 실패 로그 저장

프로그램이 자동 처리에 실패하면 원인을 남긴다.

```text
logs/
├── failed_files/
├── error_log.txt
└── statistics.json
```

기록할 항목:

- 파일명
- 실패 시간
- 실패 원인
- 추출된 원문 일부
- 사용자가 수정한 값

---

## Testing Checklist

배포 전 반드시 확인한다.

```md
# Test Checklist

## 실행
- [ ] 내 PC에서 실행된다.
- [ ] Python이 없는 PC에서도 실행된다.
- [ ] 공유폴더에서 실행된다.
- [ ] 32bit/64bit Windows 호환성을 확인했다.

## 기능
- [ ] 정상 샘플 파일이 처리된다.
- [ ] 비정상 샘플 파일에서 프로그램이 멈추지 않는다.
- [ ] 결과물이 저장된다.
- [ ] UI 입력값이 결과에 반영된다.

## 배포
- [ ] 필요한 이미지/리소스가 포함되었다.
- [ ] 실행 파일명이 버전과 일치한다.
- [ ] README에 실행 방법이 적혀 있다.
- [ ] CHANGELOG가 업데이트되었다.
```

---

## Git Rules

### 작업 저장 순서

```bash
git status
git add README.md CHANGELOG.md src/
git commit -m "feat: add label preview layout"
git push
```

### 커밋 메시지 규칙

| Type | Meaning |
|---|---|
| `feat:` | 새 기능 |
| `fix:` | 오류 수정 |
| `docs:` | 문서 수정 |
| `refactor:` | 구조 개선 |
| `test:` | 테스트 추가 |
| `chore:` | 기타 정리 |

예시:

```bash
git commit -m "fix: prevent missing precautionary statements in PDF parsing"
```

---

## Distribution Rules

### PyInstaller 예시

```bash
py -m PyInstaller --onefile --noconsole ^
  --add-data "assets;assets" ^
  --name "my_program_v1.0.0" ^
  src/main.py
```

### 배포 폴더 예시

```text
release/
└── my_program_v1.0.0/
    ├── my_program_v1.0.0.exe
    ├── README_실행방법.txt
    ├── sample/
    └── assets/
```

---

## Program Documentation Template

`README.md`는 다음 구조로 작성한다.

```md
# 프로그램명

## 1. 프로그램 목적
이 프로그램은 무엇을 자동화하는지 설명한다.

## 2. 주요 기능
- 기능 1
- 기능 2
- 기능 3

## 3. 실행 방법
1. exe 파일 실행
2. 파일 선택
3. 결과 확인
4. 저장 또는 출력

## 4. 주의사항
- 지원 파일 형식
- 오류가 날 수 있는 경우
- 문의할 사람

## 5. 버전
현재 버전: v1.0.0
```

---

## Quick Commands

| Command | Action |
|---|---|
| `현재 프로젝트 상태 정리해줘` | README, CHANGELOG, TODO를 읽고 상태 요약 |
| `오류 원인 찾아줘` | traceback 기준으로 원인과 수정 위치 분석 |
| `이 코드에서 수정 위치 알려줘` | 현재 코드 기준으로 복붙 위치 안내 |
| `기능 추가해줘` | 영향 범위 확인 후 최소 수정 코드 제안 |
| `배포파일 만들어줘` | 빌드 방식, 명령어, release 구조 안내 |
| `README 작성해줘` | 사용자용 설명서 작성 |
| `CHANGELOG 작성해줘` | 버전별 변경 이력 작성 |
| `Git 저장 방법 알려줘` | add/commit/push 명령어 안내 |
| `초보자 기준으로 설명해줘` | 복붙 위치 중심으로 쉽게 설명 |
| `리팩토링해줘` | 기능 유지하면서 구조 개선 |

---

## MSDS Label App Specific Rules

MSDS 경고표지 프로그램을 개발할 때는 다음을 추가로 지킨다.

### 핵심 기능

- PDF에서 제품명, 신호어, 그림문자, 유해위험문구, 예방조치문구, 공급자 정보를 추출한다.
- 사용자가 추출 결과를 직접 수정할 수 있게 한다.
- 라벨 규격별로 출력 레이아웃을 다르게 적용한다.
- 9칸, 2칸, 24칸 라벨을 구분한다.
- 100 ml 이하/초과에 따른 문구 작성 가이드를 표시한다.

### 개발 시 주의사항

- PDF 회사별 양식이 다르므로 실패 로그를 반드시 남긴다.
- 자동 추출 실패 시 프로그램이 멈추지 않고 직접 입력으로 넘어가야 한다.
- 배포용에서는 품질관리/개발자 탭을 숨길 수 있어야 한다.
- 공유폴더 실행 환경을 고려한다.
- Python이 없는 사용자도 실행할 수 있어야 한다.

### 법규 관련 주의

- 프로그램은 경고표지 작성을 보조하는 도구다.
- 최종 법적 적합성 판단은 사용자가 MSDS와 관련 법규를 확인해야 한다.
- 자동 생성 결과에는 “MSDS 원문 확인 필요” 안내를 표시하는 것이 좋다.

---

## Final Rule

AI는 단순히 코드를 많이 작성하는 것이 아니라, 사용자가 실제로 실행하고 배포할 수 있는 프로그램을 완성하는 것을 목표로 한다.

따라서 모든 답변은 다음 기준을 만족해야 한다.

1. 사용자가 바로 따라 할 수 있어야 한다.
2. 현재 코드와 충돌하지 않아야 한다.
3. 실행 가능해야 한다.
4. 배포와 유지보수를 고려해야 한다.
5. 변경 내용이 기록되어야 한다.
