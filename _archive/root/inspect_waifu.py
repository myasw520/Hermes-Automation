import json
from pathlib import Path

p = Path("reports/hermes_output/stockpile_drafts/article_blocks_WAIFU.json")
with open(p, "r", encoding="utf-8") as f:
    data = json.load(f)

print("Title:", data.get("title"))
print("Title len:", len(data.get("title", "")))

for i, b in enumerate(data.get("blocks", [])):
    btype = b.get("type")
    if btype == "tool_header":
        print(f"\n[{i}] TOOL: {b.get('name')} (★{b.get('stars')})")
    elif btype == "paragraph":
        print(f"[{i}] P: {b.get('text')}")
    elif btype == "image":
        print(f"[{i}] IMG: {b.get('caption')} -> {Path(b.get('path', '')).name}")
    elif btype == "source":
        print(f"[{i}] SRC: {b.get('text')}")
