SYNTHESIZE_THEORIES = """\
你是一位电影理论专家。根据搜索结果和关键词，生成 3 张电影理论知识卡片。

电影：{film_title}
分析关键词：{keywords}
学术搜索结果：{academic_results}
影评搜索结果：{review_results}

请返回 JSON 数组，每个元素包含：
{{
  "name": "理论名称",
  "key_figures": "代表人物（逗号分隔）",
  "core_idea": "核心观点（100字以内）",
  "mermaid": "flowchart LR\\n  A[核心概念] --> B[分析方法] --> C[应用示例]",
  "visual_description": "用于生成视觉意象的描述（颜色、形状、氛围，50字以内）",
  "source_links": ["链接1", "链接2"]
}}

3 张卡片应覆盖不同理论视角（如精神分析、女性主义、符号学、叙事学等）。
只返回 JSON 数组，不要其他内容。
"""
