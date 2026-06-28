# skill_api.py
# Flask 服务，提供 /audit-mep-clashes 接口：接收冲突 JSON，调用本地 Ollama（示例）并返回整改建议。
# 启动前请设置环境变量 OLLAMA_URL，例如：
# Windows PowerShell: $env:OLLAMA_URL="http://localhost:11434/api/generate"

from flask import Flask, request, jsonify
import os
import requests
import json

app = Flask(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")

PROMPT_TEMPLATE = """
你是有经验的 BIM 协调工程师，特别擅长机电（MEP）碰撞判定和整改建议。
下面提供了工程 {project} 的若干 MEP 碰撞（JSON 列表），每条含构件 A/B 的类型、系统、楼层、bbox。
请以 JSON 格式返回：
- summary: 简短中文总结
- actions: 数组（每项包含 clash_id, priority(高/中/低), responsible(电/暖/通/给排水/结构), recommendation(具体整改步骤), estimated_hours(粗略工时), ticket_text(可复制到工单系统)）
只处理最多前 50 条碰撞，如超出请先聚类并汇总。
现在：{clash_json}
"""

def call_ollama(prompt: str) -> str:
    body = {
        "model": "llama2",   # 根据你在 Ollama 中安装的模型名调整
        "prompt": prompt,
        "max_tokens": 2000
    }
    resp = requests.post(OLLAMA_URL, json=body, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    if "results" in data:
        out_texts = []
        for r in data["results"]:
            for c in r.get("content", []):
                if c.get("type") == "output_text":
                    out_texts.append(c.get("text", ""))
        return "\n".join(out_texts)
    return data if isinstance(data, str) else json.dumps(data)

@app.route("/audit-mep-clashes", methods=["POST"])
def audit_mep_clashes():
    payload = request.get_json()
    project = payload.get("project", "Unknown Project")
    clashes = payload.get("clashes", [])
    limited_clashes = clashes[:50]
    clash_json = json.dumps(limited_clashes, ensure_ascii=False)
    prompt = PROMPT_TEMPLATE.format(project=project, clash_json=clash_json)
    try:
        llm_resp = call_ollama(prompt)
        parsed = json.loads(llm_resp)
        return jsonify({"ok": True, "llm_result": parsed})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "debug_prompt": prompt}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
