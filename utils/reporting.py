from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from agno.team import Team
from config_loader import config


@dataclass
class ReportContext:
    path: Path
    lines: List[str]


def init_report_session(
    save_reports: bool,
    report_dir: str,
    session_id: str,
    base_dir: Path,
) -> Optional[ReportContext]:
    if not save_reports:
        return None

    report_base = Path(report_dir)
    if not report_base.is_absolute():
        report_base = base_dir / report_base
    report_base.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = report_base / f"session_{session_id[:8]}_{started_at.replace(':', '').replace(' ', '_')}.md"
    lines = [
        f"# 对话报告\n\n**会话 ID**: {session_id}\n**开始时间**: {started_at}\n\n---\n\n"
    ]
    report_path.write_text("".join(lines), encoding="utf-8")
    return ReportContext(path=report_path, lines=lines)


def append_report_from_last_run(
    report_context: Optional[ReportContext],
    team: Team,
    session_id: str,
    user_input: str,
) -> None:
    if report_context is None:
        return

    response_text = ""
    last_run = team.get_last_run_output(session_id=session_id)
    if last_run is not None:
        if isinstance(last_run.content, str):
            response_text = last_run.content
        else:
            try:
                response_text = json.dumps(last_run.content, ensure_ascii=False, indent=2)
            except TypeError:
                response_text = str(last_run.content)

    report_context.path.parent.mkdir(parents=True, exist_ok=True)
    report_context.lines.append(
        "## 用户\n"
        f"{user_input}\n\n"
        "## 助手\n"
        f"{response_text}\n\n"
        "---\n\n"
    )
    report_context.path.write_text("".join(report_context.lines), encoding="utf-8")


def setup_reporting(
    team: Team,
    session_id: str,
    base_dir: Path,
) -> tuple[bool, Optional[ReportContext]]:
    save_reports = config.get_system_config("output.save_reports", False)
    report_dir = config.get_system_config("output.report_dir", "reports")
    if save_reports:
        team.cache_session = True
    report_context = init_report_session(
        save_reports=save_reports,
        report_dir=report_dir,
        session_id=session_id,
        base_dir=base_dir,
    )
    if report_context is not None:
        print(f"🗂️  报告将保存到: {report_context.path}")
        print()
    return save_reports, report_context
