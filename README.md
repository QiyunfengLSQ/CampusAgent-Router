# CampusAgent Router

一个面向学习、办公和日常助手场景的小工具。用户输入一句话后，系统会判断这是搜索、总结、翻译、提醒、代码处理、资料问答还是普通聊天，并把任务交给对应的功能执行。

静态网页可以直接打开；如果启动本地后端并配置 DeepSeek API，翻译、总结、代码处理和问答会得到更好的生成结果。

## 能做什么

| 用户想做的事 | 项目会做什么 |
|---|---|
| 查资料、查新闻 | 生成可点击的搜索入口 |
| 设置提醒 | 生成可下载的 `.ics` 日历文件 |
| 总结文章 | 对粘贴的正文做摘要 |
| 根据资料回答问题 | 从粘贴或上传的文本中找依据并回答 |
| 翻译成指定语言 | 接入 DeepSeek 后按目标语言翻译 |
| 解释或修复代码 | 接入 DeepSeek 后给出代码建议 |
| 普通聊天 | 接入 DeepSeek 后进行对话 |

## 页面说明

- `index.html`：项目首页。
- `user.html`：用户端，输入需求并执行任务。
- `admin.html`：管理端，查看执行记录、任务分配规则和模型置信度。

用户端不展示复杂的模型分数，只展示任务类型、执行工具和结果。管理端里的数字含义如下：

- `执行次数`：当前浏览器记录的使用次数。
- `模型置信度`：系统判断某个任务类型的把握程度。
- 这些数字不是额度消耗，也不是费用。

## 直接打开网页

双击打开：

```text
index.html
```

或者访问 GitHub Pages：

```text
https://qiyunfenglsq.github.io/CampusAgent-Router/
```

不启动后端时，网页仍然可以完成搜索入口、日历提醒、本地摘要和简单资料检索。

## 本地运行后端

安装小依赖：

```bat
pip install -r requirements.txt
```

注意：`requirements.txt` 不包含 `torch`、`torchvision`、`torchaudio`，PyTorch 需要你按自己的 CUDA 环境单独安装。

生成数据、训练和评估：

```bat
python scripts\make_dataset.py
python scripts\train_model.py
python scripts\eval_model.py
```

启动接口：

```bat
uvicorn app.main:app --reload
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

## 接入 DeepSeek

1. 到 DeepSeek 平台创建 API Key：

```text
https://platform.deepseek.com/api_keys
```

2. 在 Windows cmd 中设置：

```bat
set DEEPSEEK_API_KEY=你的key
set DEEPSEEK_MODEL=deepseek-v4-flash
set DEEPSEEK_THINKING=disabled
uvicorn app.main:app --reload
```

PowerShell：

```powershell
$env:DEEPSEEK_API_KEY="你的key"
$env:DEEPSEEK_MODEL="deepseek-v4-flash"
$env:DEEPSEEK_THINKING="disabled"
uvicorn app.main:app --reload
```

不要把 DeepSeek 密钥写进网页、GitHub、README 或 `web/app.js`。密钥只应该放在本地后端环境变量里。

## 测试

```bat
python -m pytest
```

## 项目结构

```text
app/          FastAPI 后端
tinyintent/   训练和推理代码
scripts/      数据生成、训练、评估和 demo
tests/        测试
web/          静态页面资源
index.html    首页
user.html     用户端
admin.html    管理端
```
