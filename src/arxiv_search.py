import arxiv
import datetime
from tqdm import tqdm
import os

def fetch_llm_papers(query,max_results=70):
    """
    从 arXiv 获取最新的 LLM 相关论文（最近一天内提交的）
    """
   
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    today = datetime.datetime.now(datetime.timezone.utc).date()
    papers = []
    for result in tqdm(search.results(), desc="Fetching LLM papers"):
        # 仅保留当天或近两天的新论文
        if result.published.date() < today - datetime.timedelta(days=3):
            continue
        papers.append({
            "id": result.entry_id,
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "summary": result.summary.strip().replace("\n", " "),
            "published": result.published.strftime("%Y-%m-%d"),
            "pdf_url": result.pdf_url,
            "primary_category": result.primary_category
        })
    return papers
