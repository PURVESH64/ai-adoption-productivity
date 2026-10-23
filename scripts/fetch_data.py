"""Download the Eurostat source samples into data/raw/.

Run from the repository root:
    python scripts/fetch_data.py

Each sample is an exact, unmodified SDMX-CSV extract from the Eurostat API,
filtered at the API to the series the app uses. The URL and download time of
every file are recorded in data/raw/fetch_log.csv.
"""

from __future__ import annotations

import csv
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"

API = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data"

# (sample name, Eurostat dataset code, API URL)
SOURCES = [
    # Key order: freq.size_emp.nace_r2.indic_is.unit.geo (empty geo = all countries)
    (
        "isoc_eb_ai",
        "isoc_eb_ai",
        f"{API}/isoc_eb_ai/A.10-49+50-249+GE250+GE10.C10-S951_X_K.E_AI_TANY.PC_ENT.?format=SDMX-CSV",
    ),
    # Key order: freq.unit.na_item.geo
    (
        "nama_10_lp_ulc",
        "nama_10_lp_ulc",
        f"{API}/nama_10_lp_ulc/A.I15.RLPR_HW.?format=SDMX-CSV&startPeriod=2015",
    ),
    (
        "nama_10_lp_ulc_level",
        "nama_10_lp_ulc",
        f"{API}/nama_10_lp_ulc/A.PC_EU27_2020_MPPS_CP.NLPR_HW.?format=SDMX-CSV&startPeriod=2015",
    ),
]


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    log_rows = []
    for name, code, url in SOURCES:
        out = RAW_DIR / f"{name}_sample.csv"
        print(f"Downloading {name} ...")
        with urllib.request.urlopen(url, timeout=120) as resp:
            out.write_bytes(resp.read())
        fetched = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        log_rows.append({"sample": name, "dataset_code": code, "file": out.name, "url": url,
                         "fetched_utc": fetched})
        print(f"  saved {out.relative_to(ROOT)}")

    with open(RAW_DIR / "fetch_log.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sample", "dataset_code", "file", "url", "fetched_utc"])
        writer.writeheader()
        writer.writerows(log_rows)


if __name__ == "__main__":
    main()
