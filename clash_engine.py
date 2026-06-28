# clash_engine.py
# 作用：对从 Revit 导出的 MEP 构件（包含 bbox）做 AABB 碰撞检测，输出冲突列表 JSON。
# 说明：此 PoC 使用 rtree 做索引，AABB 重叠判定为“可能冲突”；可扩展为读取 mesh 并做精确碰撞。

import json
from rtree import index
from typing import Dict, List, Tuple

def bbox_overlap(b1: List[float], b2: List[float]) -> bool:
    # b = [xmin, ymin, zmin, xmax, ymax, zmax]
    return not (b1[3] <= b2[0] or b1[0] >= b2[3] or b1[4] <= b2[1] or b1[1] >= b2[4] or b1[5] <= b2[2] or b1[2] >= b2[5])

def build_index(elements: List[Dict]) -> Tuple[index.Index, Dict[int, Dict]]:
    idx = index.Index()
    mapping = {}
    for i, el in enumerate(elements):
        bbox = el.get("bbox")
        if not bbox or len(bbox) != 6:
            continue
        idx.insert(i, bbox)
        mapping[i] = el
    return idx, mapping

def detect_clashes(elements: List[Dict]) -> List[Dict]:
    idx, mapping = build_index(elements)
    clashes = []
    processed = set()
    for i, el in mapping.items():
        bbox = el["bbox"]
        candidates = list(idx.intersection(bbox))
        for j in candidates:
            if j <= i:
                continue
            if (i, j) in processed:
                continue
            el_b = mapping.get(j)
            if not el_b:
                continue
            if bbox_overlap(bbox, el_b["bbox"]):
                clashes.append({
                    "a": {"id": el.get("id"), "type": el.get("type"), "system": el.get("system"), "level": el.get("level")},
                    "b": {"id": el_b.get("id"), "type": el_b.get("type"), "system": el_b.get("system"), "level": el_b.get("level")},
                    "a_bbox": bbox,
                    "b_bbox": el_b["bbox"],
                    "severity": "possible",
                })
            processed.add((i, j))
    return clashes

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python clash_engine.py elements.json out_clashes.json")
        sys.exit(1)
    elems_path = sys.argv[1]
    out_path = sys.argv[2]
    with open(elems_path, "r", encoding="utf-8") as f:
        elements = json.load(f)
    clashes = detect_clashes(elements)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"clash_count": len(clashes), "clashes": clashes}, f, ensure_ascii=False, indent=2)
    print(f"Detected {len(clashes)} clashes, saved to {out_path}")
