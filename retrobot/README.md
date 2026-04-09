# Retrobot

> 당신의 회고를 자동으로 기록해주는 도구입니다.

Retrobot은 Claude Code / Codex의 작업 로그를 분석하여 **KPT(Keep/Problem/Try) 회고**를 자동 생성합니다.
매 push마다 자동으로 회고를 생성하고, 타임라인으로 정리하여 성장의 흐름을 한눈에 볼 수 있습니다.

## 설정

프로젝트 클론 후 아래 명령어를 실행하세요:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

이후 `git push`할 때마다 자동으로 회고가 생성됩니다.

## 수동 실행

```bash
# 최근 24시간 회고
python3 retrobot/retrobot.py

# 전체 세션 회고
python3 retrobot/retrobot.py --all

# 최근 7일 회고
python3 retrobot/retrobot.py --since 7d

# 특정 파일로 출력
python3 retrobot/retrobot.py --out retros/my-retro.md
```

## 출력 구조

```
retros/
├── TIMELINE.md              # 전체 회고 타임라인
├── 2026-04-09_1430_retro.md  # 개별 회고
├── 2026-04-10_0900_retro.md
└── ...
```

## 회고 내용

각 회고에는 다음이 포함됩니다:

- **요약** — 세션 수, 프롬프트 수, 에러 수
- **사용된 도구** — 도구별 사용 횟수
- **세션별 활동** — 실제 사용한 프롬프트와 발생한 에러
- **KPT 회고** — Keep(좋았던 것), Problem(나빴던 것), Try(개선할 것)
- **타임라인** — 시간순 활동 정리

> 자동 생성된 KPT는 출발점입니다. 직접 편집하여 의미 있는 회고로 보완하세요.
