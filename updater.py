#!/usr/bin/env python3
"""Geriye dönük uyumluluk sarmalayıcısı: ``python updater.py``.

Bu dosya eskiden sabit (uydurma) maç listesi ve kanal listesi yazıyordu.
Artık tek gerçek boru hattını (``python fixbet.py run``) çalıştırır:

  * güncel site adresini bulur,
  * maç listesini kaynaktan çeker ve gerçek saatlere göre kategorize eder,
  * index.html + output/*.json dosyalarını gerçek veriyle üretir.

Ek olarak eski ``data/streams.json`` sözleşmesini (kanal + günün maçları)
gerçek veriden yeniden yazar; böylece dışarıdan bu dosyayı okuyan bir şey
varsa çalışmaya devam eder.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from fixbet import config  # noqa: E402
from fixbet.main import main  # noqa: E402


def write_streams_json() -> Path | None:
    """output/ altındaki gerçek veriden data/streams.json üretir."""
    today_path = config.OUTPUT_DIR / "today_matches.json"
    channels_path = config.OUTPUT_DIR / "channels.json"
    if not today_path.exists() or not channels_path.exists():
        return None

    today = json.loads(today_path.read_text(encoding="utf-8"))
    channels_blob = json.loads(channels_path.read_text(encoding="utf-8")).get("channels", {})
    channel_list = channels_blob.get("channels", [])
    site_info = today.get("site", {})

    payload = {
        "activeDomain": site_info.get("base_domain", ""),
        "currentAddress": site_info.get("current_address", ""),
        "lastChecked": site_info.get("last_checked", ""),
        "date": today.get("date", ""),
        "channels": channel_list,
        "matches": today.get("matches", []),
    }
    out = ROOT / "data" / "streams.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[updater] data/streams.json güncellendi ({len(channel_list)} kanal, "
          f"{len(payload['matches'])} maç)")
    return out


if __name__ == "__main__":
    code = main(["run"])
    try:
        write_streams_json()
    except Exception as exc:  # noqa: BLE001 - sarmalayıcı patlamasın
        print(f"[updater] streams.json yazılamadı: {exc}")
    raise SystemExit(code)
