# Revit2020 → 本地 MEP 碰撞审核 Skill PoC

这是一个演示仓库，用于本地部署的 MEP 碰撞检测与 LLM 审核 Skill（PoC）。

包含：
- revit_mcp_client.py — 从 revit-mcp 拉取 MEP 元素的示例脚本
- clash_engine.py — 使用 rtree 做 AABB 碰撞检测
- skill_api.py — Flask 服务，调用本地 Ollama（演示）
- sample/ 包含示例数据 elements.json 与 payload.json

README 简要内容见下。

