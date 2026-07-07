import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta


DEEPSEEK_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/chat/completions")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
DEEPSEEK_THINKING = os.getenv("DEEPSEEK_THINKING", "disabled")


def clean_query(text):
    query = re.sub(r"帮我|请|一下|搜索|查一查|查一下|最近|最新|相关信息|谢谢", " ", text)
    query = re.sub(r"\s+", " ", query).strip()
    return query or text.strip()


def split_sentences(text):
    parts = re.split(r"(?<=[。！？!?；;])\s*", text.strip())
    return [part.strip() for part in parts if part.strip()]


def local_summary(text, max_items=3):
    source = text.strip()
    if not source:
        return "没有提供可总结的正文。请在资料区粘贴文章、报告或会议纪要。"
    sentences = split_sentences(source)
    if not sentences:
        return source[:260]
    selected = sentences[:max_items]
    return "\n".join(f"{idx + 1}. {sentence}" for idx, sentence in enumerate(selected))


def local_rag_answer(question, context):
    context = context.strip()
    if not context:
        return "没有提供本地资料。请在资料区粘贴笔记、文档内容，或上传 txt/md 文件。"
    terms = [term for term in re.split(r"\W+", question) if len(term) >= 2]
    chunks = split_sentences(context)
    scored = []
    for chunk in chunks:
        score = sum(1 for term in terms if term and term in chunk)
        if score:
            scored.append((score, chunk))
    if not scored:
        return "资料中没有找到明显匹配片段。下面是资料开头内容：\n" + context[:360]
    scored.sort(key=lambda item: item[0], reverse=True)
    evidence = [item[1] for item in scored[:3]]
    return "基于本地资料找到以下依据：\n" + "\n".join(f"{idx + 1}. {line}" for idx, line in enumerate(evidence))


def parse_reminder(text):
    now = datetime.now()
    target = now + timedelta(days=1 if "明天" in text else 0)
    if "后天" in text:
        target = now + timedelta(days=2)
    hour = 9
    minute = 0
    hour_map = {
        "一点": 1,
        "两点": 2,
        "二点": 2,
        "三点": 3,
        "四点": 4,
        "五点": 5,
        "六点": 6,
        "七点": 7,
        "八点": 8,
        "九点": 9,
        "十点": 10,
        "十一点": 11,
        "十二点": 12,
    }
    for key, value in hour_map.items():
        if key in text:
            hour = value
            break
    match = re.search(r"(\d{1,2})[:：点](\d{1,2})?", text)
    if match:
        hour = int(match.group(1))
        if match.group(2):
            minute = int(match.group(2))
    if "下午" in text or "晚上" in text:
        if hour < 12:
            hour += 12
    title = re.sub(r"提醒我|提醒|明天|后天|今天|早上|上午|下午|晚上|中午|\d{1,2}[:：点]\d{0,2}", " ", text)
    title = re.sub(r"\s+", " ", title).strip(" ，,。")
    title = title or "待办提醒"
    start = target.replace(hour=hour, minute=minute, second=0, microsecond=0)
    end = start + timedelta(minutes=30)
    return title, start, end


def build_ics(title, start, end):
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uid = f"campusagent-{stamp}@local"
    return "\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//CampusAgent Router//CN",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{title}",
            "END:VEVENT",
            "END:VCALENDAR",
        ]
    )


def call_deepseek(system_prompt, user_prompt):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None
    try:
        payload = {
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "thinking": {"type": DEEPSEEK_THINKING},
            "temperature": 0.2,
        }
        request = urllib.request.Request(
            DEEPSEEK_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def execute_tool(intent, text, context=""):
    if intent == "search":
        query = clean_query(text)
        encoded = urllib.parse.quote(query)
        return {
            "status": "success",
            "answer": f"已生成实时搜索入口：{query}",
            "actions": [
                {"type": "open_url", "label": "用 Bing 搜索", "url": f"https://www.bing.com/search?q={encoded}"},
                {"type": "open_url", "label": "用 GitHub 搜索", "url": f"https://github.com/search?q={encoded}&type=repositories"},
            ],
        }

    if intent == "reminder":
        title, start, end = parse_reminder(text)
        ics = build_ics(title, start, end)
        return {
            "status": "success",
            "answer": f"已生成日历提醒：{title}，时间 {start.strftime('%Y-%m-%d %H:%M')}。",
            "actions": [{"type": "download", "label": "下载日历提醒 .ics", "filename": "campusagent-reminder.ics", "content": ics}],
        }

    if intent == "summarize":
        prompt = f"请用中文把下面内容总结成 3-5 个要点：\n\n{context or text}"
        answer = call_deepseek("你是一个擅长学习和办公文本总结的助手。", prompt) or local_summary(context or text)
        return {"status": "success", "answer": answer, "actions": []}

    if intent == "rag_qa":
        prompt = f"只根据给定资料回答问题。问题：{text}\n\n资料：\n{context}"
        answer = call_deepseek("你是本地知识库问答助手，必须基于资料回答，不编造。", prompt) or local_rag_answer(text, context)
        return {"status": "success", "answer": answer, "actions": []}

    if intent == "translate":
        prompt = f"请翻译或改写以下内容，保持自然准确：\n\n{context or text}"
        answer = call_deepseek("你是专业翻译与双语表达助手。", prompt)
        if not answer:
            answer = "翻译任务需要更高质量的语言模型。请启动 FastAPI 后设置 DEEPSEEK_API_KEY，或在资料区粘贴要翻译的正文。"
        return {"status": "success", "answer": answer, "actions": []}

    if intent == "code":
        prompt = f"请根据用户需求给出可执行的代码建议、解释或修复方案：\n\n需求：{text}\n\n代码或报错：\n{context}"
        answer = call_deepseek("你是严谨的代码助手，回答要可执行、可检查。", prompt)
        if not answer:
            answer = "代码助手执行层已就绪。设置 DEEPSEEK_API_KEY 后可返回真实代码解释、修复方案和示例。"
        return {"status": "success", "answer": answer, "actions": []}

    prompt = f"请简洁自然地回复用户：{text}"
    answer = call_deepseek("你是友好、可靠的校园 AI 助手。", prompt) or "我可以继续陪你聊，也可以帮你把问题转成搜索、总结、翻译、代码或提醒任务。"
    return {"status": "success", "answer": answer, "actions": []}
