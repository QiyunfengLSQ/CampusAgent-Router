from app.executor import execute_tool


def test_execute_search_returns_links():
    result = execute_tool("search", "帮我查一下最近的 AI 新闻")
    assert result["status"] == "success"
    assert result["actions"][0]["type"] == "open_url"
    assert "bing.com" in result["actions"][0]["url"]


def test_execute_reminder_returns_ics():
    result = execute_tool("reminder", "明天早上八点提醒我背单词")
    assert result["status"] == "success"
    assert result["actions"][0]["filename"].endswith(".ics")
    assert "BEGIN:VCALENDAR" in result["actions"][0]["content"]


def test_execute_rag_uses_context():
    result = execute_tool("rag_qa", "KMP 是什么", "KMP 是一种字符串匹配算法。它通过 next 数组减少重复比较。")
    assert result["status"] == "success"
    assert "KMP" in result["answer"]
