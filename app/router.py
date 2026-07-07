ROUTE_MAP = {
    "search": ("web_search", "用户需要获取实时外部信息。"),
    "rag_qa": ("local_rag", "用户需要基于本地资料或知识库进行问答。"),
    "summarize": ("text_summarizer", "用户需要压缩、提炼或总结文本内容。"),
    "code": ("code_assistant", "用户需要生成、修改、解释或调试代码。"),
    "reminder": ("calendar_reminder", "用户需要创建提醒、日程或计划。"),
    "translate": ("translator", "用户需要进行语言翻译或改写表达。"),
    "chat": ("general_chat", "用户正在进行开放式闲聊或情绪交流。"),
}


def route_intent(intent):
    if intent not in ROUTE_MAP:
        return {"route_to": "general_chat", "reason": "无法识别到明确工具意图，回退到通用对话。"}
    route_to, reason = ROUTE_MAP[intent]
    return {"route_to": route_to, "reason": reason}
