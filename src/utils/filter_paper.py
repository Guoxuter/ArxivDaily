import json
import os
def filter_paper(papers):
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open(os.path.join(output_dir, "processed_papers.json"), "r") as f:
            processed_papers = json.load(f)
            if not processed_papers:    
                processed_papers = []
        filtered_papers = [paper for paper in papers if paper["id"] not in processed_papers]
        
        with open(os.path.join(output_dir, "processed_papers.json"), "w") as f:
            json.dump(processed_papers + [paper["id"] for paper in filtered_papers], f, indent=4)
        
        return filtered_papers
    except:
        with open(os.path.join(output_dir, "processed_papers.json"), "w") as f:
            json.dump([paper["id"] for paper in papers], f, indent=4)
        return papers
    
