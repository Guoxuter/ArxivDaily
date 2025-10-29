from typing import List, Dict, Any
from pydantic import BaseModel, Field
from typing import List


class Paper(BaseModel):
    id: str
    title: str
    summary: str = Field(description="论文摘要, 请使用中文进行总结")
    authors: List[str] = Field(description="论文作者列表")
    categories: List[str] = Field(description="论文分类列表")
    published: str = Field(description="论文发布日期")
    pdf_url: str = Field(description="论文PDF链接")

class PaperResponse(BaseModel):
    papers: List[Paper] = Field(description="符合条件的论文列表")