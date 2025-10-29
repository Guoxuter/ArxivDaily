import os
from datetime import datetime
import dotenv
dotenv.load_dotenv()


from src.llm_summary import llm_summary
from src.arxiv_search import fetch_llm_papers
from src.utils.filter_paper import filter_paper  
from src.spider.arxiv_scraper import scrape_arxiv



now = datetime.now()




def main():
    '''querys = ["LLM Memory OR Agent Memory",
              'cat:cs.AI OR cat:stat.ML',
              'Procedural Memory',
              'Personal Memory']
    
    papers = []
    for query in querys:
        papers.extend(fetch_llm_papers(query,max_results=100))
        
    if not papers:
        print("No papers found.")
        return

    papers = filter_paper(papers)'''
    
    papers = scrape_arxiv()
    print(len(papers))
    if papers:
        output_dir = 'output'
        output_dir = os.path.join(output_dir, now.strftime('%Y-%m'))
        os.makedirs(output_dir, exist_ok=True)
    
        summary = llm_summary(papers)
    
        # 按当前日期生成文件名，例如：summary_2023-10-27.md
        today_str = now.strftime('%Y-%m-%d')
        file_path = os.path.join(output_dir, f'summary_{today_str}.md')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary saved to {file_path}")
    else:
        print("No new papers found today.")
        
        
if __name__ == "__main__":
    main()