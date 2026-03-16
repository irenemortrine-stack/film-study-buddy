SYNTHESIZE_THEORIES = """\
你是一位电影理论专家。根据搜索结果和关键词，生成 3 张电影理论知识卡片。

电影：{film_title}
分析关键词：{keywords}
学术搜索结果：{academic_results}
影评搜索结果：{review_results}

请返回 JSON 数组，每个元素包含：
{{
  "name": "理论名称（中文，简洁）",
  "key_figures": "代表人物（1-2人，中文名）",
  "core_idea": "用一句大白话解释这个理论能帮我们看懂电影里的什么，举一个具体例子，100字以内",
  "mermaid": "flowchart LR\\n  A[核心概念] --> B[分析方法] --> C[应用示例]",
  "source_links": ["链接1", "链接2"]
}}

3 张卡片应覆盖不同理论视角（如精神分析、女性主义、符号学、叙事学等）。
core_idea 要通俗，避免学术术语，让普通观众能立刻理解这个理论和这部电影的关系。
只返回 JSON 数组，不要其他内容。
"""
