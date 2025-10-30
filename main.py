"""Entry point for generating the daily arXiv digest."""

from __future__ import annotations

import os
import re
from datetime import datetime

import dotenv

from src.llm_summary import llm_summary
from src.spider.arxiv_scraper import scrape_arxiv


dotenv.load_dotenv()


def generate_daily_digest() -> str | None:
    """Generate a markdown summary for the latest arXiv papers."""

    papers = scrape_arxiv()
    if not papers:
        print("No new papers found today.")
        return None

    now = datetime.now()
    output_dir = os.path.join("output", now.strftime("%Y-%m"))
    os.makedirs(output_dir, exist_ok=True)

    summary = llm_summary(papers)

    today_str = now.strftime("%Y-%m-%d")
    file_path = os.path.join(output_dir, f"summary_{today_str}.md")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(summary)

    print(f"Summary saved to {file_path}")
    update_readme(summary, today_str)
    return file_path


def update_readme(summary: str, summary_date: str) -> None:
    """Embed the latest daily summary at the top of the README file."""

    readme_path = "README.md"
    if not os.path.exists(readme_path):
        return

    summary_block = (
        "<!-- DAILY_SUMMARY_START -->\n"
        f"## 📚 今日 arXiv 摘要（{summary_date}）\n\n"
        f"{summary.strip()}\n"
        "<!-- DAILY_SUMMARY_END -->\n\n"
    )

    with open(readme_path, "r", encoding="utf-8") as readme_file:
        readme_content = readme_file.read()

    pattern = re.compile(
        r"<!-- DAILY_SUMMARY_START -->.*?<!-- DAILY_SUMMARY_END -->\n?\n?",
        flags=re.DOTALL,
    )

    if pattern.search(readme_content):
        updated_content = pattern.sub(summary_block, readme_content, count=1)
    else:
        updated_content = summary_block + readme_content

    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.write(updated_content)


def main() -> None:
    generate_daily_digest()


if __name__ == "__main__":
    main()
