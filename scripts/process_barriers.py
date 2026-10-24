"""Build data/processed/ai_barriers.csv from the raw Eurostat barriers sample.

Called by scripts/process.py; transform steps are documented in docs/data_dictionary.md.
"""

from __future__ import annotations

import pandas as pd

BARRIER_LABELS = {
    "E_AI_BLE": "Lack of relevant expertise",
    "E_AI_BLEG": "Unclear legal consequences",
    "E_AI_BCDP": "Data protection and privacy concerns",
    "E_AI_BDDT": "Data availability or quality",
    "E_AI_BINC": "Incompatible with existing systems",
    "E_AI_BCST": "Costs seem too high",
    "E_AI_BEC": "Ethical considerations",
    "E_AI_BNU": "AI not useful for the enterprise",
}


def build_barriers(tidy_raw: pd.DataFrame, size_labels: dict[str, str]) -> pd.DataFrame:
    """`tidy_raw` has already been through steps T1-T3 in process.py."""
    df = tidy_raw.assign(
        size_class_code=tidy_raw["size_emp"],
        size_class=tidy_raw["size_emp"].map(size_labels),
        barrier_code=tidy_raw["indic_is"],
        barrier=tidy_raw["indic_is"].map(BARRIER_LABELS),
        pct_of_considering=tidy_raw["OBS_VALUE"].round(2),
    )
    cols = ["geo", "country", "is_aggregate", "year", "size_class_code", "size_class",
            "barrier_code", "barrier", "pct_of_considering", "obs_flag"]
    return df[cols].sort_values(["geo", "year", "size_class_code", "barrier_code"]).reset_index(drop=True)
