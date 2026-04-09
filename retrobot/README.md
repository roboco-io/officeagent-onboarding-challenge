# Retrobot

> 당신의 회고를 자동으로 기록해주는 도구입니다.

Retrobot은 AI 에이전트(Claude Code / Codex)가 자신의 작업 로그를 분석하여 **KPT(Keep/Problem/Try) 회고**를 자동 생성합니다.
매 push마다 자동으로 회고를 생성하고, 타임라인으로 정리하여 성장의 흐름을 한눈에 볼 수 있습니다.

## 동작 방식

1. `git commit` 완료 후 `.githooks/post-commit` 훅이 트리거됨
2. 훅이 `claude` 또는 `codex` CLI를 호출하며 `retrobot/SKILL.md` 지침을 전달
3. 에이전트가 `~/.claude/projects/` (또는 `~/.codex/`) 로그를 읽고 분석
4. KPT 회고 마크다운을 `retros/`에 생성하고 자동 커밋

## 설정

프로젝트 클론 후 아래 명령어를 실행하세요:

```bash
git config core.hooksPath .githooks
```

## 수동 실행

```bash
# Claude Code로 실행
claude -p "$(cat retrobot/SKILL.md)"

# Codex로 실행
codex "$(cat retrobot/SKILL.md)"
```

## 출력 구조

```
retros/
├── TIMELINE.md              # 전체 회고 타임라인
├── 2026-04-09_1430_retro.md  # 개별 회고
└── ...
```

## 커스터마이징

`retrobot/SKILL.md`를 편집하여 회고 형식, 분석 기준, 출력 포맷을 자유롭게 조정할 수 있습니다.
