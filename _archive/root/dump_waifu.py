import json
from pathlib import Path

p = Path("reports/hermes_output/stockpile_drafts/article_blocks_WAIFU.json")
with open(p, "r", encoding="utf-8") as f:
    data = json.load(f)

with open("waifu_text.txt", "w", encoding="utf-8") as out:
    out.write(f"Title: {data.get('title')} (Length: {len(data.get('title', ''))})\n\n")
    for i, b in enumerate(data.get("blocks", [])):
        btype = b.get("type")
        if btype == "tool_header":
            out.write(f"\n[{i}] TOOL: {b.get('name')} (★{b.get('stars')})\n")
        elif btype == "paragraph":
            out.write(f"[{i}] P: {b.get('text')}\n")
        elif btype == "image":
            out.write(f"[{i}] IMG: {b.get('caption')} -> {Path(b.get('path', '')).name}\n")
        elif btype == "source":
            out.write(f"[{i}] SRC: {b.get('text')}\n")

print("Saved waifu_text.txt")
