"""拉取行情 -> series.json，并合并 content.json 生成 data.js。
单个标的失败时沿用 series.json 里的旧数据；全部失败则退出码 1（不覆盖线上）。"""
import json, sys, pathlib, datetime as dt
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
N = 520  # 保留约 2 年交易日
# key: (yfinance代码, 名称, 单位, 类型, 小数位)
YF = {
    "SPX": ("^GSPC", "标普500", "点", "px", 2),
    "DXY": ("DX-Y.NYB", "美元指数", "", "px", 2),
    "USDCNY": ("CNY=X", "USD/CNY", "", "px", 4),
    "GOLD": ("GC=F", "黄金", "美元/盎司", "px", 1),
    "WTI": ("CL=F", "WTI原油", "美元/桶", "px", 2),
    "VIX": ("^VIX", "VIX", "", "rate", 2),
}
ORDER = ["SPX", "UST10", "CN10", "DXY", "USDCNY", "GOLD", "WTI", "VIX"]


def pack(s, name, unit, typ, dec):
    s = s.dropna().tail(N)
    return {"name": name, "unit": unit, "type": typ,
            "dates": [d.strftime("%Y-%m-%d") for d in pd.to_datetime(s.index)],
            "values": [round(float(v), dec) for v in s.values]}


def get_yf(code):
    import yfinance as yf
    df = yf.download(code, period="3y", interval="1d", progress=False, auto_adjust=False)
    s = df["Close"]
    return s.iloc[:, 0] if isinstance(s, pd.DataFrame) else s


def get_bonds():
    import akshare as ak
    df = ak.bond_zh_us_rate(start_date="20230101")
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.set_index("日期")
    return df["中国国债收益率10年"], df["美国国债收益率10年"]


def fetch():
    old = {}
    p = ROOT / "series.json"
    if p.exists():
        old = json.loads(p.read_text("utf-8"))
    out, ok = {}, 0
    for k, (code, name, unit, typ, dec) in YF.items():
        try:
            out[k] = pack(get_yf(code), name, unit, typ, dec); ok += 1
        except Exception as e:
            print(f"[warn] {k} 失败: {e}", file=sys.stderr)
    try:
        cn, us = get_bonds()
        out["CN10"] = pack(cn, "中国10Y国债", "%", "rate", 3)
        out["UST10"] = pack(us, "美国10Y国债", "%", "rate", 3); ok += 2
    except Exception as e:
        print(f"[warn] 债券失败: {e}", file=sys.stderr)
    if ok == 0:
        sys.exit("全部数据源失败，保留旧数据")
    series = {k: out.get(k) or old.get(k) for k in ORDER if out.get(k) or old.get(k)}
    p.write_text(json.dumps(series, ensure_ascii=False), "utf-8")
    return series


def build():
    series = json.loads((ROOT / "series.json").read_text("utf-8"))
    content = json.loads((ROOT / "content.json").read_text("utf-8"))
    bj = dt.datetime.utcnow() + dt.timedelta(hours=8)
    content["meta"]["updated"] = bj.strftime("%Y-%m-%d %H:%M (北京时间)")
    data = dict(content, series=series)
    (ROOT / "data.js").write_text("window.DATA=" + json.dumps(data, ensure_ascii=False) + ";", "utf-8")
    asof = max(s["dates"][-1] for s in series.values())
    (ROOT / "archive" / f"{asof}.json").write_text(json.dumps(content, ensure_ascii=False, indent=1), "utf-8")


if __name__ == "__main__":
    fetch(); build()
