# revit_mcp_client.py
# 作用：示例从 Revit-MCP（假定在本地运行并暴露 HTTP API）获取模型的 MEP 构件数据并存为 JSON。
# 说明：实际 revit-mcp API 路径/字段请参考你安装的 revit-mcp README，本脚本做示意适配。

import requests
import json
from typing import List, Dict

REVIT_MCP_URL = "http://localhost:5000"  # 如果 revit-mcp 在本机运行，修改为实际端口/路径

def fetch_mep_elements(project_id: str) -> List[Dict]:
    """
    从 revit-mcp 获取 MEP 构件清单（示例接口）。
    返回每个元素包含至少：id, type, system, level, bbox([xmin,ymin,zmin,xmax,ymax,zmax]), metadata
    """
    # 以下 URL/参数 需根据你实际的 revit-mcp API 做修改
    resp = requests.get(f"{REVIT_MCP_URL}/api/projects/{project_id}/mep-elements")
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python revit_mcp_client.py <project_id> <out.json>")
        sys.exit(1)
    project_id = sys.argv[1]
    out_path = sys.argv[2]
    elems = fetch_mep_elements(project_id)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(elems, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(elems)} elements to {out_path}")
