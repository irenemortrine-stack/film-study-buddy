ESSAY_QUESTIONS = """\
你是一位电影研究导师。根据选定的理论框架，为学生设计结构化分析问题。

电影：{film_title}
选定理论：{theory_name}
理论核心观点：{core_idea}
分析关键词：{keywords}
用户原始感受：{original_review}

请生成 4-6 个引导性问题，帮助用户用该理论框架深度分析这部电影。
问题应由浅入深，从具体场景出发，逐步引向理论层面。

返回 JSON：
{{
  "questions": [
    "问题1",
    "问题2",
    "问题3",
    "问题4"
  ]
}}

只返回 JSON。
"""
