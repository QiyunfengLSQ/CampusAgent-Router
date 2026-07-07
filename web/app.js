const routeMap = {
  search: ["web_search", "用户需要获取实时外部信息。"],
  rag_qa: ["local_rag", "用户需要基于本地资料或知识库进行问答。"],
  summarize: ["text_summarizer", "用户需要压缩、提炼或总结文本内容。"],
  code: ["code_assistant", "用户需要生成、修改、解释或调试代码。"],
  reminder: ["calendar_reminder", "用户需要创建提醒、日程或计划。"],
  translate: ["translator", "用户需要进行语言翻译或改写表达。"],
  chat: ["general_chat", "用户正在进行开放式闲聊或情绪交流。"]
};

const intentNames = {
  search: "搜索资料",
  rag_qa: "资料问答",
  summarize: "文本总结",
  code: "代码处理",
  reminder: "提醒日程",
  translate: "翻译改写",
  chat: "普通聊天"
};

const toolNames = {
  web_search: "打开搜索入口",
  local_rag: "本地资料问答",
  text_summarizer: "文本总结工具",
  code_assistant: "代码助手",
  calendar_reminder: "日历提醒",
  translator: "翻译工具",
  general_chat: "普通对话"
};

const keywordRules = [
  ["search", ["查", "搜索", "最近", "最新", "新闻", "天气", "进展"]],
  ["rag_qa", ["上传", "资料", "笔记", "知识库", "本地", "根据"]],
  ["summarize", ["总结", "提炼", "摘要", "归纳", "重点"]],
  ["code", ["代码", "报错", "Python", "C++", "接口", "函数", "修复"]],
  ["reminder", ["提醒", "日程", "明天", "下周", "安排", "计划"]],
  ["translate", ["翻译", "英文", "英语", "中文", "改写"]],
  ["chat", ["聊", "陪我", "累", "迷茫", "鼓励", "怎么办"]]
];

const telemetryKey = "campusagent_router_events";
const maxTelemetryItems = 40;

function displayIntent(intent) {
  return intentNames[intent] || intent;
}

function displayTool(tool) {
  return toolNames[tool] || tool;
}

function normalizeScores(scores) {
  return Object.fromEntries(Object.entries(scores).map(([key, value]) => [key, Number(value)]));
}

function fallbackRoute(text) {
  const scores = {};
  Object.keys(routeMap).forEach((key) => {
    scores[key] = 0.03;
  });
  let best = "chat";
  let bestHits = 0;
  keywordRules.forEach(([intent, words]) => {
    const hits = words.filter((word) => text.includes(word)).length;
    if (hits > bestHits) {
      best = intent;
      bestHits = hits;
    }
  });
  scores[best] = Math.min(0.96, 0.72 + bestHits * 0.08);
  const [routeTo, reason] = routeMap[best];
  return {
    intent: best,
    route_to: routeTo,
    reason,
    confidence: scores[best],
    scores
  };
}

function cleanQuery(text) {
  return text
    .replace(/帮我|请|一下|搜索|查一查|查一下|最近|最新|相关信息|谢谢/g, " ")
    .replace(/\s+/g, " ")
    .trim() || text.trim();
}

function splitSentences(text) {
  const parts = text.split(/([。！？!?；;])/);
  const sentences = [];
  for (let index = 0; index < parts.length; index += 2) {
    const sentence = `${parts[index] || ""}${parts[index + 1] || ""}`.trim();
    if (sentence) sentences.push(sentence);
  }
  return sentences;
}

function localSummary(text) {
  if (!text.trim()) return "没有提供可总结的正文。请在资料区粘贴文章、报告或会议纪要。";
  const sentences = splitSentences(text);
  return (sentences.length ? sentences.slice(0, 3) : [text.slice(0, 260)])
    .map((sentence, index) => `${index + 1}. ${sentence}`)
    .join("\n");
}

function localRagAnswer(question, context) {
  if (!context.trim()) return "没有提供本地资料。请在资料区粘贴笔记、文档内容，或上传 txt/md 文件。";
  const compact = question.replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, "");
  const terms = [];
  for (let index = 0; index < compact.length - 1; index += 1) {
    terms.push(compact.slice(index, index + 2));
  }
  const chunks = splitSentences(context);
  const scored = chunks
    .map((chunk) => [terms.filter((term) => chunk.includes(term)).length, chunk])
    .filter(([score]) => score > 0)
    .sort((a, b) => b[0] - a[0])
    .slice(0, 3)
    .map(([, chunk]) => chunk);
  if (!scored.length) return `资料中没有找到明显匹配片段。资料开头：\n${context.slice(0, 360)}`;
  return `基于本地资料找到以下依据：\n${scored.map((line, index) => `${index + 1}. ${line}`).join("\n")}`;
}

function parseReminder(text) {
  const date = new Date();
  if (text.includes("明天")) date.setDate(date.getDate() + 1);
  if (text.includes("后天")) date.setDate(date.getDate() + 2);
  let hour = 9;
  let minute = 0;
  const hourMap = { 一点: 1, 两点: 2, 二点: 2, 三点: 3, 四点: 4, 五点: 5, 六点: 6, 七点: 7, 八点: 8, 九点: 9, 十点: 10, 十一点: 11, 十二点: 12 };
  Object.entries(hourMap).forEach(([key, value]) => {
    if (text.includes(key)) hour = value;
  });
  const match = text.match(/(\d{1,2})[:：点](\d{1,2})?/);
  if (match) {
    hour = Number(match[1]);
    if (match[2]) minute = Number(match[2]);
  }
  if ((text.includes("下午") || text.includes("晚上")) && hour < 12) hour += 12;
  date.setHours(hour, minute, 0, 0);
  const title = text
    .replace(/提醒我|提醒|明天|后天|今天|早上|上午|下午|晚上|中午|\d{1,2}[:：点]\d{0,2}/g, " ")
    .replace(/\s+/g, " ")
    .trim() || "待办提醒";
  return { title, start: date, end: new Date(date.getTime() + 30 * 60 * 1000) };
}

function formatIcsDate(date) {
  const pad = (value) => String(value).padStart(2, "0");
  return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}T${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`;
}

function buildIcs(title, start, end) {
  const stamp = new Date().toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
  return [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//CampusAgent Router//CN",
    "BEGIN:VEVENT",
    `UID:campusagent-${stamp}@local`,
    `DTSTAMP:${stamp}`,
    `DTSTART:${formatIcsDate(start)}`,
    `DTEND:${formatIcsDate(end)}`,
    `SUMMARY:${title}`,
    "END:VEVENT",
    "END:VCALENDAR"
  ].join("\n");
}

function executeLocal(route, text, context) {
  if (route.intent === "search") {
    const query = cleanQuery(text);
    const encoded = encodeURIComponent(query);
    return {
      ...route,
      status: "success",
      answer: `已生成实时搜索入口：${query}`,
      actions: [
        { type: "open_url", label: "用 Bing 搜索", url: `https://www.bing.com/search?q=${encoded}` },
        { type: "open_url", label: "用 GitHub 搜索", url: `https://github.com/search?q=${encoded}&type=repositories` }
      ]
    };
  }
  if (route.intent === "reminder") {
    const item = parseReminder(text);
    return {
      ...route,
      status: "success",
      answer: `已生成日历提醒：${item.title}，时间 ${item.start.toLocaleString()}。`,
      actions: [{ type: "download", label: "下载日历提醒 .ics", filename: "campusagent-reminder.ics", content: buildIcs(item.title, item.start, item.end) }]
    };
  }
  if (route.intent === "summarize") {
    return { ...route, status: "success", answer: localSummary(context || text), actions: [] };
  }
  if (route.intent === "rag_qa") {
    return { ...route, status: "success", answer: localRagAnswer(text, context), actions: [] };
  }
  if (route.intent === "translate") {
    return { ...route, status: "needs_api", answer: "翻译到对应语言需要后端 DeepSeek。请在输入中说明目标语言，例如“翻译成中文/英文/日语”，并启动 FastAPI 设置 DEEPSEEK_API_KEY。", actions: [] };
  }
  if (route.intent === "code") {
    return { ...route, status: "needs_api", answer: "代码解释和修复需要后端 DeepSeek。请在资料区粘贴代码/报错，并启动带 API Key 的 FastAPI 服务。", actions: [] };
  }
  return { ...route, status: "success", answer: "我可以继续陪你聊，也可以把问题转成搜索、总结、翻译、代码或提醒任务。", actions: [] };
}

async function executeTask(text, context) {
  try {
    const response = await fetch("http://127.0.0.1:8000/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, context })
    });
    if (!response.ok) throw new Error("api unavailable");
    const badge = document.querySelector("#modeBadge");
    if (badge) badge.textContent = "后端在线";
    const result = await response.json();
    result.scores = normalizeScores(result.scores);
    return result;
  } catch {
    const badge = document.querySelector("#modeBadge");
    if (badge) badge.textContent = "本地模式";
    return executeLocal(fallbackRoute(text), text, context);
  }
}

function renderScores(scores) {
  const root = document.querySelector("#scoreList");
  if (!root) return;
  root.innerHTML = "";
  Object.entries(scores).forEach(([label, value]) => {
    const row = document.createElement("div");
    row.className = "score-row";
    row.innerHTML = `
      <span>${displayIntent(label)}</span>
      <div class="score-bar"><span style="width:${Math.round(value * 100)}%"></span></div>
      <b>${Number(value).toFixed(2)}</b>
    `;
    root.appendChild(row);
  });
}

function readTelemetry() {
  try {
    return JSON.parse(localStorage.getItem(telemetryKey) || "[]");
  } catch {
    return [];
  }
}

function writeTelemetry(items) {
  localStorage.setItem(telemetryKey, JSON.stringify(items.slice(0, maxTelemetryItems)));
}

function recordTelemetry(result, text) {
  const items = readTelemetry();
  items.unshift({
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    time: new Date().toLocaleString(),
    text,
    intent: result.intent,
    route_to: result.route_to,
    intent_name: displayIntent(result.intent),
    tool_name: displayTool(result.route_to),
    confidence: Number(result.confidence) || 0,
    status: result.status || "success",
    scores: result.scores || {}
  });
  writeTelemetry(items);
}

function renderActions(actions) {
  const root = document.querySelector("#actionList");
  if (!root) return;
  root.innerHTML = "";
  actions.forEach((action) => {
    if (action.type === "open_url") {
      const link = document.createElement("a");
      link.className = "action-button";
      link.href = action.url;
      link.target = "_blank";
      link.rel = "noreferrer";
      link.textContent = action.label;
      root.appendChild(link);
    }
    if (action.type === "download") {
      const button = document.createElement("button");
      button.className = "action-button";
      button.textContent = action.label;
      button.addEventListener("click", () => {
        const blob = new Blob([action.content], { type: "text/calendar;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = action.filename || "campusagent-output.txt";
        link.click();
        URL.revokeObjectURL(url);
      });
      root.appendChild(button);
    }
  });
}

async function runUserRoute() {
  const input = document.querySelector("#queryInput");
  const context = document.querySelector("#contextInput");
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;
  const result = await executeTask(text, context ? context.value : "");
  document.querySelector("#intentText").textContent = displayIntent(result.intent);
  document.querySelector("#routeText").textContent = displayTool(result.route_to);
  document.querySelector("#reasonText").textContent = result.reason;
  document.querySelector("#executionStatus").textContent = result.status;
  document.querySelector("#answerText").textContent = result.answer;
  recordTelemetry(result, text);
  renderActions(result.actions || []);
}

function setPendingPreview() {
  document.querySelector("#intentText").textContent = "待判断";
  document.querySelector("#routeText").textContent = "待选择";
  document.querySelector("#reasonText").textContent = "点击“执行任务”后，系统会识别意图、路由工具并返回执行结果。";
  document.querySelector("#executionStatus").textContent = "ready";
  document.querySelector("#answerText").textContent = "选择快捷场景或输入需求后，点击“执行任务”。";
  renderActions([]);
}

function setupUserPage() {
  const input = document.querySelector("#queryInput");
  const context = document.querySelector("#contextInput");
  if (!input) return;
  document.querySelector("#routeBtn").addEventListener("click", runUserRoute);
  document.querySelector("#clearBtn").addEventListener("click", () => {
    input.value = "";
    if (context) context.value = "";
    input.focus();
  });
  const fileInput = document.querySelector("#fileInput");
  if (fileInput && context) {
    fileInput.addEventListener("change", async () => {
      const file = fileInput.files[0];
      if (!file) return;
      context.value = await file.text();
    });
  }
  document.querySelectorAll(".sample").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".sample").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      input.value = button.dataset.text;
      setPendingPreview();
    });
  });
  setPendingPreview();
}

function setupAdminPage() {
  const table = document.querySelector("#routeTable");
  if (!table) return;
  table.innerHTML = Object.entries(routeMap)
    .map(([intent, [tool, reason]]) => `
      <div class="route-item">
        <b>${displayIntent(intent)}</b>
        <span>${displayTool(tool)} · ${reason}</span>
      </div>
    `)
    .join("");
  setupAdminMonitor();
}

function renderEventLog(items) {
  const root = document.querySelector("#eventLog");
  if (!root) return;
  if (!items.length) {
    root.innerHTML = '<div class="event-item"><span>暂无执行记录</span><p>打开用户端执行一次任务后，这里会自动更新。</p></div>';
    return;
  }
  root.innerHTML = items
    .slice(0, 12)
    .map((item) => `
      <div class="event-item">
        <span>${item.time} · ${item.status}</span>
        <p><b>${item.intent_name || displayIntent(item.intent)}</b> 交给 ${item.tool_name || displayTool(item.route_to)} · 模型置信度 ${Number(item.confidence).toFixed(2)}</p>
        <p>${item.text}</p>
      </div>
    `)
    .join("");
}

function renderAdminMonitor() {
  const items = readTelemetry();
  const latest = items[0];
  const count = document.querySelector("#runCount");
  const latestIntent = document.querySelector("#latestIntent");
  const latestRoute = document.querySelector("#latestRoute");
  const latestQuery = document.querySelector("#latestQuery");
  if (count) count.textContent = String(items.length);
  if (latestIntent) latestIntent.textContent = latest ? (latest.intent_name || displayIntent(latest.intent)) : "-";
  if (latestRoute) latestRoute.textContent = latest ? (latest.tool_name || displayTool(latest.route_to)) : "等待用户端执行任务";
  if (latestQuery) latestQuery.textContent = latest ? latest.text : "暂无数据";
  renderScores(latest ? latest.scores : {});
  renderEventLog(items);
}

function setupAdminMonitor() {
  renderAdminMonitor();
  const clearButton = document.querySelector("#clearMonitorBtn");
  if (clearButton) {
    clearButton.addEventListener("click", () => {
      writeTelemetry([]);
      renderAdminMonitor();
    });
  }
  window.addEventListener("storage", (event) => {
    if (event.key === telemetryKey) renderAdminMonitor();
  });
  setInterval(renderAdminMonitor, 1000);
}

setupUserPage();
setupAdminPage();
