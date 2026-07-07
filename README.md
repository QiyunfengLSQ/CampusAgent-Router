# CampusAgent Router

CampusAgent Router is a lightweight AI Agent intent recognition and tool routing project. It classifies user requests into seven intents and recommends the next tool for an Agent workflow.

The repository also includes a static technology-style web interface that can be opened directly or deployed with GitHub Pages.

## Features

- Chinese intent dataset generation.
- Tiny PyTorch Transformer classifier without HuggingFace or pretrained models.
- Training, evaluation, metrics export, and badcase report.
- FastAPI inference service with `/health`, `/predict`, and `/route`.
- FastAPI execution service with `/execute`.
- Static web UI with separated user and admin pages.
- User page supports local static execution and optional FastAPI + DeepSeek live mode.
- Admin page shows dataset, model, route table, and run commands.

## Intent And Route Mapping

| Intent | Route |
|---|---|
| search | web_search |
| rag_qa | local_rag |
| summarize | text_summarizer |
| code | code_assistant |
| reminder | calendar_reminder |
| translate | translator |
| chat | general_chat |

## Project Structure

```text
app/
  main.py
  predictor.py
  router.py
  schemas.py
tinyintent/
  dataset.py
  evaluate.py
  model.py
  tokenizer.py
  train.py
  utils.py
scripts/
  make_dataset.py
  train_model.py
  eval_model.py
  predict_demo.py
tests/
web/
  app.js
  styles.css
index.html
user.html
admin.html
```

## Web UI

Open these files directly in a browser:

- `index.html`: project entrance.
- `user.html`: user-side router console.
- `admin.html`: admin dashboard.

When FastAPI is not running, the user page still performs practical local actions:

- `search`: opens real search result links.
- `reminder`: generates a downloadable `.ics` calendar file.
- `summarize`: creates a simple local extractive summary.
- `rag_qa`: searches pasted/uploaded local text and returns evidence.

When FastAPI is running on `http://127.0.0.1:8000`, the page calls the real `/execute` API automatically. If `DEEPSEEK_API_KEY` is set, summarize, RAG QA, translate, code, and chat use DeepSeek for stronger answers.

## Windows Setup

Torch is intentionally not listed in `requirements.txt`. Install your CUDA PyTorch build separately first.

```bat
pip install -r requirements.txt
```

Check CUDA:

```bat
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')"
```

## Generate Dataset

```bat
python scripts\make_dataset.py
```

## Train

```bat
python scripts\train_model.py
```

Training logs include device, epoch, train loss, train accuracy, validation loss, and validation accuracy. The best model is saved to `artifacts\model.pt`.

## Evaluate

```bat
python scripts\eval_model.py
```

Evaluation writes:

- `artifacts\metrics.json`
- `reports\badcases.md`

## Prediction Demo

```bat
python scripts\predict_demo.py
```

If Chinese output looks garbled in PowerShell, run:

```bat
chcp 65001
```

## Start API

Optional DeepSeek setup:

```bat
set DEEPSEEK_API_KEY=your_deepseek_api_key
set DEEPSEEK_MODEL=deepseek-v4-flash
set DEEPSEEK_THINKING=disabled
```

PowerShell:

```powershell
$env:DEEPSEEK_API_KEY="your_deepseek_api_key"
$env:DEEPSEEK_MODEL="deepseek-v4-flash"
$env:DEEPSEEK_THINKING="disabled"
```

```bat
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## API Examples

`GET /health`

```json
{
  "status": "ok",
  "device": "cuda",
  "model_loaded": true
}
```

`POST /predict`

```json
{
  "text": "帮我总结一下这篇文章"
}
```

`POST /route`

```json
{
  "text": "帮我查一下最近的 AI 新闻"
}
```

`POST /execute`

```json
{
  "text": "根据资料回答 KMP 是什么",
  "context": "KMP 是一种字符串匹配算法，它通过 next 数组减少重复比较。"
}
```

Example response:

```json
{
  "intent": "rag_qa",
  "confidence": 0.94,
  "route_to": "local_rag",
  "reason": "用户需要基于本地资料或知识库进行问答。",
  "status": "success",
  "answer": "KMP 是一种字符串匹配算法...",
  "actions": [],
  "scores": {
    "rag_qa": 0.94
  }
}
```

## What Happens After Intent Recognition

The project now follows a complete Agent pipeline:

```text
user query -> intent classifier -> route selector -> tool executor -> final result
```

Execution behavior:

| Intent | Executor Result |
|---|---|
| search | Generates real search links. |
| reminder | Generates a downloadable calendar `.ics` file. |
| summarize | Summarizes pasted text locally or through DeepSeek. |
| rag_qa | Answers using pasted/uploaded local context, optionally through DeepSeek. |
| translate | Uses DeepSeek when API key is configured. |
| code | Uses DeepSeek for code explanation and repair when API key is configured. |
| chat | Uses DeepSeek when API key is configured, otherwise returns a local assistant response. |

## DeepSeek API Setup Guide

1. Create a DeepSeek API key.

   Open:

   ```text
   https://platform.deepseek.com/api_keys
   ```

   Sign in, create an API key, and copy it once. Treat it like a password.

2. Never put the API key in frontend files.

   Do not write your key into `index.html`, `user.html`, `web/app.js`, browser console code, GitHub Pages, or README. This project only reads the key from backend environment variables.

3. Install dependencies.

   ```bat
   pip install -r requirements.txt
   ```

   `requirements.txt` intentionally does not include `torch`, `torchvision`, or `torchaudio`.

4. Set the key in Windows cmd.

   ```bat
   set DEEPSEEK_API_KEY=sk-your-key-here
   set DEEPSEEK_MODEL=deepseek-v4-flash
   set DEEPSEEK_THINKING=disabled
   uvicorn app.main:app --reload
   ```

5. Or set the key in PowerShell.

   ```powershell
   $env:DEEPSEEK_API_KEY="sk-your-key-here"
   $env:DEEPSEEK_MODEL="deepseek-v4-flash"
   $env:DEEPSEEK_THINKING="disabled"
   uvicorn app.main:app --reload
   ```

6. Open the user page.

   Open `user.html` directly or open the GitHub Pages URL. When the backend is running at `http://127.0.0.1:8000`, the page calls `/execute` automatically.

7. Try tasks that need DeepSeek.

   ```text
   把这句话翻译成英文：我正在做一个 Agent 路由项目
   ```

   ```text
   解释这段 Python 代码为什么报错
   ```

   ```text
   根据资料回答 KMP 是什么
   ```

8. Test the API directly.

   Windows cmd:

   ```bat
   curl -X POST http://127.0.0.1:8000/execute ^
     -H "Content-Type: application/json" ^
     -d "{\"text\":\"把这句话翻译成英文：我正在做一个 Agent 路由项目\",\"context\":\"\"}"
   ```

9. Optional model choices.

   - `deepseek-v4-flash`: recommended default for fast execution.
   - `deepseek-v4-pro`: stronger model for higher quality answers.

10. Common issues.

   - If the page shows `静态演示`, the FastAPI backend is not reachable.
   - If translate/code/chat returns a fallback message, check `DEEPSEEK_API_KEY`.
   - If GitHub Pages is open but local API is not running, only static local tools can work.
   - If PowerShell shows garbled Chinese, run `chcp 65001` in cmd or use UTF-8 terminal settings.

Example response:

```json
{
  "intent": "search",
  "confidence": 0.96,
  "route_to": "web_search",
  "reason": "用户需要获取实时外部信息。",
  "scores": {
    "search": 0.96,
    "rag_qa": 0.01
  }
}
```

## Test

```bat
python -m pytest
```

## Deploy With GitHub Pages

This project already has a static entry file at `index.html`, so GitHub Pages can serve it directly from the repository root.

Recommended repository description:

```text
Lightweight AI Agent intent recognition and tool routing system with a static web UI.
```

After pushing to GitHub, enable Pages:

1. Open repository settings.
2. Go to Pages.
3. Choose `Deploy from a branch`.
4. Select branch `main` and folder `/root`.
5. Save and wait for the Pages URL.

## Notes

- No Docker.
- No HuggingFace dependency.
- No pretrained model download.
- No `torch`, `torchvision`, or `torchaudio` in `requirements.txt`.
- The static UI can be opened without starting a server.
