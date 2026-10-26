"""Section 5: do digital skills go with AI adoption? (ICT specialists share, Eurostat isoc_sks_itspt)."""

from __future__ import annotations

from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"
SKILLS = PROCESSED / "skills_vs_adoption.csv"
LEVEL = PROCESSED / "productivity_level.csv"

EU = "EU-27 average"
EU_COLOUR = "#E69F00"
SELECTED_COLOUR = "#0072B2"
ABOVE_COLOUR = "#009E73"
BELOW_COLOUR = "#CC79A7"
OTHER_COLOUR = "#666666"
DEFINITION_CHANGE_YEAR = 2025


@st.cache_data
def load_skills(data_version: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """`data_version` (latest file modification time) makes the cache refresh when the data changes."""
    skills = pd.read_csv(SKILLS, keep_default_na=False, na_values=[""])
    level = pd.read_csv(LEVEL, keep_default_na=False, na_values=[""])
    return skills, level


def show(chart: alt.TopLevelMixin, plot_height: int, extra: int) -> None:
    st.altair_chart(
        chart.properties(height=plot_height, padding={"top": 16, "left": 5, "right": 10, "bottom": 5}),
        width="stretch",
        height=plot_height + extra,
    )


def partial_r(df: pd.DataFrame, x: str, y: str, control: str) -> float:
    """Correlation of x and y after removing the linear effect of `control` from both."""
    z = np.column_stack([np.ones(len(df)), df[control]])

    def residuals(col: str) -> np.ndarray:
        v = df[col].to_numpy()
        return v - z @ np.linalg.lstsq(z, v, rcond=None)[0]

    return float(np.corrcoef(residuals(x), residuals(y))[0, 1])


def render_skills(selected: list[str]) -> None:
    st.header("5. Do digital skills go with AI adoption?")
    skills, level = load_skills(max(SKILLS.stat().st_mtime, LEVEL.stat().st_mtime))

    countries = sorted(skills.loc[~skills["is_aggregate"], "country"].unique())
    default = next((c for c in selected if c in countries), countries[0])
    c1, c2 = st.columns(2)
    year = c1.selectbox("Year", sorted(skills["year"].unique(), reverse=True), index=1, key="skills_year",
                        help="From 2025 the AI measure also counts tools that generate pictures, video or sound.")
    country = c2.selectbox("Highlight a country", countries, index=countries.index(default), key="skills_country")

    df = skills[skills["year"] == year].copy()
    pts = df[~df["is_aggregate"]]
    eu = df[df["is_aggregate"]]
    if pts.empty or eu.empty:
        st.info(f"No ICT specialist and AI adoption data for {year}. Try another year.")
        return

    r = pts["ict_specialists_pct_emp"].corr(pts["ai_adoption_pct"])
    df["group"] = "Other country"
    df.loc[df["country"] == country, "group"] = "Highlighted country"
    df.loc[df["is_aggregate"], "group"] = EU
    df["label"] = df["geo"].where(~df["is_aggregate"], "EU")
    groups = ["Highlighted country", EU, "Other country"]
    colour = alt.Color("group:N", scale=alt.Scale(domain=groups, range=[SELECTED_COLOUR, EU_COLOUR, OTHER_COLOUR]),
                       legend=alt.Legend(title="Point colour", orient="bottom", labelLimit=200))
    x = alt.X("ict_specialists_pct_emp:Q", title=f"ICT specialists, {year} (% of total employment)")
    y = alt.Y("ai_adoption_pct:Q", title=f"Enterprises using AI, {year} (% of enterprises, 10+ employees)")
    dots = alt.Chart(df).mark_circle(size=90, opacity=0.9).encode(x=x, y=y, color=colour)
    names = alt.Chart(df).mark_text(dx=8, align="left", fontSize=11).encode(x=x, y=y, text="label:N", color=colour)
    trend = (alt.Chart(pts).transform_regression("ict_specialists_pct_emp", "ai_adoption_pct")
             .mark_line(strokeDash=[6, 4], color="#444444")
             .encode(x="ict_specialists_pct_emp:Q", y="ai_adoption_pct:Q"))
    if r >= 0.3:
        headline = "Countries with more ICT specialists tend to have more firms using AI"
    elif r <= -0.3:
        headline = "Countries with more ICT specialists tend to have fewer firms using AI"
    else:
        headline = "ICT specialist share shows no clear link to AI adoption"
    show((trend + dots + names).properties(
        title=alt.Title(headline, subtitle=f"Correlation r = {r:.2f} across {len(pts)} countries, {year}"),
    ), plot_height=360, extra=180)
    st.caption(
        "Each point is one country, labelled with its Eurostat code. x = employed ICT specialists as a % of total "
        "employment; y = % of enterprises (10+ employees) using at least one AI technology. Dashed line = "
        f"least-squares trend across {len(pts)} countries (EU-27 average excluded)."
        + (" The 2025 AI measure counts one more technology than earlier years." if year == DEFINITION_CHANGE_YEAR
           else "")
    )

    eu_ict = float(eu["ict_specialists_pct_emp"].iloc[0])
    eu_ai = float(eu["ai_adoption_pct"].iloc[0])
    dev = pts.assign(gap_pp=(pts["ict_specialists_pct_emp"] - eu_ict).round(2))
    dev["side"] = np.where(dev["gap_pp"] >= 0, "Above EU-27 average", "Below EU-27 average")
    dev.loc[dev["country"] == country, "side"] = "Highlighted country"
    order = dev.sort_values("gap_pp", ascending=False)["country"].tolist()

    left, right = st.columns([3, 2])
    with left:
        yb = alt.Y("country:N", sort=order, title=None, axis=alt.Axis(labelOverlap=False, labelLimit=200))
        span = dev["gap_pp"].abs().max() * 1.2
        bars = alt.Chart(dev).mark_bar().encode(
            x=alt.X("gap_pp:Q", title=f"Difference from EU-27 average ({eu_ict:.1f}%), percentage points",
                    scale=alt.Scale(domain=[-span, span])),
            y=yb,
            color=alt.Color("side:N", scale=alt.Scale(
                domain=["Above EU-27 average", "Below EU-27 average", "Highlighted country"],
                range=[ABOVE_COLOUR, BELOW_COLOUR, SELECTED_COLOUR]),
                legend=alt.Legend(title="Bar colour", orient="bottom", columns=2, labelLimit=200)),
        )
        label = dict(x="gap_pp:Q", y=yb, text=alt.Text("gap_pp:Q", format="+.1f"))
        labels = (
            alt.Chart(dev[dev["gap_pp"] >= 0]).mark_text(fontSize=11, align="left", dx=3).encode(**label)
            + alt.Chart(dev[dev["gap_pp"] < 0]).mark_text(fontSize=11, align="right", dx=-3).encode(**label)
        )
        zero = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="#444444").encode(x="x:Q")
        show((bars + zero + labels).properties(
            title=alt.Title(f"ICT specialist share compared with the EU-27, {year}",
                            subtitle="% of total employment, minus the EU-27 average"),
        ), plot_height=18 * len(dev), extra=170)
        st.caption("Bars to the right: a larger share of ICT specialists than the EU-27 average; to the left: smaller.")

    with right:
        own = pts[pts["country"] == country]
        if own.empty:
            st.info(f"No ICT specialist data for {country} in {year}.")
        else:
            row = own.iloc[0]
            st.markdown(
                f"**{country}, {year}**\n\n"
                f"- ICT specialists: **{row['ict_specialists_pct_emp']:.1f}%** of employment "
                f"(EU-27: {eu_ict:.1f}%)\n"
                f"- Enterprises using AI: **{row['ai_adoption_pct']:.1f}%** (EU-27: {eu_ai:.1f}%)"
            )
        merged = pts.merge(level[["geo", "year", "productivity_level_pct_eu"]], on=["geo", "year"], how="inner")
        if len(merged) >= 5:
            pr = partial_r(merged, "ict_specialists_pct_emp", "ai_adoption_pct", "productivity_level_pct_eu")
            st.markdown(
                f"**Is it just richer countries?** Comparing countries at a similar productivity level, the link is "
                f"**r = {pr:.2f}** (partial correlation over {len(merged)} countries with productivity data), "
                f"compared with **r = {r:.2f}** without that adjustment."
            )
        st.markdown(
            "**What this means for Elena:** section 4 shows lack of expertise is the most cited reason for not "
            "using AI, and here countries with more ICT specialists have more firms using AI. A skills policy "
            "may target the barrier more directly than a cost subsidy. This data cannot show that training more "
            "specialists would *cause* higher adoption."
        )

    with st.expander("Values behind the charts in this section"):
        table = dev.sort_values("gap_pp", ascending=False)[
            ["country", "geo", "ict_specialists_pct_emp", "gap_pp", "ai_adoption_pct", "ict_flag"]
        ].rename(columns={
            "country": "Country",
            "geo": "Code",
            "ict_specialists_pct_emp": f"ICT specialists {year} (% of employment)",
            "gap_pp": "Difference from EU-27 (pp)",
            "ai_adoption_pct": f"Enterprises using AI {year} (%)",
            "ict_flag": "ICT flag (b = break, e = estimated, d = definition differs)",
        })
        st.dataframe(table.fillna(""), hide_index=True, width="stretch")
