# 出海指挥官 Export Director

跨境外贸 AI 智能营销总控台：**大管家 × 第三方服务矩阵**，
一句话完成「策略 → 素材 → 红人种草/智能投流 → 投放诊断 → 优化迭代」的闭环。
**第三方负责“做”，大管家负责“想、解读、复盘、进化”，实现 1+1>2。**

## 交付物

| 提交项 | 位置 |
|---|---|
| 线上 Demo | https://export-commander-ai-6yxng2upjur3gqkdccmbfq.streamlit.app/ |
| 演示视频 | `演示视频/demo.mp4`（63 秒，含中文旁白解说） |
| 技术说明 | `技术说明.md` |

## 体验方式

1. 打开线上 Demo，对右侧大管家发送 **“全流程”**；
2. 观察模块逐一亮起，大管家逐段解读；
3. 顶部出现 **ROUND 效果卡**，再次运行可看迭代反哺。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run frontend/app.py
```

默认演示模式（零成本、离线可跑）；接入真实模型：复制 `.env.example` 为 `.env` 并填入 Key。

## 附注

已适配阿里云百炼大模型（OpenAI 兼容协议）；当前演示因 Token 额度有限使用内置演示数据。
