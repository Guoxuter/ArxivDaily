from openai import OpenAI
import os
import dotenv
dotenv.load_dotenv()
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from src.utils.paper_schema import PaperResponse
from src.prompt.choice_prompt import choice_prompt
from src.prompt.summary_prompt import summary_prompt
KEY_WORDS = os.getenv("KEY_WORDS")



client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_API_BASE"),
)

def call_llm(prompt: str, model="doubao-seed-1-6-250615",**kwargs) -> str:
    
    if "response_format" in kwargs:
        resp = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=25600,
            temperature=0.3,
            **kwargs
        )
    else:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=25600,
            temperature=0.3,
            **kwargs
        )
    return resp.choices[0].message.content



MAX_BATCH_SIZE = 10      # 每次最多输入多少篇论文（可根据token大小调整）
MAX_WORKERS = 5          # 并行线程数
RETRY = 3                # 每个任务重试次数

KEY_WORDS = os.getenv("KEY_WORDS")



def process_batch(batch_papers, batch_id):
    """处理单个批次，带重试机制"""
    for attempt in range(RETRY):
        try:
            prompt = choice_prompt.replace("{{key_words}}", KEY_WORDS).replace("{{input}}", str(batch_papers))
            result = call_llm(prompt, response_format=PaperResponse,extra_body={"enable_thinking":False})
            parsed = json.loads(result)['papers']
            return parsed
        except Exception as e:
            print(f"[Batch {batch_id}] 第 {attempt+1} 次尝试失败: {e}")
            time.sleep(2)
    print(f"[Batch {batch_id}] 重试失败，跳过该批。")
    return []

def llm_summary(papers):
    """并行执行 LLM 筛选与总结"""
    # === 1. 拆分 papers ===
    batches = [papers[i:i + MAX_BATCH_SIZE] for i in range(0, len(papers), MAX_BATCH_SIZE)]

    print(f"总共有 {len(papers)} 篇论文，将分成 {len(batches)} 批并行处理。")

    specific_papers = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_batch = {executor.submit(process_batch, batch, i): i for i, batch in enumerate(batches)}

        for future in as_completed(future_to_batch):
            batch_id = future_to_batch[future]
            try:
                result = future.result()
                print(f"[Batch {batch_id}] 完成，得到 {len(result)} 条结果。")
                specific_papers.extend(result)
                print(len(specific_papers))
            except Exception as e:
                print(f"[Batch {batch_id}] 失败: {e}")
    
    # specific_papers=call_llm(choice_prompt.replace("{{key_words}}",KEY_WORDS).replace(f"{{input}}",str(papers)),
                            # response_format=PaperResponse, )
    
    prompt = summary_prompt.replace("{{input}}",str(specific_papers))
    return call_llm(prompt,model="deepseek-r1-250528")