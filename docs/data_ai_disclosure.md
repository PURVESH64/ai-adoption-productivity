# Data and AI disclosure statement

## Data

- All data in this app comes from public Eurostat datasets: *Artificial intelligence by size class of enterprise* (`isoc_eb_ai`) and *Labour productivity and unit labour costs* (`nama_10_lp_ulc`).
- They are reused under CC BY 4.0 (Commission Decision 2011/833/EU). Eurostat is acknowledged as the source in the app footer and in this repository.
- Raw samples were downloaded unmodified from the Eurostat API (`scripts/fetch_data.py`). Every processed file is produced from them by `scripts/process.py`, and each transform is documented in `docs/data_dictionary.md`.
- No personal data is used. All figures are national or EU-level aggregates.
- Known limits of the data (no 2022 AI survey, a wider AI definition from 2025, series breaks, provisional 2025 productivity values, firms with fewer than 10 employees and the financial sector not covered) are stated in the app under *What this data cannot show*.

## Use of AI tools

- We used generative AI assistance (the Cursor AI coding agent) to help find suitable datasets, write the data download and processing scripts, build the Streamlit app, and draft documentation and on-screen text.
- Each substantive use is recorded in `docs/ai_provenance_matrix.md`: who used it, what was asked, what came back, how it was checked, and the outcome.
- AI output was treated as a draft. Team members checked numbers against the raw Eurostat files, reran the processing scripts, tested the interactions and colour accessibility, and edited the text so that claims stay within the data.
- The team takes full responsibility for the analysis, the design decisions and every claim made in the app.

_Signed:_ Purvesh Jayeshbhai Ribadiya (26 october 2026), Shifa Ansari (26 october 2026)
