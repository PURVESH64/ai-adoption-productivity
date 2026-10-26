"""AI adoption vs productivity in Europe: a Streamlit data narrative.

Reads only the processed files in data/processed/ (built by scripts/process.py).
"""

from __future__ import annotations

from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from views.barriers import render_barriers
from views.skills import render_skills

DATA = Path(__file__).parent / "data" / "processed"

QUESTION = (
    "Has the rise in business AI adoption across Europe translated into "
    "faster labour productivity growth?"
)

# Okabe-Ito palette: distinguishable under the common colour vision deficiencies.
EU_COLOUR = "#E69F00"
SELECTED_COLOUR = "#0072B2"
OTHER_COLOUR = "#BBBBBB"
COUNTRY_PALETTE = ["#0072B2", "#009E73", "#CC79A7"]
SIZE_ORDER = ["Small (10-49 employees)", "Medium (50-249 employees)", "Large (250+ employees)"]
EU = "EU-27 average"
GROUPS = ["Selected country", EU, "Other country"]

# Eurostat added an eighth AI technology (generating pictures, video or sound) in 2025.
DEFINITION_CHANGE_YEAR = 2025
DEFAULT_PERIOD = (2021, 2024)

st.set_page_config(page_title="AI adoption vs productivity in Europe", layout="wide")


@st.cache_data
def load(data_version: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """`data_version` (latest file modification time) makes the cache refresh when the data changes."""
    ai = pd.read_csv(DATA / "ai_adoption.csv", keep_default_na=False, na_values=[""])
    comp = pd.read_csv(DATA / "adoption_vs_productivity.csv", keep_default_na=False, na_values=[""])
    refresh = pd.read_csv(DATA / "refresh_info.csv")
    return ai, comp, refresh


def correlation(df: pd.DataFrame, x: str = "ai_change_pp", y: str = "lp_growth_pct") -> float:
    countries = df[~df["is_aggregate"]]
    return countries[x].corr(countries[y])


def partial_correlation(df: pd.DataFrame, control: str = "lp_level_base_pct_eu") -> float:
    """Correlation of AI change and productivity growth after removing the linear effect of `control`."""
    countries = df[~df["is_aggregate"]]
    z = np.column_stack([np.ones(len(countries)), countries[control]])

    def residuals(col: str) -> np.ndarray:
        y = countries[col].to_numpy()
        return y - z @ np.linalg.lstsq(z, y, rcond=None)[0]

    return float(np.corrcoef(residuals("ai_change_pp"), residuals("lp_growth_pct"))[0, 1])


def describe_link(r: float, positive: str, negative: str, none: str) -> str:
    if r >= 0.3:
        return positive
    if r <= -0.3:
        return negative
    return none


def show(chart: alt.TopLevelMixin, plot_height: int, extra: int = 140) -> None:
    """Render full-width. The frame is taller than the plot so the title, axes and legend fit inside it."""
    st.altair_chart(
        chart.properties(height=plot_height, padding={"top": 16, "left": 5, "right": 10, "bottom": 5}),
        width="stretch",
        height=plot_height + extra,
    )


def group_column(df: pd.DataFrame, selected: list[str]) -> pd.Series:
    group = pd.Series("Other country", index=df.index)
    group[df["country"].isin(selected)] = "Selected country"
    group[df["is_aggregate"]] = EU
    return group


def period_label(period: tuple[int, int]) -> str:
    base, end = period
    note = " (wider AI definition in 2025)" if end == DEFINITION_CHANGE_YEAR else " (same AI definition)"
    return f"{base} to {end}{note}"


ai, comp, refresh = load(max(f.stat().st_mtime for f in DATA.glob("*.csv")))
periods = {key: g for key, g in comp.groupby(["base_year", "end_year"])}
r_by_period = {key: correlation(g) for key, g in periods.items()}
default = periods[DEFAULT_PERIOD]
eu_default = default[default["is_aggregate"]].iloc[0]
eu_2025 = ai[ai["is_aggregate"] & (ai["size_class_code"] == "GE10") & (ai["year"] == 2025)].iloc[0]

# ---------------------------------------------------------------- sidebar filters
with st.sidebar:
    st.header("Filters")
    year = st.selectbox("Survey year (section 1)", sorted(ai["year"].unique(), reverse=True))
    size = st.selectbox(
        "Firm size (sections 1 and 2)",
        ["All firms (10+ employees)", *SIZE_ORDER],
        help="Eurostat surveys enterprises with 10 or more employees only.",
    )
    country_names = sorted(ai.loc[~ai["is_aggregate"], "country"].unique())
    selected = st.multiselect(
        "Compare countries (up to 3)",
        country_names,
        default=["Denmark", "Germany", "Poland"],
        max_selections=3,
    )
    period = st.selectbox(
        "Comparison period (section 3)",
        list(periods),
        index=list(periods).index(DEFAULT_PERIOD),
        format_func=period_label,
        help="Periods ending in 2024 use the same seven-technology AI definition throughout. "
             "In 2025 Eurostat added an eighth technology (generating pictures, video or sound).",
    )
    st.caption("The EU-27 average is always shown for reference.")

# ---------------------------------------------------------------- opening screen
st.title("Is AI making Europe more productive?")
st.markdown(f"**Question:** {QUESTION}")

base0, end0 = DEFAULT_PERIOD
n_countries = int((~default["is_aggregate"]).sum())
st.markdown(
    f"Across the EU-27, the share of enterprises (10+ employees) using AI rose from "
    f"**{eu_default['ai_pct_base']:.1f}% in {base0} to {eu_default['ai_pct_end']:.1f}% in {end0}** on a "
    f"like-for-like basis, and reached **{eu_2025['ai_adoption_pct']:.1f}% in 2025** after Eurostat added "
    f"tools that generate pictures, video or sound. Over {base0}-{end0}, EU-27 real labour productivity "
    f"per hour worked changed by **{eu_default['lp_growth_pct']:+.1f}%**."
)

m1, m2, m3 = st.columns(3)
m1.metric(f"EU-27 firms using AI, {end0}", f"{eu_default['ai_pct_end']:.1f}%",
          f"{eu_default['ai_change_pp']:+.1f} pp since {base0}")
m2.metric(f"EU-27 productivity change, {base0}-{str(end0)[2:]}", f"{eu_default['lp_growth_pct']:+.1f}%")
m3.metric(f"AI rise vs productivity, {base0}-{str(end0)[2:]}", f"r = {r_by_period[DEFAULT_PERIOD]:.2f}")
st.caption(f"Productivity = real labour productivity per hour worked. r = correlation across {n_countries} "
           "European countries between the rise in AI use and productivity growth (section 3).")

# ---------------------------------------------------------------- section 1
st.header("1. Where does each country stand?")
col_rank, col_size = st.columns([1, 1])

with col_rank:
    rank = ai[(ai["year"] == year) & (ai["size_class"] == size)].copy()
    if rank.empty:
        st.info(f"Eurostat has no AI adoption data for {size.lower()} in {year}. Try another year.")
    else:
        rank["group"] = group_column(rank, selected)
        order = rank.sort_values("ai_adoption_pct", ascending=False)["country"].tolist()
        y = alt.Y("country:N", sort=order, title=None,
                  axis=alt.Axis(labelOverlap=False, labelLimit=200))
        bars = alt.Chart(rank).mark_bar().encode(
            x=alt.X("ai_adoption_pct:Q", title="Enterprises using AI (% of enterprises)",
                    scale=alt.Scale(domain=[0, rank["ai_adoption_pct"].max() * 1.12], nice=False)),
            y=y,
            color=alt.Color("group:N", scale=alt.Scale(domain=GROUPS,
                            range=[SELECTED_COLOUR, EU_COLOUR, OTHER_COLOUR]),
                            legend=alt.Legend(title="Bar colour", orient="bottom", columns=2,
                                              labelLimit=200)),
        )
        labels = alt.Chart(rank).mark_text(align="left", dx=3, fontSize=11).encode(
            x="ai_adoption_pct:Q", y=y, text=alt.Text("ai_adoption_pct:Q", format=".1f"),
        )
        show((bars + labels).properties(
            title=alt.Title(f"AI use by country, {year}", subtitle=size),
        ), plot_height=20 * len(rank))
        st.caption("Countries ranked by the % of enterprises using at least one AI technology. "
                   "Changes with the survey-year and firm-size filters.")

with col_size:
    size_df = ai[(ai["year"] == year) & (ai["size_class"].isin(SIZE_ORDER))
                 & (ai["country"].isin([*selected, EU]))]
    if not selected:
        st.info("Select at least one country in the sidebar to compare firm sizes.")
    elif size_df.empty:
        st.info(f"No firm-size data for the selected countries in {year}.")
    else:
        domain = [*selected, EU]
        rng = [*COUNTRY_PALETTE[: len(selected)], EU_COLOUR]
        x = alt.X("size_class:N", sort=SIZE_ORDER, title="Firm size (employees)",
                  axis=alt.Axis(labelAngle=0, labelExpr="split(datum.label, ' (')[0]"))
        base = alt.Chart(size_df).encode(x=x, xOffset=alt.XOffset("country:N", sort=domain))
        grouped = base.mark_bar().encode(
            y=alt.Y("ai_adoption_pct:Q", title="Enterprises using AI (% of enterprises)"),
            color=alt.Color("country:N", scale=alt.Scale(domain=domain, range=rng),
                            legend=alt.Legend(title="Country", orient="bottom", labelLimit=200)),
        )
        text = base.mark_text(dy=-6, fontSize=11).encode(
            y="ai_adoption_pct:Q", text=alt.Text("ai_adoption_pct:Q", format=".1f"),
        )
        show((grouped + text).properties(
            title=alt.Title(f"AI use by firm size, {year}", subtitle="Selected countries and EU-27"),
        ), plot_height=380)
        st.caption("In every country and year with data, large firms (250+ employees) are more likely "
                   "to use AI than small firms (10-49 employees).")

# ---------------------------------------------------------------- section 2
st.header("2. How fast is adoption growing?")
trend = ai[(ai["size_class"] == size) & (ai["country"].isin([*selected, EU]))]
if not selected:
    st.info("Select at least one country in the sidebar to see its trend against the EU-27 average.")
elif trend.empty:
    st.info("No data for this combination of countries and firm size.")
else:
    domain = [*selected, EU]
    rng = [*COUNTRY_PALETTE[: len(selected)], EU_COLOUR]
    colour = alt.Color("country:N", scale=alt.Scale(domain=domain, range=rng),
                       legend=alt.Legend(title="Country", orient="right", labelLimit=200))
    xt = alt.X("year:Q", title="Survey year (no AI survey was run in 2022)",
               scale=alt.Scale(domain=[2020.7, 2025.3]),
               axis=alt.Axis(values=[2021, 2023, 2024, 2025], format="d"))
    yt = alt.Y("ai_adoption_pct:Q", title="Enterprises using AI (% of enterprises)",
               scale=alt.Scale(zero=True))
    lines = alt.Chart(trend).mark_line(point=True, strokeWidth=2.5).encode(x=xt, y=yt, color=colour)
    marker = pd.DataFrame({"year": [DEFINITION_CHANGE_YEAR - 0.5], "label": ["Wider AI definition from 2025"]})
    rule = alt.Chart(marker).mark_rule(strokeDash=[4, 4], color="#666666").encode(x="year:Q")
    rule_text = alt.Chart(marker).mark_text(align="right", dx=-4, y=8, fontSize=11, color="#444444").encode(
        x="year:Q", text="label:N")
    chart_col, table_col = st.columns([3, 2])
    with chart_col:
        show((lines + rule + rule_text).properties(
            title=alt.Title("AI adoption over time", subtitle=size),
        ), plot_height=280, extra=100)
    with table_col:
        values = (trend.pivot(index="country", columns="year", values="ai_adoption_pct")
                  .reindex(domain).dropna(how="all"))
        values.columns = [str(c) for c in values.columns]
        values.index.name = "Country"
        st.markdown("**Values plotted (% of enterprises)**")
        st.dataframe(values.style.format("{:.1f}", na_rep="n/a"), width="stretch")
    st.caption("% of enterprises using at least one AI technology in each survey year, selected countries "
               "against the EU-27 average. From 2025 the measure also counts tools that generate pictures, "
               "video or sound, so part of the 2024-2025 jump is a change of definition. Eurostat also flags "
               "series breaks for France and Sweden (2023) and the Netherlands (2025).")

# ---------------------------------------------------------------- section 3
st.header("3. Did productivity follow?")
base_year, end_year = period
pts = periods[period].copy()
r = r_by_period[period]
n_pts = int((~pts["is_aggregate"]).sum())
pts["group"] = group_column(pts, selected)
pts["label"] = pts["geo"].where(~pts["is_aggregate"], "EU")
span = f"{base_year}-{end_year}"

xs = alt.X("ai_change_pp:Q", title=f"Change in enterprises using AI, {span} (percentage points)")
ys = alt.Y("lp_growth_pct:Q", title=f"Real labour productivity growth per hour, {span} (%)")
scolour = alt.Color("group:N", scale=alt.Scale(domain=GROUPS,
                    range=[SELECTED_COLOUR, EU_COLOUR, "#666666"]),
                    legend=alt.Legend(title="Point colour", orient="bottom", labelLimit=200))
zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#999999").encode(y="y:Q")


def labelled_scatter(x: alt.X, y: alt.Y, x_field: str) -> alt.LayerChart:
    dots = alt.Chart(pts).mark_circle(size=90, opacity=0.9).encode(x=x, y=y, color=scolour)
    names = alt.Chart(pts).mark_text(dx=8, align="left", fontSize=11).encode(
        x=x, y=y, text="label:N", color=scolour)
    trendline = (
        alt.Chart(pts[~pts["is_aggregate"]])
        .transform_regression(x_field, "lp_growth_pct")
        .mark_line(strokeDash=[6, 4], color="#444444")
        .encode(x=f"{x_field}:Q", y="lp_growth_pct:Q")
    )
    return zero + trendline + dots + names


link = describe_link(r, "tended to come with faster", "tended to come with slower", "showed no clear link to")
show(labelled_scatter(xs, ys, "ai_change_pp").properties(
    title=alt.Title(
        f"Bigger rises in AI use {link} productivity growth",
        subtitle=f"Correlation r = {r:.2f} across {n_pts} countries, {span}",
    ),
), plot_height=380, extra=180)
st.caption(
    f"Each point is one country, labelled with its Eurostat code. x = change in the % of enterprises "
    f"(10+ employees) using AI between {base_year} and {end_year}; y = % change in real labour productivity "
    f"per hour worked (index 2015 = 100) over the same years. Dashed line = least-squares trend across "
    f"{n_pts} countries (EU-27 average excluded)."
)

st.subheader("Is it just catch-up?")
r_level = correlation(pts, x="lp_level_base_pct_eu")
r_partial = partial_correlation(pts)
level_link = describe_link(r_level, "tended to grow faster", "tended to grow more slowly",
                           "showed no clear difference in growth")
xl = alt.X("lp_level_base_pct_eu:Q",
           title=f"Productivity per hour worked in {base_year} (% of EU-27 average, PPS)")
show(labelled_scatter(xl, ys, "lp_level_base_pct_eu").properties(
    title=alt.Title(
        f"Countries with higher starting productivity {level_link}",
        subtitle=f"Correlation r = {r_level:.2f} across {n_pts} countries, {span}",
    ),
), plot_height=340, extra=180)
st.caption(
    f"x = nominal labour productivity per hour worked in {base_year}, in purchasing power standards, as a % "
    f"of the EU-27 average (100 = EU average); y = real productivity growth, {span} (%). "
    "Lower-productivity economies can grow faster by catching up, regardless of AI."
)
st.markdown(
    f"Holding the starting productivity level constant, the link between the rise in AI use and "
    f"productivity growth over {span} is **r = {r_partial:.2f}** (partial correlation), compared with "
    f"**r = {r:.2f}** without that adjustment. "
    + ("Catch-up growth does not turn the relationship positive."
       if r_partial < 0.3 else "After this adjustment the relationship becomes positive.")
)

with st.expander("Values behind the charts in this section"):
    table = pts.sort_values("ai_change_pp", ascending=False)[
        ["country", "geo", "ai_pct_base", "ai_pct_end", "ai_change_pp", "lp_growth_pct",
         "lp_level_base_pct_eu", "lp_end_flag", "ai_series_break"]
    ].rename(columns={
        "country": "Country",
        "geo": "Code",
        "ai_pct_base": f"AI use {base_year} (%)",
        "ai_pct_end": f"AI use {end_year} (%)",
        "ai_change_pp": "AI change (pp)",
        "lp_growth_pct": f"Productivity growth {span} (%)",
        "lp_level_base_pct_eu": f"Productivity level {base_year} (% of EU-27)",
        "lp_end_flag": f"{end_year} productivity flag (p = provisional)",
        "ai_series_break": "Break in AI series",
    })
    st.dataframe(table.fillna(""), hide_index=True, width="stretch")

# ---------------------------------------------------------------- section 4
render_barriers(selected)

# ---------------------------------------------------------------- section 5
render_skills(selected)

# ---------------------------------------------------------------- answer and limits
countries = default[~default["is_aggregate"]]
top_lp = countries.nlargest(3, "lp_growth_pct")
top_ai = countries.nlargest(3, "ai_change_pp")
r_values = list(r_by_period.values())
no_positive_link = all(v < 0.3 for v in r_values)


def _fmt(df: pd.DataFrame, col: str, unit: str) -> str:
    return ", ".join(f"{row.country} ({getattr(row, col):.1f}{unit})" for row in df.itertuples())


st.header("Our answer")
lead = ("**Not yet, on this evidence.** The countries where business AI adoption rose most did **not** "
        "grow labour productivity faster."
        if no_positive_link else
        "**Possibly.** Countries where AI adoption rose most also tended to grow productivity faster.")
st.markdown(
    f"{lead} Across {len(countries)} European countries and all four comparison periods, the correlation "
    f"ranges from **r = {min(r_values):.2f} to r = {max(r_values):.2f}** (we read |r| < 0.3 as no clear link).\n\n"
    f"- The biggest rises in AI use ({base0}-{end0}) were in {_fmt(top_ai, 'ai_change_pp', ' pp')}; their "
    f"productivity growth was {', '.join(f'{v:.1f}%' for v in top_ai['lp_growth_pct'])}.\n"
    f"- The fastest productivity growth ({base0}-{end0}) was in {_fmt(top_lp, 'lp_growth_pct', '%')}, where "
    f"{end0} AI use was only {', '.join(f'{v:.1f}%' for v in top_lp['ai_pct_end'])}.\n\n"
    "A reasonable reader could still argue *yes, eventually*: EU adoption has risen every survey year, "
    "and the productivity effects of new technologies can take longer than a few years to appear."
)

st.header("What this data cannot show")
st.markdown(
    "- **Cause and effect.** A correlation across countries cannot show whether AI raises or lowers "
    "productivity. We checked one alternative explanation (catch-up from a lower starting level); others, "
    "such as energy prices or post-pandemic recovery, are not in this data.\n"
    "- **Which firms benefited.** Productivity is measured for the whole economy, while AI use is a "
    "share of enterprises. The firms that adopted AI may have gained even if national figures did not move.\n"
    "- **Intensity of use.** Eurostat records whether a firm uses *at least one* AI technology, "
    "not how much it relies on it.\n"
    "- **A consistent long series.** Only four survey years exist (2021, 2023, 2024, 2025; none in 2022). "
    "The 2025 measure counts an extra technology, some series have breaks, and several 2025 productivity "
    "values are provisional.\n"
    "- **Micro-enterprises and finance.** The survey covers firms with 10+ employees and excludes the "
    "financial sector."
)

# ---------------------------------------------------------------- sources footer
st.divider()
st.subheader("Sources and data refresh")
for row in refresh.itertuples():
    st.markdown(
        f"- **Eurostat `{row.dataset_code}`**: {row.title}. "
        f"[Data browser](https://ec.europa.eu/eurostat/databrowser/view/{row.dataset_code}/default/table). "
        f"Last updated by Eurostat: **{row.source_last_update}**; downloaded: **{row.fetched_date}**."
    )
st.caption("Licence: Eurostat data is reusable under CC BY 4.0 (Commission Decision 2011/833/EU). "
           "Processing code and data dictionary are in the project repository.")
