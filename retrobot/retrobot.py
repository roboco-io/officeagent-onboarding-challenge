#!/usr/bin/env python3
"""
Retrobot — 자동 회고 생성기

Claude Code / Codex 로그를 분석하여 KPT(Keep/Problem/Try) 회고를 자동 생성합니다.

로그 위치:
  - Claude Code: ~/.claude/projects/<project-path-encoded>/*.jsonl
  - Codex: ~/.codex/projects/<project-path-encoded>/*.jsonl

사용법:
  python retrobot/retrobot.py              # 마지막 세션 회고
  python retrobot/retrobot.py --all        # 전체 세션 회고
  python retrobot/retrobot.py --since 24h  # 최근 24시간
"""

import json
import os
import sys
import glob
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

RETRO_DIR = "retros"
KST = timezone(timedelta(hours=9))


def find_project_log_dir() -> Optional[Path]:
    """현재 프로젝트의 Claude Code / Codex 로그 디렉토리를 찾는다."""
    project_root = _get_git_root()
    if not project_root:
        return None

    # Claude Code: ~/.claude/projects/-Users-foo-bar-project/
    encoded = project_root.replace("/", "-")
    candidates = [
        Path.home() / ".claude" / "projects" / encoded,
        Path.home() / ".codex" / "projects" / encoded,
    ]
    for d in candidates:
        if d.is_dir():
            return d
    return None


def _get_git_root() -> Optional[str]:
    """git 루트 경로를 반환."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def parse_sessions(log_dir: Path, since: Optional[datetime] = None) -> list[dict]:
    """JSONL 로그 파일들을 파싱하여 세션별 데이터를 추출한다."""
    sessions = {}

    for jsonl_file in sorted(log_dir.glob("*.jsonl")):
        session_id = jsonl_file.stem
        entries = []

        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                ts = _parse_timestamp(entry)
                if since and ts and ts < since:
                    continue
                entries.append(entry)

        if not entries:
            continue

        sessions[session_id] = {
            "id": session_id[:8],
            "entries": entries,
            "tasks": _extract_tasks(entries),
            "prompts": _extract_prompts(entries),
            "tools_used": _extract_tools(entries),
            "errors": _extract_errors(entries),
            "start_time": _get_session_time(entries, first=True),
            "end_time": _get_session_time(entries, first=False),
        }

    return list(sessions.values())


def _parse_timestamp(entry: dict) -> Optional[datetime]:
    """엔트리에서 타임스탬프를 추출."""
    ts = entry.get("timestamp")
    if not ts:
        return None
    try:
        if isinstance(ts, str):
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        elif isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts / 1000 if ts > 1e12 else ts, tz=KST)
    except Exception:
        return None
    return None


def _get_session_time(entries: list, first: bool) -> str:
    """세션의 시작/종료 시간."""
    for entry in (entries if first else reversed(entries)):
        ts = _parse_timestamp(entry)
        if ts:
            return ts.astimezone(KST).strftime("%Y-%m-%d %H:%M")
    return "unknown"


def _extract_prompts(entries: list) -> list[str]:
    """사용자 프롬프트를 추출."""
    prompts = []
    for entry in entries:
        if entry.get("type") == "human":
            msg = entry.get("message", {})
            if isinstance(msg, dict):
                content = msg.get("content", "")
            else:
                content = str(msg)
            text = _content_to_text(content)
            if text and len(text) > 5:
                prompts.append(text[:200])
    return prompts


def _content_to_text(content) -> str:
    """content 필드를 텍스트로 변환."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return " ".join(parts).strip()
    return ""


def _extract_tasks(entries: list) -> list[str]:
    """태스크/목표를 추출."""
    tasks = []
    for entry in entries:
        if entry.get("type") == "human":
            text = _content_to_text(entry.get("message", {}).get("content", ""))
            if text and not text.startswith("<") and len(text) > 10:
                tasks.append(text[:100])
    return tasks[:10]


def _extract_tools(entries: list) -> dict[str, int]:
    """사용된 도구와 횟수를 집계."""
    tools = {}
    for entry in entries:
        if entry.get("type") == "tool_use":
            name = entry.get("name", entry.get("tool_name", "unknown"))
            tools[name] = tools.get(name, 0) + 1
        elif entry.get("type") == "assistant":
            msg = entry.get("message", {})
            content = msg.get("content", []) if isinstance(msg, dict) else []
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        name = block.get("name", "unknown")
                        tools[name] = tools.get(name, 0) + 1
    return tools


def _extract_errors(entries: list) -> list[str]:
    """에러/실패 메시지를 추출."""
    errors = []
    for entry in entries:
        if entry.get("type") == "tool_result":
            content = entry.get("content", "")
            text = _content_to_text(content)
            if any(kw in text.lower() for kw in ["error", "failed", "traceback", "exception"]):
                errors.append(text[:150])
    return errors[:5]


def generate_kpt(sessions: list) -> str:
    """세션 데이터를 기반으로 KPT 회고 마크다운을 생성."""
    now = datetime.now(KST)
    total_prompts = sum(len(s["prompts"]) for s in sessions)
    total_tasks = sum(len(s["tasks"]) for s in sessions)
    all_tools = {}
    all_errors = []

    for s in sessions:
        for tool, count in s["tools_used"].items():
            all_tools[tool] = all_tools.get(tool, 0) + count
        all_errors.extend(s["errors"])

    top_tools = sorted(all_tools.items(), key=lambda x: -x[1])[:10]

    md = f"""# Retrobot 회고 — {now.strftime("%Y-%m-%d %H:%M")} KST

> 자동 생성된 회고입니다. 직접 편집하여 보완하세요.

## 요약

| 항목 | 값 |
|------|-----|
| 세션 수 | {len(sessions)} |
| 총 프롬프트 | {total_prompts} |
| 총 태스크 | {total_tasks} |
| 에러 발생 | {len(all_errors)} |
| 생성 시각 | {now.strftime("%Y-%m-%d %H:%M KST")} |

## 사용된 도구

| 도구 | 횟수 |
|------|------|
"""
    for tool, count in top_tools:
        md += f"| {tool} | {count} |\n"

    md += """
---

## 세션별 활동

"""
    for s in sessions:
        md += f"### 세션 `{s['id']}` ({s['start_time']} ~ {s['end_time']})\n\n"
        md += "**프롬프트:**\n"
        for i, p in enumerate(s["prompts"][:5], 1):
            md += f"{i}. {p}\n"
        if s["errors"]:
            md += "\n**발생한 에러:**\n"
            for e in s["errors"]:
                md += f"- `{e[:80]}`\n"
        md += "\n"

    md += """---

## KPT 회고

### Keep (좋았던 것)

"""
    # Keep 자동 분석
    if total_tasks > 0:
        md += f"- 총 {total_tasks}개의 태스크를 수행했습니다.\n"
    if top_tools:
        md += f"- 다양한 도구를 활용했습니다 ({', '.join(t for t, _ in top_tools[:3])} 등).\n"
    if len(all_errors) == 0:
        md += "- 에러 없이 작업을 완료했습니다.\n"
    md += "- <!-- 직접 추가하세요 -->\n"

    md += """
### Problem (나빴던 것)

"""
    if all_errors:
        md += f"- {len(all_errors)}건의 에러가 발생했습니다.\n"
        for e in all_errors[:3]:
            md += f"  - `{e[:80]}`\n"
    md += "- <!-- 직접 추가하세요 -->\n"

    md += """
### Try (개선해야 할 것)

"""
    if all_errors:
        md += "- 에러 발생 원인을 분석하고 재발 방지 대책을 세웁니다.\n"
    md += "- <!-- 직접 추가하세요 -->\n"

    md += """
---

## 타임라인

| 시각 | 세션 | 주요 활동 |
|------|------|----------|
"""
    for s in sessions:
        summary = s["tasks"][0] if s["tasks"] else "활동 기록 없음"
        md += f"| {s['start_time']} | `{s['id']}` | {summary[:60]} |\n"

    md += "\n---\n*Generated by Retrobot*\n"
    return md


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Retrobot — 자동 회고 생성기")
    parser.add_argument("--all", action="store_true", help="전체 세션 회고")
    parser.add_argument("--since", type=str, default=None, help="기간 (예: 24h, 7d)")
    parser.add_argument("--out", type=str, default=None, help="출력 파일 경로")
    args = parser.parse_args()

    log_dir = find_project_log_dir()
    if not log_dir:
        print("⚠ 프로젝트 로그 디렉토리를 찾을 수 없습니다.")
        print("  Claude Code 또는 Codex로 작업한 이력이 있는 프로젝트에서 실행하세요.")
        sys.exit(0)

    since = None
    if args.since and not args.all:
        since = _parse_since(args.since)
    elif not args.all:
        since = datetime.now(KST) - timedelta(hours=24)

    print(f"📂 로그 디렉토리: {log_dir}")
    sessions = parse_sessions(log_dir, since=since)

    if not sessions:
        print("ℹ 해당 기간에 세션 기록이 없습니다.")
        sys.exit(0)

    print(f"📊 {len(sessions)}개 세션 분석 중...")

    kpt = generate_kpt(sessions)

    os.makedirs(RETRO_DIR, exist_ok=True)
    now = datetime.now(KST)
    filename = args.out or f"{RETRO_DIR}/{now.strftime('%Y-%m-%d_%H%M')}_retro.md"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(kpt)

    print(f"✅ 회고 생성 완료: {filename}")

    _update_timeline(filename, now)


def _parse_since(s: str) -> datetime:
    """'24h', '7d' 같은 문자열을 datetime으로 변환."""
    now = datetime.now(KST)
    s = s.strip().lower()
    if s.endswith("h"):
        return now - timedelta(hours=int(s[:-1]))
    elif s.endswith("d"):
        return now - timedelta(days=int(s[:-1]))
    return now - timedelta(hours=24)


def _update_timeline(retro_file: str, now: datetime):
    """retros/TIMELINE.md에 회고 링크를 추가."""
    timeline_path = f"{RETRO_DIR}/TIMELINE.md"
    header = "# Retrobot Timeline\n\n| 날짜 | 회고 |\n|------|------|\n"

    existing = ""
    if os.path.exists(timeline_path):
        with open(timeline_path, "r", encoding="utf-8") as f:
            existing = f.read()

    basename = os.path.basename(retro_file)
    new_entry = f"| {now.strftime('%Y-%m-%d %H:%M')} | [{basename}](./{basename}) |"

    if existing:
        lines = existing.strip().split("\n")
        table_lines = [l for l in lines if l.startswith("|")]
        if len(table_lines) >= 2:
            lines.insert(lines.index(table_lines[-1]) + 1 if table_lines else len(lines), new_entry)
            content = "\n".join(lines) + "\n"
        else:
            content = header + new_entry + "\n"
    else:
        content = header + new_entry + "\n"

    with open(timeline_path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    main()
