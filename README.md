# 出海指挥官 (Export Commander)

> 跨境电商 AI 营销闭环系统 | AI+跨境黑客松巅峰赛 · 场景二：AI智能营销

## 一句话介绍
**大管家(大脑) × 第三方服务矩阵(手脚)** —— 一个对话式 AI 营销操盘手，
把「策略 → 素材 → 红人/投流 → 诊断 → 迭代」全链路串成闭环，并持续自我优化。

## 核心亮点
- 🧠 **大管家智能层**：理解用户意图 → 制定调用计划 → 分析每个模块结果 → 全流程优化建议（策略/分析/优化三层智能）
- 🧩 **第三方服务矩阵**：只做**对接与编排**，不重复造轮子 —— 策略(卖家精灵/SimilarWeb/Jungle Scout)、素材(Canva/AdCreative.ai/Midjourney/Synthesia)、红人(Upfluence/Grin/HypeAuditor)、投流(TikTok/Meta/Google Ads)、诊断(Northbeam/Triple Whale/Rockerbox)，均可切换/多选
- 🔄 **双引擎并行**：红人种草 ⊕ 投流放大，可只开一条、也可同时开启
- 📦 **商品库**：多商品批量管理，每商品独立闭环与历史
- 📊 **效果闭环**：ROUND 循环历史（ROAS/花费/收入），迭代建议自动反哺下一轮策略
- 🧪 **模拟演示模式**：默认开启，全程离线零 Token 消耗，适合现场 Demo；有额度时一键切回真实大模型

## 运行
```bash
pip install -r requirements.txt
streamlit run frontend/app.py --server.port=8501
# 或 python run.py
```
浏览器打开 http://localhost:8501

## 体验方式（已上线）

- 线上 Demo：https://export-commander-ai-6yxng2upjur3gqkdccmbfq.streamlit.app/
- 本地运行：`pip install -r requirements.txt` && `streamlit run frontend/app.py`

## 演示视频

- **演示视频/demo.mp4**（63 秒实录：5 秒标题卡+中文配音解说 → 全流程 → 素材/红人/投流/诊断闭环 → ROUND 效果卡）

## 技术说明

- 架构、创新点、闭环设计、模拟/真实模式与后续规划见 **`技术说明.md`**

## 演示流程（推荐）

1. 侧边栏保持「模拟演示模式」开（默认）
2. 右侧对话大管家输入：**全流程**（或点快捷指令 🚀 全流程）
3. 观察中间栏 5 个模块依次执行：策略 → 素材(文案+主图) → 红人匹配 → 多渠道投流 → 诊断+迭代
4. 顶部出现 ROUND 1 效果卡片：ROAS / 花费 / 收入
5. 再次输入「全流程」→ 上轮迭代建议自动应用（闭环）

## 部署（免费）
支持任何可运行 Python Streamlit 的平台（Hugging Face Spaces / Streamlit Cloud / Render / Railway / Docker）：

| 平台 | 免费额度 | 说明 |
|---|---|---|
| Hugging Face Spaces | 免费 CPU | `sdk: streamlit` + `app_file: frontend/app.py`，无需信用卡 |
| Streamlit Community Cloud | 免费公开应用 | GitHub 仓库关联，2 分钟部署 |

- 部署环境默认 `MOCK_MODE=true`（无需任何密钥即可演示）
- 恢复真实模型：把 `.env.example` 复制为 `.env` 填入 API Key，并设 `MOCK_MODE=false`

## 项目结构
```
├── frontend/app.py         # Streamlit 三栏 UI（商品库 | 模块矩阵 | 大管家）
├── app/
│   ├── config.py           # 环境变量 + MOCK_MODE 开关
│   ├── llm.py              # 百炼 OpenAI 兼容客户端
│   ├── prompts.py          # 大模型 Prompt（模块 + 管家智能层）
│   ├── mockdata.py         # 全链路模拟数据（离线演示）
│   └── agents/core.py      # 模块函数 + 管家函数（steward_chat/analyze/optimize）
├── .env.example            # 环境变量模板（不提交密钥）
├── Dockerfile / runtime.txt
└── 交接文档.md              # 开发与部署细节
```
