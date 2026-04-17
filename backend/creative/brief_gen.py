"""
Campaign brief generator — assembles all agent outputs into
a structured Markdown document and optionally converts to PDF.
"""

import os
import json
import re
from datetime import date, datetime
from typing import Optional
from loguru import logger


class BriefGenerator:
    """Generates campaign brief documents from agent council output."""

    def __init__(self, output_dir: str = "./data/outputs"):
        self.output_dir = output_dir

    def _get_day_dir(self) -> str:
        day_dir = os.path.join(self.output_dir, str(date.today()), "briefs")
        os.makedirs(day_dir, exist_ok=True)
        return day_dir

    def generate_markdown(self, council_output: dict, analysis_brief: dict) -> str:
        """Generate a high-performance Markdown campaign brief with Neuro-Marketing sections."""
        agents = council_output.get("agents", {})
        run_id = council_output.get("run_id", "unknown")
        quality = council_output.get("quality_score", 0)
        
        # Extract agent outputs
        trends = agents.get("trend_analyst", {}).get("output", "No trends available")
        strategy = agents.get("strategy_planner", {}).get("output", "No strategy available")
        copy = agents.get("copywriter", {}).get("output", "No copy available")
        creative = agents.get("creative_director", {}).get("output", "No creative direction")
        critic = agents.get("critic", {}).get("output", "No review available")
        
        # Detect 'Angles' in copy if present (simple regex heuristic)
        angle_sections = ""
        if "ANGLE" in copy.upper() or "PAIN" in copy.upper() or "OUTCOME" in copy.upper():
            angle_sections = "> [!TIP]\n> This campaign uses **Triple-Angle Logic**: Pain, Outcome, and Proof variations are provided below for A/B testing."

        # Analysis stats
        sentiment = analysis_brief.get("sentiment_scores", {})
        platforms = ", ".join(analysis_brief.get("platforms_covered", []))
        total_analyzed = analysis_brief.get("total_items_analyzed", 0)

        md = f"""# 🚀 High-Performance Campaign Brief — {date.today().strftime('%B %d, %Y')}

> **Agent Council Quality**: **{quality}/10** | Run ID: `{run_id}`
> {angle_sections}

---

## 🧠 Strategic Foundation
### Neuro-Marketing Strategy
{strategy}

### Market Signals & Trends
{trends}

---

## ✍️ Triple-Angle Copy Assets
*Generated using AIDA & PAS frameworks for maximum conversion.*

{copy}

---

## 🎨 Visual Design System (Remotion & Graphics)
{creative}

---

## ⚖️ Quality Audit (Critic)
{critic}

---

## 📊 Pipeline Data Intelligence
| Metric | Value |
|:---|:---|
| Items Analyzed | {total_analyzed} items |
| Networks Scanned | {platforms or 'N/A'} |
| Sentiment Index | {sentiment.get('overall', 'N/A')} |
| Positive Bias | ✅ {sentiment.get('positive_pct', 0)}% |
| Negative Friction | ⚠️ {sentiment.get('negative_pct', 0)}% |
| Neutral Baseline | {sentiment.get('neutral_pct', 0)}% |

---

## ⚙️ Metadata & Execution
| Field | Value |
|:---|:---|
| Generated | {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} |
| Duration | {council_output.get('duration_seconds', 0)}s |
| Quality Gate | {'✅ STRATEGICALLY SOUND' if council_output.get('passed_quality_gate') else '⚠️ NEEDS REFINEMENT'} |

### Agent Audit Log
"""
        for log in council_output.get("logs", []):
            md += f"- **{log['agent']}**: {log['provider']} ({log['tokens']} tokens) | {log['duration']}s\n"

        md += "\n---\n\n*This brief was strictly optimized for conversion. Use Angle Variations for A/B testing.*\n"

        return md

    def save_brief(self, council_output: dict, analysis_brief: dict) -> dict:
        """Generate and save the campaign brief as Markdown (and optionally PDF)."""
        markdown = self.generate_markdown(council_output, analysis_brief)

        day_dir = self._get_day_dir()
        run_id = council_output.get("run_id", "unknown")
        
        # Save Markdown
        md_path = os.path.join(day_dir, f"campaign_brief_{run_id}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        logger.info(f"Brief saved: {md_path}")

        # Try PDF conversion
        pdf_path = None
        try:
            pdf_path = self._convert_to_pdf(markdown, day_dir, run_id)
        except Exception as e:
            logger.warning(f"PDF conversion failed (non-critical): {e}")

        return {
            "markdown_path": md_path,
            "pdf_path": pdf_path,
            "markdown_content": markdown,
            "run_id": run_id,
        }

    def _convert_to_pdf(self, markdown: str, day_dir: str, run_id: str) -> Optional[str]:
        """Convert Markdown to PDF using weasyprint."""
        try:
            import markdown as md_lib
            from weasyprint import HTML

            html_content = md_lib.markdown(markdown, extensions=["tables", "fenced_code"])
            styled_html = f"""<!DOCTYPE html>
<html>
<head>
<style>
    body {{ font-family: 'Helvetica Neue', Arial, sans-serif; padding: 40px; color: #333; line-height: 1.6; }}
    h1 {{ color: #1a1a2e; border-bottom: 3px solid #6c63ff; padding-bottom: 10px; }}
    h2 {{ color: #16213e; margin-top: 30px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
    th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
    th {{ background: #6c63ff; color: white; }}
    tr:nth-child(even) {{ background: #f8f9fa; }}
    blockquote {{ border-left: 4px solid #6c63ff; padding: 10px 20px; background: #f0f0ff; margin: 20px 0; }}
    code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
    hr {{ border: none; border-top: 2px solid #eee; margin: 30px 0; }}
</style>
</head>
<body>{html_content}</body>
</html>"""

            pdf_path = os.path.join(day_dir, f"campaign_brief_{run_id}.pdf")
            HTML(string=styled_html).write_pdf(pdf_path)
            logger.success(f"PDF saved: {pdf_path}")
            return pdf_path

        except ImportError:
            logger.debug("weasyprint not available for PDF generation")
            return None
