"""Entry point for generating the daily arXiv digest."""

from __future__ import annotations

import os
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
    return file_path


def main() -> None:
    generate_daily_digest()


if __name__ == "__main__":
    main()
