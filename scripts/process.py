"""Transform the raw Eurostat samples in data/raw/ into the processed files the app reads.

Run from the repository root:
    python scripts/process.py

Deterministic: the same raw samples always produce identical processed files.
Each transform step is documented in docs/data_dictionary.md.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from process_barriers import build_barriers

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

# Comparison periods. Eurostat added an eighth AI technology (generating pictures, video or
# sound) to the "at least one AI technology" measure in 2025, so 2024 is kept as an end year
# that uses the same seven-technology definition as the base years.
BASE_YEARS = (2021, 2023)
END_YEARS = (2024, 2025)

COUNTRY_NAMES = {
    "EU27_2020": "EU-27 average",
    "AL": "Albania", "AT": "Austria", "BA": "Bosnia and Herzegovina", "BE": "Belgium",
    "BG": "Bulgaria", "CH": "Switzerland", "CY": "Cyprus", "CZ": "Czechia",
    "DE": "Germany", "DK": "Denmark", "EE": "Estonia", "EL": "Greece", "ES": "Spain",
    "FI": "Finland", "FR": "France", "HR": "Croatia", "HU": "Hungary", "IE": "Ireland",
    "IS": "Iceland", "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia",
    "ME": "Montenegro", "MK": "North Macedonia", "MT": "Malta", "NL": "Netherlands",
    "NO": "Norway", "PL": "Poland", "PT": "Portugal", "RO": "Romania", "RS": "Serbia",
    "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia", "TR": "Türkiye",
}

SIZE_LABELS = {
    "GE10": "All firms (10+ employees)",
    "10-49": "Small (10-49 employees)",
    "50-249": "Medium (50-249 employees)",
    "GE250": "Large (250+ employees)",
}

SAMPLE_TITLES = {
    "isoc_eb_ai": "Artificial intelligence by size class of enterprise",
    "nama_10_lp_ulc": "Labour productivity and unit labour costs: real productivity per hour (index)",
    "nama_10_lp_ulc_level": "Labour productivity and unit labour costs: productivity per hour (% of EU-27, PPS)",
    "isoc_eb_ai_barriers": "Artificial intelligence by size class of enterprise: reasons for not using AI",
}


def read_raw(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW / f"{name}_sample.csv", dtype={"OBS_FLAG": "string"})


def last_update(df: pd.DataFrame) -> str:
    """Eurostat's 'LAST UPDATE' column (dd/mm/yy hh:mm:ss) as an ISO date."""
    raw = df["LAST UPDATE"].iloc[0]
    return datetime.strptime(raw, "%d/%m/%y %H:%M:%S").strftime("%Y-%m-%d")


def tidy(raw: pd.DataFrame, label: str) -> pd.DataFrame:
    """Steps T1-T3: drop empty values, keep named geos, add country name, year and flag."""
    df = raw[raw["OBS_VALUE"].notna()]
    dropped = sorted(set(df["geo"]) - set(COUNTRY_NAMES))
    if dropped:
        print(f"  {label}: dropped geo codes {dropped}")
    df = df[df["geo"].isin(COUNTRY_NAMES)].copy()
    df["country"] = df["geo"].map(COUNTRY_NAMES)
    df["is_aggregate"] = df["geo"].eq("EU27_2020")
    df["year"] = df["TIME_PERIOD"].astype(int)
    df["obs_flag"] = df["OBS_FLAG"].fillna("")
    return df


def build_ai_adoption(raw: pd.DataFrame) -> pd.DataFrame:
    df = tidy(raw, "isoc_eb_ai")
    df = df.assign(
        size_class_code=df["size_emp"],
        size_class=df["size_emp"].map(SIZE_LABELS),
        ai_adoption_pct=df["OBS_VALUE"].round(2),
    )
    cols = ["geo", "country", "is_aggregate", "year", "size_class_code", "size_class",
            "ai_adoption_pct", "obs_flag"]
    return df[cols].sort_values(["geo", "size_class_code", "year"]).reset_index(drop=True)


def build_productivity(raw: pd.DataFrame) -> pd.DataFrame:
    df = tidy(raw, "nama_10_lp_ulc")
    df["productivity_index_2015"] = df["OBS_VALUE"].round(2)
    cols = ["geo", "country", "is_aggregate", "year", "productivity_index_2015", "obs_flag"]
    return df[cols].sort_values(["geo", "year"]).reset_index(drop=True)


def build_productivity_level(raw: pd.DataFrame) -> pd.DataFrame:
    df = tidy(raw, "nama_10_lp_ulc_level")
    df["productivity_level_pct_eu"] = df["OBS_VALUE"].round(2)
    cols = ["geo", "country", "is_aggregate", "year", "productivity_level_pct_eu", "obs_flag"]
    return df[cols].sort_values(["geo", "year"]).reset_index(drop=True)


def build_comparison(ai: pd.DataFrame, lp: pd.DataFrame, level: pd.DataFrame) -> pd.DataFrame:
    """One row per (country, base year, end year).

    Only countries with AI adoption and productivity in both the base and end year are kept.
    """
    all_firms = ai[ai["size_class_code"] == "GE10"]
    a = all_firms.pivot(index="geo", columns="year", values="ai_adoption_pct")
    a_flag = all_firms.pivot(index="geo", columns="year", values="obs_flag")
    p = lp.pivot(index="geo", columns="year", values="productivity_index_2015")
    p_flag = lp.pivot(index="geo", columns="year", values="obs_flag")
    lvl = level.pivot(index="geo", columns="year", values="productivity_level_pct_eu")

    frames = []
    for base in BASE_YEARS:
        for end in END_YEARS:
            df = pd.DataFrame({
                "ai_pct_base": a[base],
                "ai_pct_end": a[end],
                "lp_index_base": p[base],
                "lp_index_end": p[end],
            }).dropna()
            df["ai_change_pp"] = (df["ai_pct_end"] - df["ai_pct_base"]).round(2)
            df["lp_growth_pct"] = ((df["lp_index_end"] / df["lp_index_base"] - 1) * 100).round(2)
            df["lp_level_base_pct_eu"] = lvl[base].reindex(df.index)
            df["lp_end_flag"] = p_flag[end].reindex(df.index).fillna("")
            survey_years = [y for y in a_flag.columns if base <= y <= end]
            df["ai_series_break"] = a_flag.loc[df.index, survey_years].eq("b").any(axis=1)
            df.insert(0, "end_year", end)
            df.insert(0, "base_year", base)
            frames.append(df)

    df = pd.concat(frames).reset_index().rename(columns={"index": "geo"})
    df.insert(1, "country", df["geo"].map(COUNTRY_NAMES))
    df.insert(2, "is_aggregate", df["geo"].eq("EU27_2020"))
    return df.sort_values(["base_year", "end_year", "geo"]).reset_index(drop=True)


def build_refresh_info(updated: dict[str, str]) -> pd.DataFrame:
    log = pd.read_csv(RAW / "fetch_log.csv")
    log["title"] = log["sample"].map(SAMPLE_TITLES)
    log["source_last_update"] = log["sample"].map(updated)
    log["fetched_date"] = log["fetched_utc"].str[:10]
    return log[["sample", "dataset_code", "title", "source_last_update", "fetched_date", "url"]]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    raws = {name: read_raw(name) for name in SAMPLE_TITLES}
    ai = build_ai_adoption(raws["isoc_eb_ai"])
    lp = build_productivity(raws["nama_10_lp_ulc"])
    level = build_productivity_level(raws["nama_10_lp_ulc_level"])
    comp = build_comparison(ai, lp, level)
    barriers = build_barriers(tidy(raws["isoc_eb_ai_barriers"], "isoc_eb_ai_barriers"), SIZE_LABELS)
    refresh = build_refresh_info({name: last_update(df) for name, df in raws.items()})

    outputs = {
        "ai_adoption.csv": ai,
        "productivity.csv": lp,
        "productivity_level.csv": level,
        "adoption_vs_productivity.csv": comp,
        "ai_barriers.csv": barriers,
        "refresh_info.csv": refresh,
    }
    for name, df in outputs.items():
        df.to_csv(OUT / name, index=False)
        print(f"  wrote data/processed/{name} ({len(df)} rows)")


if __name__ == "__main__":
    main()
