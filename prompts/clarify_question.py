CLARIFY_QUESTION = """\
你是一个热爱电影的朋友，正在和用户聊他/她刚看完的电影。
你的目标是通过轻松的追问，帮助用户挖掘更深的感受。

电影：{film_title}
用户最初的感受：{original_review}
已有关键词：{keywords}
已有对话：
{conversation_history}

请提出一个自然、口语化的追问，帮助挖掘用户感受背后的深层原因。
不要问太学术的问题，像朋友聊天一样。
只返回问题本身，不要其他内容。
"""

SHOULD_STOP_CLARIFYING = """\
判断用户是否想结束追问，进入下一步分析。

用户最新消息：{message}

如果用户表达了"差不多了"、"就这些"、"可以了"、"开始分析"、"就这样吧"、"就这样"、"好了"等结束意图，返回 YES。
否则返回 NO。
只返回 YES 或 NO。
"""

FINALIZE_KEYWORDS = """\
根据以下对话，提炼出最终的分析关键词列表。

电影：{film_title}
原始感受：{original_review}
对话记录：
{conversation_history}

请返回 JSON：
{{
  "keywords": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"]
}}

关键词应涵盖：情感基调、核心主题、人物关系、叙事结构、视觉风格等维度。
只返回 JSON。
"""
