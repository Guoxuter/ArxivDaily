"""Utilities for filtering and summarising arXiv papers with an LLM."""

from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List

import dotenv
from openai import OpenAI

from src.prompt.choice_prompt import choice_prompt
from src.prompt.summary_prompt import summary_prompt
from src.utils.paper_schema import PaperResponse

dotenv.load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
API_BASE = os.getenv("LLM_API_BASE")
if not API_KEY:
    raise RuntimeError("Missing LLM_API_KEY environment variable.")

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE,
)

MAX_BATCH_SIZE = 10      # 每次最多输入多少篇论文（可根据token大小调整）
MAX_WORKERS = 5          # 并行线程数
RETRY = 3                # 每个任务重试次数


def call_llm(prompt: str, model: str = "doubao-seed-1-6-250615", **kwargs) -> str:
    """Call the underlying LLM client with the provided prompt."""

    if "response_format" in kwargs:
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=25600,
            temperature=0.3,
            **kwargs,
        )
    else:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=25600,
            temperature=0.3,
            **kwargs,
        )
    return response.choices[0].message.content


def _get_keywords() -> str:
    key_words = os.getenv("KEY_WORDS")
    if not key_words:
        raise RuntimeError("Missing KEY_WORDS environment variable.")
    return key_words


def process_batch(batch_papers: Iterable[dict], batch_id: int) -> List[dict]:
    """处理单个批次，带重试机制。"""

    for attempt in range(RETRY):
        try:
            prompt = choice_prompt.replace("{{key_words}}", _get_keywords()).replace(
                "{{input}}", str(batch_papers)
            )
            result = call_llm(
                prompt,
                response_format=PaperResponse,
                extra_body={"enable_thinking": False},
            )
            parsed = json.loads(result)["papers"]
            return parsed
        except Exception as exc:  # noqa: BLE001
            print(f"[Batch {batch_id}] 第 {attempt + 1} 次尝试失败: {exc}")
            time.sleep(2)
    print(f"[Batch {batch_id}] 重试失败，跳过该批。")
    return []


def llm_summary(papers: List[dict]) -> str:
    """并行执行 LLM 筛选与总结。"""

    batches = [papers[i : i + MAX_BATCH_SIZE] for i in range(0, len(papers), MAX_BATCH_SIZE)]
    print(f"总共有 {len(papers)} 篇论文，将分成 {len(batches)} 批并行处理。")

    specific_papers: List[dict] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_batch = {executor.submit(process_batch, batch, i): i for i, batch in enumerate(batches)}
        for future in as_completed(future_to_batch):
            batch_id = future_to_batch[future]
            try:
                result = future.result()
                print(f"[Batch {batch_id}] 完成，得到 {len(result)} 条结果。")
                specific_papers.extend(result)
                print(len(specific_papers))
            except Exception as exc:  # noqa: BLE001
                print(f"[Batch {batch_id}] 失败: {exc}")

    prompt = summary_prompt.replace("{{input}}", str(specific_papers))
    return call_llm(prompt, model="deepseek-r1-250528")
