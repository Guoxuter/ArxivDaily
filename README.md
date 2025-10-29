# ArxivDaily

自动化抓取 arXiv 论文、使用 LLM 筛选并输出 Markdown 摘要的管道。该仓库已经按照 [Video-Generation-arxiv-daily](https://github.com/KashiwaByte/Video-Generation-arxiv-daily/blob/main/docs/README.md#usage) 中的思路适配为 **GitHub Actions 每日运行并推送结果**。

## 功能概述
- 按照环境变量中配置的分类抓取 arXiv 最新论文
- 提取标题、摘要、作者、发布日期、PDF 链接等信息
- 调用 LLM 根据关键词筛选、打分并生成中文 Markdown 摘要
- 把筛选后的论文输出到 `output/<年月>/summary_<日期>.md`
- GitHub Actions 定时运行并把新的摘要文件提交回仓库，实现“每日论文推送”

## 本地开发
1. 克隆仓库并安装依赖
   ```bash
   git clone <your_repo_url>
   cd ArxivDaily
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. 准备环境变量，复制 `.env.example`
   ```bash
   cp .env.example .env
   ```
   | 变量名 | 说明 |
   | ------ | ---- |
   | `LLM_API_KEY` | LLM 服务的 API key（必填） |
   | `LLM_API_BASE` | 可选的自定义 Base URL，如果使用官方 OpenAI 可以留空 |
   | `KEY_WORDS` | 用分号分隔的检索关键词，LLM 会据此筛选论文 |
   | `CATEGORIES` | 需要抓取的 arXiv 分类列表，逗号分隔 |
3. 运行脚本
   ```bash
   python main.py
   ```
   程序会在 `output/<年月>/` 下生成当日的 Markdown 摘要，并在 `output/processed_papers.json` 中记录已处理的论文 ID，避免重复推送。

## 使用 GitHub Actions 每日推送
1. 在 GitHub 创建一个仓库并推送本项目代码：
   ```bash
   git remote add origin git@github.com:<your_name>/<your_repo>.git
   git push -u origin main
   ```
2. 在仓库的 **Settings → Secrets and variables → Actions** 中添加下列 Secrets（若已存在可以点击条目右侧的 “Update secret” 按钮进行修改）：
    - `LLM_API_KEY`
    - `LLM_API_BASE`（如果不需要可设置为空字符串）
    - `KEY_WORDS`
    - `CATEGORIES`

   如果需要替换或修正某个值，在 Secrets 列表中点击相应条目的 `Update secret`，重新填写后保存即可；若要删除则选择 `Remove secret`。
3. 仓库已经内置 `.github/workflows/arxiv-daily.yml` 工作流，默认每天 UTC 时间 1:00 运行；你也可以在 Actions 页面手动触发 `workflow_dispatch`。
4. 工作流步骤：
   - 安装依赖并运行 `python main.py`
   - 如果 `output/` 目录有更新，会自动使用 `GITHUB_TOKEN` 提交并推送

运行成功后，你可以在仓库的 `output/` 目录中查看每日更新的 Markdown 摘要，也可以订阅仓库的通知获得推送。

## 目录结构
```
├── main.py                      # 执行入口
├── requirements.txt             # Python 依赖
├── output/                      # 生成的 Markdown 摘要及处理记录
├── src/
│   ├── llm_summary.py           # 调用 LLM 进行筛选与总结
│   ├── spider/arxiv_scraper.py  # 抓取 arXiv 新论文
│   ├── utils/filter_paper.py    # 去重过滤
│   └── prompt/                  # 提示词模板
└── .github/workflows/arxiv-daily.yml  # GitHub Actions 工作流
```

## 常见问题
- **没有配置 `KEY_WORDS` 或 `LLM_API_KEY` 时脚本会报错**：请确保在本地 `.env` 或 GitHub Secrets 中正确填写。
- **依赖安装失败并提示 `ResolutionImpossible`**：通常是由于某些三方库的版本冲突，可删除本地或远端环境中的虚拟环境后重新执行 `pip install -r requirements.txt`，工作流中的依赖版本已经放宽，确保能够自动解析。
- **工作流没有新提交**：若当日没有新论文或摘要内容未改变，`output/` 下不会产生变化，工作流会直接结束。

欢迎在此基础上继续扩展，例如发送到飞书、钉钉或企业微信等。
