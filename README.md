# OfficeAgent BE 채용 과제 — Document Q&A API

## 시작하기

이 리포지토리를 **포크**한 후, 아래 PRD에 따라 과제를 구현하세요.

## 과제 내용

**[PRD 바로가기 →](./docs/PRD.md)**

문서를 업로드하면 내용을 분석하고, 사용자 질문에 대해 문서 근거 기반 답변을 생성하는 REST API 서버를 구현합니다.

### 평가 역량

| 역량 | 설명 |
|------|------|
| BE 설계 | FastAPI 서버 설계, 레이어 분리, 비동기 처리 |
| RAG | 문서 청킹, 임베딩, 벡터 검색, 답변 생성 |
| LLM 활용 | Claude Code SDK 또는 Codex CLI 통합 |
| 캐싱 | LLM 응답 캐시, 유사 질문 처리, 무효화 |
| 프롬프트 | 프롬프트 설계 및 설계 의도 문서화 |

### 기술 스택

- **언어 / 프레임워크:** 자유 (선택 이유를 ARCHITECTURE.md에 설명)
- **LLM:** Claude Code SDK 또는 Codex CLI (구독 기반, API 키 불필요)
- 그 외 기술 선택(벡터 DB, 캐시 DB 등)은 자유

## 제출 방법

1. 이 리포지토리를 포크합니다.
2. 과제를 구현합니다.
3. **비공개 리포지토리**로 전환 후 [`serithemage`](https://github.com/serithemage)를 Collaborator로 초대합니다.

**기한:** 7일

자세한 내용은 [PRD](./docs/PRD.md)를 참고하세요.
