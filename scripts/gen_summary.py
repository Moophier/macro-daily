"""可选：用 Claude 根据真实数据生成「行情自动速览」，写入 content.json 的 auto 字段。
没有 ANTHROPIC_API_KEY 时自动跳过。只描述数据，不做预测、不编造新闻。"""
import os, json, pathlib, requests, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import fetch_data as fd

key = os.environ.get("ANTHROPIC_API_KEY")
if not key:
    print("无 API Key，跳过自动速览"); sys.exit(0)

series = json.loads((fd.ROOT / "series.json").read_text("utf-8"))
lines = []
for k, s in series.items():
    v, d = s["values"], s["dates"]
    rate = s["type"] == "rate"
    def chg(n):
        if len(v) <= n: return "NA"
        return (f"{(v[-1]-v[-1-n])*(100 if s['unit']=='%' else 1):+.1f}" + ("bp" if s['unit']=='%' else "")) if rate \
            else f"{(v[-1]/v[-1-n]-1)*100:+.2f}%"
    lines.append(f"{s['name']}: 最新{v[-1]} ({d[-1]}), 1日{chg(1)}, 5日{chg(5)}, 20日{chg(20)}")

prompt = ("你是宏观研究员。仅依据下列数据，写 3-4 条简洁的中文行情速览（每条一行，不加序号）。"
          "只描述数据事实与相对强弱，不要预测，不要编造新闻、政策或数据之外的原因。\n\n" + "\n".join(lines))
r = requests.post("https://api.anthropic.com/v1/messages",
    headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
    json={"model": "claude-sonnet-5-5", "max_tokens": 600, "messages": [{"role": "user", "content": prompt}]}, timeout=60)
r.raise_for_status()
text = "".join(b.get("text", "") for b in r.json()["content"])
items = [x.strip("-•· ").strip() for x in text.splitlines() if x.strip()]

cp = fd.ROOT / "content.json"
c = json.loads(cp.read_text("utf-8"))
c["auto"] = {"asof": max(s["dates"][-1] for s in series.values()), "items": items}
cp.write_text(json.dumps(c, ensure_ascii=False, indent=1), "utf-8")
fd.build()
