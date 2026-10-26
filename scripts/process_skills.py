"""Build data/processed/skills_vs_adoption.csv: ICT specialists share vs business AI adoption.

Called by scripts/process.py; transform steps are documented in docs/data_dictionary.md.
"""

from __future__ import annotations

import pandas as pd


def build_skills(tidy_raw: pd.DataFrame, ai: pd.DataFrame) -> pd.DataFrame:
    """`tidy_raw` has been through steps T1-T3 in process.py; `ai` is the processed ai_adoption table.

    Keeps country-years present in both sources, using AI adoption for all firms (10+ employees).
    """
    skills = tidy_raw.assign(ict_specialists_pct_emp=tidy_raw["OBS_VALUE"].round(2))[
        ["geo", "country", "is_aggregate", "year", "ict_specialists_pct_emp", "obs_flag"]
    ].rename(columns={"obs_flag": "ict_flag"})
    adoption = ai[ai["size_class_code"] == "GE10"][["geo", "year", "ai_adoption_pct", "obs_flag"]].rename(
        columns={"obs_flag": "ai_flag"})
    df = skills.merge(adoption, on=["geo", "year"], how="inner")
    cols = ["geo", "country", "is_aggregate", "year", "ict_specialists_pct_emp", "ai_adoption_pct",
            "ict_flag", "ai_flag"]
    return df[cols].sort_values(["year", "geo"]).reset_index(drop=True)
