# CampusAgent Router JD Mapping

CampusAgent Router 是一个面向 AI Agent 前置理解层的小型完整项目。它覆盖数据构造、轻量 Transformer 训练、评估、推理服务和工具路由，适合在简历和面试中展示工程闭环能力。

## 1. 服务端开发工程师

- JD 关键词：Python、FastAPI、RESTful API、Pydantic、服务健康检查、工程化测试。
- 本项目对应能力：实现 `/health`、`/predict`、`/route` 接口，封装 predictor 生命周期，使用 schema 管理请求响应，并用 pytest 覆盖 API。
- 面试介绍：我把模型推理能力封装成可部署服务，接口既能返回 intent 也能返回 Agent 工具路由，服务层和模型层解耦，便于后续替换模型或接入网关。

## 2. AI 搜索算法 / 架构工程师

- JD 关键词：Query Understanding、意图识别、搜索路由、召回前置分类、评估指标。
- 本项目对应能力：对搜索、RAG、总结、代码、提醒、翻译、闲聊进行 query 分类，并把 search 路由到 web_search，把 rag_qa 路由到 local_rag。
- 面试介绍：项目模拟搜索和 Agent 系统中的 query understanding 模块，先判断用户是否需要实时搜索、知识库问答或普通生成，再决定下游工具。

## 3. Agent Infra 研发工程师

- JD 关键词：Agent Router、Tool Calling、Intent Routing、工具编排、可观测性。
- 本项目对应能力：`app/router.py` 维护 intent 到工具的映射和 reason，`/route` 返回结构化决策结果，可直接作为 Agent 执行器的前置节点。
- 面试介绍：我没有只做文本分类 demo，而是把分类输出转换为工具调用建议，让 Agent 在执行任务前先完成可解释的路由决策。

## 4. 大模型训练 / 推理框架工程师

- JD 关键词：PyTorch、Transformer、训练循环、GPU、模型保存、推理封装。
- 本项目对应能力：从零实现字符 tokenizer、Embedding、可学习位置编码、TransformerEncoder、attention mask、mean pooling 和分类头，自动使用 CUDA。
- 面试介绍：项目不用 HuggingFace 和预训练模型，自己实现小型 Transformer 分类器，训练脚本保存最优模型并提供独立推理加载流程。

## 5. 后训练数据 / 算法研究员

- JD 关键词：数据合成、标签体系、badcase 分析、分类评估、混淆矩阵。
- 本项目对应能力：自动生成七类中文意图数据，每类至少 150 条；评估输出 accuracy、precision、recall、f1、confusion matrix，并生成 badcase 报告。
- 面试介绍：我设计了 Agent 场景下的意图标签体系，并通过模板多样化构造训练数据，再用 badcase 分析定位容易混淆的用户表达。

## 6. 通用 Agent 数据产品经理

- JD 关键词：用户意图、场景抽象、工具体系、产品闭环、指标定义。
- 本项目对应能力：围绕学习、办公、生活助手设计七类意图和七类工具，输出 confidence 与 reason，方便产品侧理解 Agent 决策。
- 面试介绍：这个项目把用户自然语言请求转换成结构化工具路由结果，既能体现产品场景拆解，也能体现数据、模型和 API 的完整落地。
