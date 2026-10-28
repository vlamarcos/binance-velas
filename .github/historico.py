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

# 28 out 2026 (pedido do Marcos: visão de todos os timeframes): histórico 15m ~6 meses, compacto (t,o,h,l,c,v).
# Só se faltar o ficheiro: depois disso o histórico 15m cresce localmente com os ficheiros de 1000 velas.
for s in ("ETHUSDT", "BTCUSDT"):
    f15 = f"data/hist/{s}_15m_6m.json"
    if os.path.exists(f15):
        continue
    os.makedirs("data/hist", exist_ok=True)
    out, end = [], ""
    for _ in range(18):                      # 18 x 1000 velas 15m ≈ 6,25 meses
        d = get(s, "15m", end)
        out = d + out
        end = f"&endTime={d[0][0] - 1}"
    out = sorted({r[0]: r for r in out}.values())
    for a, b in zip(out, out[1:]):
        assert b[0] - a[0] == 900000, "buraco 15m"
    json.dump([r[:6] for r in out], open(f15, "w"), separators=(",", ":"))
    print(s, "histórico 15m", len(out))

# 28 out 2026 (pedido do Marcos: pesquisa de padrões com muitos dados): histórico longo, uma vez (só se faltar o ficheiro).
# 1h desde 2019-01-01 e 15m dos últimos ~2 anos, paginado para a frente com startTime. Compacto (t,o,h,l,c,v).
def longo(s, i, ms, desde, f):
    if os.path.exists(f):
        return
    out, t = [], desde
    agora = int(time.time() * 1000)
    while t < agora - ms:
        d = get(s, i, f"&startTime={t}")
        if not d:
            break
        out += d
        t = d[-1][0] + ms
    out = sorted({r[0]: r for r in out}.values())[:-1]          # tira a vela em formação
    buracos = sum(1 for a, b in zip(out, out[1:]) if b[0] - a[0] != ms)   # a Binance tem paragens antigas: regista, não falha
    print(s, i, "buracos", buracos)
    json.dump([r[:6] for r in out], open(f, "w"), separators=(",", ":"))
    print(s, i, "longo", len(out))
for s in ("ETHUSDT", "BTCUSDT"):
  try:                                       # nunca deixa o histórico longo partir o robô das velas
    longo(s, "1h", 3600000, 1546300800000, f"data/hist/{s}_1h_longo.json")
    longo(s, "15m", 900000, int(time.time() * 1000) - 730 * 86400000, f"data/hist/{s}_15m_2a.json")
  except BaseException as e:
    print("histórico longo falhou", s, e)
