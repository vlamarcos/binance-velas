"""Histórico longo (só data-api.binance.vision): 1h ~6 meses (paginado), 1d (1000) e 1w (500).
Corre só uma vez por dia (00h UTC) ou se faltar o ficheiro, para não encher o repositório."""
import json, os, time, urllib.request, datetime as dt
B = "https://data-api.binance.vision/api/v3/klines?symbol={}&interval={}&limit=1000{}"
def get(s, i, extra=""):
    for k in range(3):
        try:
            return json.load(urllib.request.urlopen(B.format(s, i, extra), timeout=30))
        except Exception:
            time.sleep(10)
    raise SystemExit(f"falhou {s} {i}")
h = dt.datetime.now(dt.timezone.utc).hour
for s in ("ETHUSDT", "BTCUSDT"):
    f1 = f"data/hist/{s}_1h_6m.json"
    if h != 0 and os.path.exists(f1):
        continue
    os.makedirs("data/hist", exist_ok=True)
    out, end = [], ""
    for _ in range(5):                       # 5 x 1000 velas 1h ≈ 6,8 meses
        d = get(s, "1h", end)
        out = d + out
        end = f"&endTime={d[0][0] - 1}"
    out = sorted({r[0]: r for r in out}.values())
    for a, b in zip(out, out[1:]):
        assert b[0] - a[0] == 3600000, "buraco 1h"
    json.dump(out, open(f1, "w"))
    json.dump(get(s, "1d"), open(f"data/hist/{s}_1d.json", "w"))
    json.dump(get(s, "1w", "").__getitem__(slice(-500, None)), open(f"data/hist/{s}_1w.json", "w"))
    print(s, "histórico", len(out))
