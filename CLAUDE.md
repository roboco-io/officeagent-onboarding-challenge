# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

OfficeAgent BE 채용 과제 — Document Q&A API. 문서를 업로드하면 내용을 분석하고, 사용자 질문에 대해 문서 근거 기반 답변을 생성하는 REST API 서버를 구현하는 과제 리포지토리.

## 핵심 요구사항

1. **문서 수집 (Ingestion)**: 문서 파일(PDF, TXT 등) 업로드 → 텍스트 추출 → 검색 가능한 형태로 저장. 최소 2개 포맷 지원.
2. **질의응답 (RAG)**: 업로드된 문서에서 관련 내용을 벡터 검색하고, LLM으로 답변 생성. 출처 포함 필수. 근거 없는 질문은 환각 없이 처리.
3. **LLM 응답 캐싱**: 동일/유사 질문 캐시, 캐시 히트 여부 응답에 포함, 문서 변경 시 관련 캐시 무효화.
4. **프롬프트 설계**: `PROMPT_DESIGN.md`에 프롬프트 설계 의도와 전략 문서화.

## 기술 조건

- **언어/프레임워크**: 자유 선택 (선택 이유를 `ARCHITECTURE.md`에 설명)
- **LLM SDK**: `claude-code-sdk` (pip) 또는 `@openai/codex` (npm) 중 택 1 — API 키 불필요, 구독 기반
- **벡터 DB, 캐시 DB, 청킹 전략**: 자유 선택
- **실행**: `docker compose up` 또는 README에 명시된 방법으로 한 줄 실행 가능해야 함

## 필수 산출물

- `README.md` — 실행 방법 + 아키텍처 설명
- `ARCHITECTURE.md` — 기술 스택 선택 이유, LLM SDK 통합 방식
- `PROMPT_DESIGN.md` — 프롬프트 설계 의도와 전략

## 샘플 문서

`sample-docs/`에 테스트용 문서 포함:
- `company-policy.txt` — 사내 복리후생 안내 (교육비, 재택근무, 연차 등)
- `development-guide.md` — 개발 가이드 (코드 리뷰, 브랜치 전략, 배포 프로세스)

## AGENTS.md

`AGENTS.md`는 `CLAUDE.md`의 심볼릭 링크. Codex 등 다른 AI 에이전트도 동일한 지침을 읽을 수 있도록 제공.

## Retrobot (자동 회고)

- `retrobot/SKILL.md` — AI 에이전트가 읽고 실행하는 KPT 회고 생성 지침
- `.githooks/post-commit` — 커밋 후 `claude` 또는 `codex` CLI를 호출하여 KPT 회고 자동 생성
- 커밋 메시지에 "Retrobot"이 포함되면 훅 스킵 (무한 루프 방지)
- 회고 결과는 `retros/` 디렉토리에 저장되고 자동 커밋됨
- 과제 구현과는 별개의 도구

### 설정

리포지토리 클론/생성 후 git hook을 활성화합니다:

```bash
git config core.hooksPath .githooks
```

### 수동 실행

```bash
claude -p "$(cat retrobot/SKILL.md)"   # Claude Code
codex "$(cat retrobot/SKILL.md)"       # Codex
```

## 평가 비중

| 영역 | 비중 |
|------|------|
| BE 설계 (구조, 레이어 분리, 비동기, 에러 핸들링) | 20% |
| RAG 파이프라인 (청킹·임베딩·검색·답변 생성) | 25% |
| LLM API 활용 (호출 설계, 스트리밍, 구조화 출력) | 20% |
| 캐싱 전략 (설계, 유사 질문, 무효화) | 20% |
| 프롬프트 엔지니어링 (품질, 환각 억제, 설계 문서) | 15% |

**완성도보다 설계 의도와 구현 품질을 우선 평가.** 부분 구현도 평가 대상이며, 미구현 부분은 설계 문서로 대체 가능.
