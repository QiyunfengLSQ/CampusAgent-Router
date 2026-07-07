import random
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

SEED = 42


INTENT_SPECS = {
    "search": {
        "objects": ["杭州今天的天气", "最近的AI新闻", "DeepSeek的最新进展", "考研报名时间", "Python 3.13新特性", "上海地铁运营信息", "新能源汽车销量", "校园讲座安排"],
        "templates": [
            "帮我查一下{obj}",
            "搜索{obj}",
            "我想了解现在{obj}是什么情况",
            "查一查网上关于{obj}的最新消息",
            "帮我找一下{obj}相关信息",
            "看看最近有没有{obj}的更新",
        ],
    },
    "rag_qa": {
        "objects": ["上传资料里的结论", "我的笔记中KMP的解释", "本地知识库的这段内容", "课程PDF里的重点", "会议纪要中的行动项", "论文材料里的实验设置", "项目文档里的接口说明", "复习资料里的定义"],
        "templates": [
            "根据{obj}回答这个问题",
            "在{obj}里面找答案",
            "只基于{obj}帮我解释一下",
            "从{obj}里查一下相关内容",
            "不要联网，按{obj}回答",
            "结合{obj}给我一个准确答复",
        ],
    },
    "summarize": {
        "objects": ["这篇文章", "这段话", "这份报告", "课堂录音文字稿", "会议纪要", "论文摘要", "产品需求文档", "新闻材料"],
        "templates": [
            "帮我总结一下{obj}",
            "提炼{obj}的重点",
            "把{obj}总结成三点",
            "给{obj}写一个简短摘要",
            "压缩{obj}，保留核心信息",
            "归纳{obj}里的主要观点",
        ],
    },
    "code": {
        "objects": ["一个快排", "这段C++代码", "这个Python报错", "FastAPI接口", "SQL查询语句", "前端按钮样式", "单元测试", "数据读取函数"],
        "templates": [
            "帮我写{obj}",
            "解释一下{obj}",
            "修复{obj}",
            "给{obj}加上注释",
            "优化{obj}的实现",
            "看看{obj}为什么运行失败",
        ],
    },
    "reminder": {
        "objects": ["明天早上八点背单词", "下周一交作业", "今晚十点休息", "周五下午开组会", "每天晚上复习数学", "考试前一天整理资料", "月底提交报销", "下午三点喝水"],
        "templates": [
            "{obj}提醒我",
            "帮我安排{obj}",
            "创建一个{obj}的日程",
            "到时候提醒我{obj}",
            "把{obj}加入计划",
            "设置提醒：{obj}",
        ],
    },
    "translate": {
        "objects": ["这句话翻译成英文", "这段英语翻译成中文", "中文改成英文表达", "邮件内容翻译成日语", "摘要翻译成学术英语", "这句口语换成正式英文", "简历项目翻译成英文", "这段中文润色成英文"],
        "templates": [
            "帮我把{obj}",
            "请{obj}",
            "我需要{obj}",
            "能不能{obj}",
            "直接{obj}",
            "把下面内容{obj}",
        ],
    },
    "chat": {
        "objects": ["我今天该干嘛", "陪我聊一会儿", "我有点累了怎么办", "你觉得我适合学什么", "给我一点鼓励", "我们随便聊聊", "我现在有点迷茫", "你怎么看待拖延"],
        "templates": [
            "{obj}",
            "想问问你，{obj}",
            "不做任务，{obj}",
            "和我说说，{obj}",
            "我想放松一下，{obj}",
            "你可以陪我想想吗，{obj}",
        ],
    },
}


def build_samples(per_label=180):
    random.seed(SEED)
    rows = []
    for label, spec in INTENT_SPECS.items():
        seen = set()
        while len(seen) < per_label:
            template = random.choice(spec["templates"])
            obj = random.choice(spec["objects"])
            prefix = random.choice(["", "请", "麻烦你", "现在", "如果可以的话"])
            suffix = random.choice(["", "谢谢", "尽量简洁", "给我详细一点", "适合学习场景"])
            text = f"{prefix}{template.format(obj=obj)}{suffix}"
            seen.add(text)
        rows.extend({"text": text, "label": label} for text in sorted(seen))
    random.shuffle(rows)
    return rows


def split_rows(rows):
    by_label = {}
    for row in rows:
        by_label.setdefault(row["label"], []).append(row)
    train, valid, test = [], [], []
    for label_rows in by_label.values():
        n = len(label_rows)
        train.extend(label_rows[: int(n * 0.8)])
        valid.extend(label_rows[int(n * 0.8) : int(n * 0.9)])
        test.extend(label_rows[int(n * 0.9) :])
    random.shuffle(train)
    random.shuffle(valid)
    random.shuffle(test)
    return train, valid, test


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    rows = build_samples()
    train, valid, test = split_rows(rows)
    out_dir = Path("data/processed")
    write_jsonl(out_dir / "train.jsonl", train)
    write_jsonl(out_dir / "valid.jsonl", valid)
    write_jsonl(out_dir / "test.jsonl", test)
    print(f"generated total={len(rows)} train={len(train)} valid={len(valid)} test={len(test)}")


if __name__ == "__main__":
    main()
