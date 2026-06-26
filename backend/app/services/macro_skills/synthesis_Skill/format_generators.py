from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import TEMPLATES_DIR
from app.models.synthesis.synthesis_models import FinalReport


class FormatGenerator:
    def __init__(self, templates_dir: Path | None = None) -> None:
        self.templates_dir = templates_dir or TEMPLATES_DIR
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def to_markdown(self, report: FinalReport) -> str:
        template = self.env.get_template("report_markdown.md")
        return template.render(report=report.model_dump(), report_json=json.dumps(report.model_dump(), indent=2))

    def to_pdf_html(self, report: FinalReport) -> str:
        template = self.env.get_template("report_pdf.html")
        css_path = self.templates_dir / "styles" / "report.css"
        css_content = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
        return template.render(
            report=report.model_dump(),
            css_content=css_content,
        )
