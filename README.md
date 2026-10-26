# Is AI making Europe more productive?

An interactive data narrative (Streamlit) for *The Rise of Artificial Intelligence: Data Narrative Studio*, Assignment 3.

- **Deployed app:** https://ai-adoption-appuctivity-jjrmxanoefkvkcrimwafsx.streamlit.app
- **Assessed version:** _add the commit hash or release tag here_

## Question

**Has the rise in business AI adoption across Europe translated into faster labour productivity growth?**

The question is arguable. The same Eurostat data supports a "not yet" reading: across 30 European countries, the countries where AI use rose most did not grow productivity faster, in any of the four comparison periods we test, and the result holds after allowing for catch-up growth. It also supports a "yes, eventually" reading: EU adoption has risen in every survey year, and productivity effects of new technologies can take longer than a few years to appear.

## Persona

**Elena, senior economic policy adviser at a national ministry of the economy in an EU member state.**
Elena must recommend whether her government should fund an AI adoption subsidy for small and medium-sized businesses, justified by expected productivity gains. She needs to know where her country stands on AI adoption, whether the evidence so far links AI adoption to productivity growth, and what would actually help firms adopt AI.

## User stories

1. **As** a policy adviser, **I want** to see where my country ranks on business AI adoption, by firm size and over time, against the EU-27 average, **so that** I know whether we are leading, lagging or catching up.
2. **As** a policy adviser, **I want** to see whether the countries where AI adoption grew most also grew labour productivity faster, even after allowing for catch-up growth, **so that** I can decide whether productivity is a sound justification for an AI adoption subsidy.
3. **As** a policy adviser, **I want** to see why firms that considered AI did not adopt it, and whether countries with more ICT specialists have more firms using AI, **so that** I can judge whether a cost subsidy or a skills policy targets the barrier that actually holds firms back.

### Walking through each story in the app

| Story | Where in the app | How |
|---|---|---|
| 1 | Sections 1 and 2 | Pick a **survey year** and **firm size** in the sidebar; the ranking chart re-sorts. Add your country to **Compare countries** to highlight it, see its firm-size breakdown, and follow its trend against the EU-27 average in the line chart and value table. |
| 2 | Section 3 and *Our answer* | The first scatter plot compares each country's rise in AI use with its productivity growth; switch the **comparison period** to test robustness. *Is it just catch-up?* adjusts for each country's starting productivity level. Read the answer and the limits below it. |
| 3 | Sections 4 and 5: *What holds firms back?* and *Do digital skills go with AI adoption?* | In section 4, choose a **country**, **firm size** and **survey year**; the chart ranks the reasons for not using AI against the EU-27 average, and the text states the most cited reason and where cost ranks. In section 5, choose a **year** and **highlight a country**; the scatter plot compares each country's share of ICT specialists with its AI adoption, the bar chart shows each country's skills gap to the EU-27, and the side panel tests whether the link holds among countries at a similar productivity level. |

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Regenerating the data

```bash
python scripts/fetch_data.py   # optional: re-download the raw samples from the Eurostat API
python scripts/process.py      # rebuild data/processed/ from data/raw/
```

`process.py` is deterministic: running it on the committed raw samples reproduces the committed processed files exactly. Every transform is documented in [`docs/data_dictionary.md`](docs/data_dictionary.md).

## Repository structure

```
app.py                       Streamlit app (reads data/processed/ only)
scripts/fetch_data.py        downloads raw samples from the Eurostat API
scripts/process.py           raw samples -> processed files
scripts/process_barriers.py  barriers transform (called by process.py)
views/barriers.py            section 4: reasons for not using AI
scripts/process_skills.py    ICT specialists transform (called by process.py)
views/skills.py              section 5: ICT specialists vs AI adoption
data/raw/                    unmodified Eurostat extracts + fetch log
data/processed/              files the app reads
docs/data_dictionary.md      every dataset: source, URL, licence, columns, units, keys, coverage, transform
docs/ai_provenance_matrix.md one row per substantive AI use
docs/data_ai_disclosure.md   Data and AI disclosure statement
```

## Data sources

- Eurostat, *Artificial intelligence by size class of enterprise* (`isoc_eb_ai`): AI adoption and reasons for not using AI, CC BY 4.0.
- Eurostat, *Labour productivity and unit labour costs* (`nama_10_lp_ulc`): real productivity index and productivity level, CC BY 4.0.
- Eurostat, *Employed ICT specialists - total* (`isoc_sks_itspt`): ICT specialists as a % of total employment, CC BY 4.0.

## Team

| Member | Contribution |
|---|---|
| Purvesh Jayeshbhai Ribadiya (lead) | Question and persona; data pipeline (`scripts/`); sections 1-3 of the app, including the comparison-period robustness check and the catch-up analysis; data dictionary for the adoption and productivity datasets |
| Shifa Ansari | User story 3 and sections 4 and 5 of the app: reasons for not using AI (`scripts/process_barriers.py`, `views/barriers.py`) and ICT specialists vs AI adoption (`scripts/process_skills.py`, `views/skills.py`), with both data extracts and their data dictionary entries |
