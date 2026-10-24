"""Section 4: what holds firms back from using AI (reasons for not using AI, Eurostat isoc_eb_ai)."""

from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parents[1] / "data" / "processed" / "ai_barriers.csv"

EU = "EU-27 average"
EU_COLOUR = "#E69F00"
COUNTRY_COLOUR = "#0072B2"
SIZES = ["All firms (10+ employees)", "Small (10-49 employees)",
         "Medium (50-249 employees)", "Large (250+ employees)"]
COST = "Costs seem too high"


@st.cache_data
def load_barriers(data_version: float) -> pd.DataFrame:
    """`data_version` (file modification time) makes the cache refresh when the data changes."""
    return pd.read_csv(DATA, keep_default_na=False, na_values=[""])


def render_barriers(selected: list[str]) -> None:
    st.header("4. What holds firms back?")
    df = load_barriers(DATA.stat().st_mtime)

    countries = [EU, *sorted(df.loc[~df["is_aggregate"], "country"].unique())]
    default = next((c for c in selected if c in countries), EU)
    c1, c2, c3 = st.columns(3)
    country = c1.selectbox("Country", countries, index=countries.index(default), key="barrier_country",
                           help="Countries that did not report reasons for not using AI are not listed.")
    size = c2.selectbox("Firm size", SIZES, key="barrier_size")
    years = sorted(df.loc[(df["country"] == country) & (df["size_class"] == size), "year"].unique(),
                   reverse=True)
    if not years:
        st.info(f"Eurostat has no data on reasons for not using AI for {size.lower()} in {country}. "
                "Try another firm size or country.")
        return
    year = c3.selectbox("Survey year", years, key="barrier_year")

    shown = [country] if country == EU else [country, EU]
    view = df[(df["country"].isin(shown)) & (df["size_class"] == size) & (df["year"] == year)]
    own = view[view["country"] == country].sort_values("pct_of_considering", ascending=False)
    if own.empty:
        st.info(f"No reasons for not using AI were reported for {country} in {year}.")
        return

    order = own["barrier"].tolist()
    y = alt.Y("barrier:N", sort=order, title=None, axis=alt.Axis(labelLimit=260))
    colour = alt.Color("country:N", scale=alt.Scale(domain=shown, range=[COUNTRY_COLOUR, EU_COLOUR][: len(shown)]),
                       legend=alt.Legend(title="Country", orient="bottom", labelLimit=200))
    offset = alt.YOffset("country:N", sort=shown)
    x = alt.X("pct_of_considering:Q", title="% of enterprises that had considered using AI",
              scale=alt.Scale(domain=[0, view["pct_of_considering"].max() * 1.12], nice=False))
    bars = alt.Chart(view).mark_bar().encode(x=x, y=y, yOffset=offset, color=colour)
    labels = alt.Chart(view).mark_text(align="left", dx=3, fontSize=11).encode(
        x="pct_of_considering:Q", y=y, yOffset=offset,
        text=alt.Text("pct_of_considering:Q", format=".1f"))
    plot_height = 26 * len(order) * len(shown)
    st.altair_chart(
        (bars + labels).properties(
            title=alt.Title(f"Reasons for not using AI, {country}, {year}", subtitle=size),
            height=plot_height,
            padding={"top": 16, "left": 5, "right": 10, "bottom": 5},
        ),
        width="stretch",
        height=plot_height + 160,
    )
    st.caption(
        "Reasons given by enterprises that had considered using AI but were not using it, as a % of all "
        "enterprises that had considered using AI. Firms could give several reasons, so the shares do not "
        "add up to 100%. Ranked by the selected country's values."
    )

    top = own.iloc[0]
    cost = own[own["barrier"] == COST]
    place = "the EU-27" if country == EU else country
    firms = size.split(" (")[0].lower()
    firms = firms if firms.endswith("firms") else f"{firms} firms"
    text = (f"Among {firms} in **{place}** in {year}, the most cited reason was "
            f"**{top['barrier'].lower()}** ({top['pct_of_considering']:.1f}%).")
    if not cost.empty and cost.iloc[0]["barrier"] != top["barrier"]:
        rank = order.index(COST) + 1
        text += (f" **Costs seem too high** ranked {rank} of {len(order)} "
                 f"({cost.iloc[0]['pct_of_considering']:.1f}%), so a subsidy that only lowers costs would "
                 f"target a less common barrier than {top['barrier'].lower()}.")
    st.markdown(text)
