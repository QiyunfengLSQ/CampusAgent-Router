# CampusAgent Router

CampusAgent Router is a lightweight AI Agent intent recognition and tool routing project. It classifies user requests into seven intents and recommends the next tool for an Agent workflow.

The repository also includes a static technology-style web interface that can be opened directly or deployed with GitHub Pages.

## Features

- Chinese intent dataset generation.
- Tiny PyTorch Transformer classifier without HuggingFace or pretrained models.
- Training, evaluation, metrics export, and badcase report.
- FastAPI inference service with `/health`, `/predict`, and `/route`.
- Static web UI with separated user and admin pages.
- User page supports local static demo mode and optional FastAPI live mode.
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

When FastAPI is not running, the user page uses a built-in static demo router. When FastAPI is running on `http://127.0.0.1:8000`, the page calls the real `/route` API automatically.

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
