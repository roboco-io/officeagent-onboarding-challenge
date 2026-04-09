# 템플릿 리포지토리 가이드

이 문서는 이 템플릿 리포지토리에 포함된 구성 요소와 설정을 설명합니다.

## 디렉토리 구조

```
.
├── README.md                  # 프로젝트 시작 가이드
├── CLAUDE.md                  # AI 에이전트(Claude Code) 지침
├── AGENTS.md → CLAUDE.md      # CLAUDE.md 심볼릭 링크
├── .githooks/                 # Git hook 디렉토리
├── docs/
│   ├── PRD.md                 # 과제 명세서
│   └── TEMPLATE_GUIDE.md      # 이 문서
├── sample-docs/               # 테스트용 샘플 문서
│   ├── company-policy.txt     # 사내 복리후생 안내
│   └── development-guide.md   # 개발 가이드
├── retrobot/                  # 자동 회고 시스템
│   ├── SKILL.md               # AI 에이전트용 회고 생성 지침
│   └── README.md              # Retrobot 사용법
└── .githooks/
    └── post-commit            # 커밋 후 자동 회고 훅
```

## 구성 요소 설명

### 1. 과제 명세 (`docs/PRD.md`)

채용 과제의 요구사항, 기술 조건, 평가 기준, 제출 방법을 정의합니다.

- 핵심 요구사항: 문서 수집, 질의응답(RAG), LLM 캐싱, 프롬프트 설계
- 언어/프레임워크 자유 선택
- LLM은 Claude Code SDK 또는 Codex CLI 사용 (구독 기반, API 키 불필요)

### 2. AI 에이전트 지침 (`CLAUDE.md` / `AGENTS.md`)

Claude Code 또는 Codex로 과제를 진행할 때, 에이전트가 프로젝트 맥락을 이해하도록 돕는 지침 파일입니다.

- 과제 개요 및 핵심 요구사항 요약
- 기술 조건 및 필수 산출물 안내
- Retrobot 설정 방법
- 평가 비중 정보

`AGENTS.md`는 `CLAUDE.md`의 심볼릭 링크로, Codex 등 다른 에이전트도 동일한 지침을 읽을 수 있습니다.

### 3. 샘플 문서 (`sample-docs/`)

과제 구현 시 테스트에 활용할 수 있는 예시 문서입니다.

| 파일 | 내용 |
|------|------|
| `company-policy.txt` | 교육비 지원, 재택근무, 연차 휴가, 건강검진, 경조사 지원 등 |
| `development-guide.md` | 코드 리뷰 정책, 브랜치 전략, 배포 프로세스, 장애 대응 등 |

### 4. Retrobot — 자동 회고 (`retrobot/`)

AI 에이전트의 작업 로그를 분석하여 KPT(Keep/Problem/Try) 회고를 자동 생성하는 시스템입니다.

**동작 흐름:**
1. 지원자가 `git commit` 실행
2. `.githooks/post-commit` 훅이 트리거
3. 훅이 `claude` 또는 `codex` CLI를 호출하며 `retrobot/SKILL.md` 지침을 전달
4. 에이전트가 `~/.claude/projects/` (또는 `~/.codex/`) 로그를 분석
5. KPT 회고 마크다운을 `retros/`에 생성하고 자동 커밋

**무한 루프 방지:** 커밋 메시지에 "Retrobot"이 포함되면 훅이 스킵됩니다.

**커스터마이징:** `retrobot/SKILL.md`를 편집하여 회고 형식을 자유롭게 변경할 수 있습니다.

### 5. Git Hook 설정 (`.githooks/`)

리포지토리에 포함된 `.githooks/` 디렉토리를 git hook 경로로 지정합니다.

```bash
git config core.hooksPath .githooks
```

이 설정은 로컬 git config에 저장되므로, 리포지토리를 클론할 때마다 1회 실행이 필요합니다.
윈도우/맥/리눅스 모두 동일하게 동작합니다.

## 시작 순서

```bash
# 1. 템플릿으로 비공개 리포지토리 생성 (GitHub UI에서)

# 2. 클론
git clone https://github.com/<your-id>/officeagent-onboarding-challenge.git
cd officeagent-onboarding-challenge

# 3. Git hook 설정 (Retrobot 활성화)
git config core.hooksPath .githooks

# 4. 과제 구현 시작
# ...

# 5. 제출 — serithemage를 Collaborator로 초대
```
