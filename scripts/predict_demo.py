import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.predictor import IntentPredictor
from app.router import route_intent


EXAMPLES = [
    "帮我查一下最近的AI新闻",
    "根据我上传的资料回答这个问题",
    "帮我总结一下这篇文章",
    "修复这个 Python 报错",
    "明天早上八点提醒我背单词",
    "把这句话翻译成英文",
    "陪我聊一会儿",
]


if __name__ == "__main__":
    predictor = IntentPredictor()
    for text in EXAMPLES:
        pred = predictor.predict(text)
        route = route_intent(pred["intent"])
        print({"text": text, **pred, **route})
