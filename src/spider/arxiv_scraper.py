
import os
import re

import requests
import scrapy
from datetime import datetime
from scrapy.http import TextResponse

from src.utils.filter_paper import filter_paper

class ArxivSpider(scrapy.Spider):
    name = "arxiv"
    allowed_domains = ["arxiv.org"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = os.environ.get("CATEGORIES", "cs.CL,cs.LG,stat.ML,cs.AI")
        categories = categories.split(",")
        self.target_categories = set(map(str.strip, categories))
        self.start_urls = [
            f"https://arxiv.org/list/{cat}/new" for cat in self.target_categories
        ]

    def parse(self, response,max_papers=-1):
        """
        修改后的版本：不再使用 yield，而是一次性收集并返回所有论文。
        """
        papers = []

        anchors = []
        for li in response.css("div[id=dlpage] ul li"):
            href = li.css("a::attr(href)").get()
            if href and "item" in href:
                anchors.append(int(href.split("item")[-1]))

        # 遍历论文
        for paper in response.css("dl dt"):
            paper_anchor = paper.css("a[name^='item']::attr(name)").get()
            if not paper_anchor:
                continue
            paper_id = int(paper_anchor.split("item")[-1])
            if anchors and paper_id >= anchors[-1]:
                continue

            # 获取论文ID和摘要链接
            abstract_link = paper.css("a[title='Abstract']::attr(href)").get()
            if not abstract_link:
                continue
            arxiv_id = abstract_link.split("/")[-1]

            # 对应 dd 元素
            paper_dd = paper.xpath("following-sibling::dd[1]")
            if not paper_dd:
                continue

            # 论文标题
            title = paper_dd.css("div.list-title::text").getall()
            title = "".join(title).replace("Title:", "").strip()

            # 作者
            authors = paper_dd.css("div.list-authors a::text").getall()
            authors = [a.strip() for a in authors]

            # 摘要
            summary = paper_dd.css("p.mathjax::text").get()
            if summary:
                summary = summary.strip().replace("\n", " ")
            else:
                summary = ""

            # 发布时间
            published = paper_dd.css("div.list-date::text").get()
            if published:
                published = published.replace("Date:", "").strip()
            else:
                published = datetime.now().strftime("%Y-%m-%d")

            # 分类
            subjects_text = paper_dd.css(".list-subjects .primary-subject::text").get()
            if not subjects_text:
                subjects_text = paper_dd.css(".list-subjects::text").get()

            categories_in_paper = re.findall(r'\(([^)]+)\)', subjects_text or "")
            paper_categories = set(categories_in_paper)

            # PDF链接
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

            # 只保留目标分类
            if not paper_categories.intersection(self.target_categories):
                continue

            # 添加到列表
            papers.append({
                "id": arxiv_id,
                "title": title,
                "authors": authors,
                "summary": summary,
                "published": published,
                "pdf_url": pdf_url,
                "primary_category": list(paper_categories)[0] if paper_categories else ""
            })
        if max_papers > 0:
            return papers[:max_papers]
        return papers



def scrape_arxiv():

    spider = ArxivSpider()
    all_papers = []
    
    for url in spider.start_urls:
        html = requests.get(url).text
        response = TextResponse(url=url, body=html, encoding="utf-8")
        papers = spider.parse(response)
        filter_papers = filter_paper(papers) 
        all_papers.extend(filter_papers)

    return all_papers

# 测试运行（仅示例，不依赖 Scrapy 引擎）
if __name__ == "__main__":


    papers = scrape_arxiv()
    print(papers[:3])
    print(len(papers))

    