const routeMap = {
  search: ["web_search", "用户需要获取实时外部信息。"],
  rag_qa: ["local_rag", "用户需要基于本地资料或知识库进行问答。"],
  summarize: ["text_summarizer", "用户需要压缩、提炼或总结文本内容。"],
  code: ["code_assistant", "用户需要生成、修改、解释或调试代码。"],
  reminder: ["calendar_reminder", "用户需要创建提醒、日程或计划。"],
  translate: ["translator", "用户需要进行语言翻译或改写表达。"],
  chat: ["general_chat", "用户正在进行开放式闲聊或情绪交流。"]
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

async function predictRoute(text) {
  try {
    const response = await fetch("http://127.0.0.1:8000/route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (!response.ok) throw new Error("api unavailable");
    const badge = document.querySelector("#modeBadge");
    if (badge) badge.textContent = "API 在线";
    return await response.json();
  } catch {
    const badge = document.querySelector("#modeBadge");
    if (badge) badge.textContent = "静态演示";
    return fallbackRoute(text);
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
      <span>${label}</span>
      <div class="score-bar"><span style="width:${Math.round(value * 100)}%"></span></div>
      <b>${Number(value).toFixed(2)}</b>
    `;
    root.appendChild(row);
  });
}

async function runUserRoute() {
  const input = document.querySelector("#queryInput");
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;
  const result = await predictRoute(text);
  document.querySelector("#intentText").textContent = result.intent;
  document.querySelector("#routeText").textContent = result.route_to;
  document.querySelector("#confidenceText").textContent = Number(result.confidence).toFixed(2);
  document.querySelector("#reasonText").textContent = result.reason;
  renderScores(result.scores);
}

function setupUserPage() {
  const input = document.querySelector("#queryInput");
  if (!input) return;
  document.querySelector("#routeBtn").addEventListener("click", runUserRoute);
  document.querySelector("#clearBtn").addEventListener("click", () => {
    input.value = "";
    input.focus();
  });
  document.querySelectorAll(".sample").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".sample").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      input.value = button.dataset.text;
      runUserRoute();
    });
  });
  runUserRoute();
}

function setupAdminPage() {
  const table = document.querySelector("#routeTable");
  if (!table) return;
  table.innerHTML = Object.entries(routeMap)
    .map(([intent, [tool, reason]]) => `
      <div class="route-item">
        <b>${intent}</b>
        <span>${tool} · ${reason}</span>
      </div>
    `)
    .join("");
}

setupUserPage();
setupAdminPage();
