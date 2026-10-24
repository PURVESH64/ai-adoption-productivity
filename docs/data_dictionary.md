# Data dictionary

All data comes from Eurostat. Raw samples are unmodified API extracts; processed files are produced from them by `scripts/process.py`.

**Licence (all datasets):** Eurostat data may be reused free of charge with acknowledgement of the source, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (Commission Decision 2011/833/EU; see the [Eurostat copyright notice](https://ec.europa.eu/eurostat/about-us/policies/copyright)).

**Eurostat observation flags:** `b` = break in time series, `e` = estimated, `p` = provisional, `u` = low reliability, empty = no flag.

**Country codes:** Eurostat uses ISO 3166 alpha-2 codes, except `EL` = Greece and `EU27_2020` = EU-27 aggregate (2020 composition).

**Definition change in 2025:** Eurostat's "enterprises using at least one AI technology" (`E_AI_TANY`) counted seven technologies in 2021, 2023 and 2024. From 2025 it also counts an eighth: technologies generating pictures, video, sound or audio. Comparisons ending in 2024 therefore use a consistent definition; comparisons ending in 2025 do not.

---

## Raw source samples (`data/raw/`)

### 1. `isoc_eb_ai_sample.csv`

| Item | Value |
|---|---|
| Source | Eurostat, *Artificial intelligence by size class of enterprise* (`isoc_eb_ai`), from the annual EU survey on ICT usage and e-commerce in enterprises |
| Data browser | https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table |
| API URL used | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_eb_ai/A.10-49+50-249+GE250+GE10.C10-S951_X_K.E_AI_TANY.PC_ENT.?format=SDMX-CSV |
| Licence | CC BY 4.0 |
| Filter applied at the API | indicator `E_AI_TANY` (enterprises using at least one AI technology); unit `PC_ENT` (% of enterprises); sector `C10-S951_X_K` (all activities except the financial sector); size classes `GE10`, `10-49`, `50-249`, `GE250`; all countries |
| Rows | 560 (9 with no value) |
| Primary key | `geo`, `size_emp`, `TIME_PERIOD` |
| Time coverage | 2021, 2023, 2024, 2025 (no AI survey in 2022) |
| Latest observation | 2025 |
| Eurostat last update | 2026-06-15 |
| Transform | None. Saved exactly as returned by the API (`scripts/fetch_data.py`). |

| Column | Meaning | Unit / values |
|---|---|---|
| `DATAFLOW` | Eurostat dataset identifier | text |
| `LAST UPDATE` | Date Eurostat last updated the dataset | `dd/mm/yy hh:mm:ss` |
| `freq` | Frequency | `A` = annual |
| `size_emp` | Enterprise size class (persons employed) | `GE10`, `10-49`, `50-249`, `GE250` |
| `nace_r2` | Economic activity | `C10-S951_X_K` |
| `indic_is` | Indicator | `E_AI_TANY` |
| `unit` | Unit | `PC_ENT` = % of enterprises |
| `geo` | Country or aggregate | Eurostat geo code (36 codes) |
| `TIME_PERIOD` | Survey year | year |
| `OBS_VALUE` | Share of enterprises using at least one AI technology | % of enterprises |
| `OBS_FLAG` | Eurostat observation flag | `b` or empty |
| `CONF_STATUS` | Confidentiality status | empty in this extract |

### 2. `nama_10_lp_ulc_sample.csv`

| Item | Value |
|---|---|
| Source | Eurostat, *Labour productivity and unit labour costs* (`nama_10_lp_ulc`), national accounts |
| Data browser | https://ec.europa.eu/eurostat/databrowser/view/nama_10_lp_ulc/default/table |
| API URL used | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nama_10_lp_ulc/A.I15.RLPR_HW.?format=SDMX-CSV&startPeriod=2015 |
| Licence | CC BY 4.0 |
| Filter applied at the API | item `RLPR_HW` (real labour productivity per hour worked); unit `I15` (index, 2015 = 100); years 2015 onwards; all countries |
| Rows | 418 |
| Primary key | `geo`, `TIME_PERIOD` |
| Time coverage | 2015-2025 |
| Latest observation | 2025 (35 values provisional) |
| Eurostat last update | 2026-10-22 |
| Transform | None. Saved exactly as returned by the API (`scripts/fetch_data.py`). |

| Column | Meaning | Unit / values |
|---|---|---|
| `DATAFLOW`, `LAST UPDATE`, `freq`, `geo`, `TIME_PERIOD`, `CONF_STATUS` | As in dataset 1 | as above |
| `unit` | Unit | `I15` = index, 2015 = 100 |
| `na_item` | National accounts item | `RLPR_HW` = real labour productivity per hour worked |
| `OBS_VALUE` | Real labour productivity per hour worked | index, 2015 = 100 |
| `OBS_FLAG` | Eurostat observation flag | `p`, `b` or empty |

### 3. `nama_10_lp_ulc_level_sample.csv`

| Item | Value |
|---|---|
| Source | Eurostat, *Labour productivity and unit labour costs* (`nama_10_lp_ulc`), national accounts |
| Data browser | https://ec.europa.eu/eurostat/databrowser/view/nama_10_lp_ulc/default/table |
| API URL used | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nama_10_lp_ulc/A.PC_EU27_2020_MPPS_CP.NLPR_HW.?format=SDMX-CSV&startPeriod=2015 |
| Licence | CC BY 4.0 |
| Filter applied at the API | item `NLPR_HW` (nominal labour productivity per hour worked); unit `PC_EU27_2020_MPPS_CP` (% of the EU-27 total, based on purchasing power standards, current prices); years 2015 onwards; all countries |
| Rows | 416 |
| Primary key | `geo`, `TIME_PERIOD` |
| Time coverage | 2015-2025 |
| Latest observation | 2025 (35 values provisional) |
| Eurostat last update | 2026-10-22 |
| Transform | None. Saved exactly as returned by the API (`scripts/fetch_data.py`). |

| Column | Meaning | Unit / values |
|---|---|---|
| `DATAFLOW`, `LAST UPDATE`, `freq`, `geo`, `TIME_PERIOD`, `CONF_STATUS` | As in dataset 1 | as above |
| `unit` | Unit | `PC_EU27_2020_MPPS_CP` |
| `na_item` | National accounts item | `NLPR_HW` = nominal labour productivity per hour worked |
| `OBS_VALUE` | Productivity per hour worked relative to the EU-27 | % of EU-27 average (EU-27 = 100) |
| `OBS_FLAG` | Eurostat observation flag | `p`, `e`, `b` or empty |

### 4. `isoc_eb_ai_barriers_sample.csv`

| Item | Value |
|---|---|
| Source | Eurostat, *Artificial intelligence by size class of enterprise* (`isoc_eb_ai`), reasons for not using AI |
| Data browser | https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table |
| API URL used | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_eb_ai/A.10-49+50-249+GE250+GE10.C10-S951_X_K.E_AI_BLE+E_AI_BLEG+E_AI_BCDP+E_AI_BDDT+E_AI_BINC+E_AI_BCST+E_AI_BEC+E_AI_BNU.PC_ENT_AI_EC.?format=SDMX-CSV |
| Licence | CC BY 4.0 |
| Filter applied at the API | eight indicators "enterprises do not use AI technologies, because ..." (see `barrier_code` in file 10); unit `PC_ENT_AI_EC` (% of enterprises that ever considered using AI technologies); sector `C10-S951_X_K`; size classes `GE10`, `10-49`, `50-249`, `GE250`; all countries |
| Rows | 3,028 (55 with no value, flagged `u`) |
| Primary key | `geo`, `size_emp`, `indic_is`, `TIME_PERIOD` |
| Time coverage | 2021, 2023, 2024, 2025 (21-23 countries per year; the EU-27 aggregate from 2023) |
| Latest observation | 2025 |
| Eurostat last update | 2026-06-15 |
| Transform | None. Saved exactly as returned by the API (`scripts/fetch_data.py`). |

| Column | Meaning | Unit / values |
|---|---|---|
| `DATAFLOW`, `LAST UPDATE`, `freq`, `size_emp`, `nace_r2`, `geo`, `TIME_PERIOD`, `CONF_STATUS` | As in dataset 1 | as above |
| `indic_is` | Reason for not using AI | `E_AI_BLE`, `E_AI_BLEG`, `E_AI_BCDP`, `E_AI_BDDT`, `E_AI_BINC`, `E_AI_BCST`, `E_AI_BEC`, `E_AI_BNU` |
| `unit` | Unit | `PC_ENT_AI_EC` = % of enterprises that ever considered using AI |
| `OBS_VALUE` | Enterprises giving this reason | % of enterprises that had considered using AI |
| `OBS_FLAG` | Eurostat observation flag | `u`, `b` or empty |

### 5. `fetch_log.csv`

| Item | Value |
|---|---|
| Source | Written by `scripts/fetch_data.py` |
| Licence | Project file |
| Primary key | `sample` |
| Columns | `sample` (raw sample name), `dataset_code` (Eurostat code), `file` (raw file name), `url` (exact API URL), `fetched_utc` (download time, ISO 8601 UTC) |
| Time coverage / latest observation | Not applicable (one row per download) |
| Transform | Not applicable |

---

## Processed files (`data/processed/`)

All produced by `python scripts/process.py`. Common steps:

- **T1.** Drop rows with no `OBS_VALUE`.
- **T2.** Keep the EU-27 aggregate and named countries. Drop euro-area aggregates (`EA`, `EA12`, `EA19`, `EA20`, `EA21`).
- **T3.** Add the English `country` name, `is_aggregate` (`True` only for `EU27_2020`), integer `year` from `TIME_PERIOD`, and `obs_flag` (missing flag becomes an empty string).
- **T4.** Round values to 2 decimal places.

### 6. `ai_adoption.csv`

| Item | Value |
|---|---|
| Built from | `data/raw/isoc_eb_ai_sample.csv` |
| Rows | 535 (33 countries + EU-27; 4 size classes; 4 years; some combinations missing) |
| Primary key | `geo`, `year`, `size_class_code` |
| Time coverage | 2021, 2023, 2024, 2025 |
| Latest observation | 2025 |
| Transform | T1-T4; `size_emp` is kept as `size_class_code` and given a readable label `size_class`. North Macedonia (`MK`) drops out at T1 because it has no values. |

| Column | Meaning | Unit |
|---|---|---|
| `geo` | Eurostat geo code | code |
| `country` | Country name, or "EU-27 average" | text |
| `is_aggregate` | `True` for the EU-27 aggregate | boolean |
| `year` | Survey year | year |
| `size_class_code` | Size class code | `GE10`, `10-49`, `50-249`, `GE250` |
| `size_class` | Readable size class | e.g. "Small (10-49 employees)" |
| `ai_adoption_pct` | Enterprises using at least one AI technology | % of enterprises |
| `obs_flag` | Eurostat flag | `b` or empty |

### 7. `productivity.csv`

| Item | Value |
|---|---|
| Built from | `data/raw/nama_10_lp_ulc_sample.csv` |
| Rows | 363 (32 countries + EU-27, 11 years) |
| Primary key | `geo`, `year` |
| Time coverage | 2015-2025 |
| Latest observation | 2025 (partly provisional) |
| Transform | T1-T4. |

| Column | Meaning | Unit |
|---|---|---|
| `geo`, `country`, `is_aggregate`, `year` | As in file 6 | |
| `productivity_index_2015` | Real labour productivity per hour worked | index, 2015 = 100 |
| `obs_flag` | Eurostat flag | `p`, `b` or empty |

### 8. `productivity_level.csv`

| Item | Value |
|---|---|
| Built from | `data/raw/nama_10_lp_ulc_level_sample.csv` |
| Rows | 362 (32 countries + EU-27; one country-year has no value) |
| Primary key | `geo`, `year` |
| Time coverage | 2015-2025 |
| Latest observation | 2025 (partly provisional) |
| Transform | T1-T4. |

| Column | Meaning | Unit |
|---|---|---|
| `geo`, `country`, `is_aggregate`, `year` | As in file 6 | |
| `productivity_level_pct_eu` | Nominal labour productivity per hour worked, purchasing power standards | % of EU-27 average (EU-27 = 100) |
| `obs_flag` | Eurostat flag | `p`, `e`, `b` or empty |

### 9. `adoption_vs_productivity.csv`

| Item | Value |
|---|---|
| Built from | Processed files 6, 7 and 8 |
| Rows | 124 (31 geos: 30 countries + EU-27, × 4 comparison periods) |
| Primary key | `geo`, `base_year`, `end_year` |
| Time coverage | Base year 2021 or 2023; end year 2024 or 2025 |
| Latest observation | 2025 |
| Transform | **T5.** Use the all-firms size class (`GE10`) of file 6. **T6.** For each period (base 2021 or 2023, end 2024 or 2025), keep countries with AI adoption *and* productivity in both the base and end year (inner join on `geo`). **T7.** `ai_change_pp = ai_pct_end − ai_pct_base`. **T8.** `lp_growth_pct = (lp_index_end / lp_index_base − 1) × 100`. **T9.** `lp_level_base_pct_eu` = file 8 value for the base year. **T10.** `ai_series_break` = `True` if any AI observation from the base to the end year carries flag `b`. Results rounded to 2 decimal places. |

| Column | Meaning | Unit |
|---|---|---|
| `geo`, `country`, `is_aggregate` | As in file 6 | |
| `base_year` / `end_year` | Start / end of the comparison period | year |
| `ai_pct_base` / `ai_pct_end` | Enterprises (10+ employees) using AI in the base / end year | % of enterprises |
| `lp_index_base` / `lp_index_end` | Real labour productivity per hour worked in the base / end year | index, 2015 = 100 |
| `ai_change_pp` | Change in AI adoption | percentage points |
| `lp_growth_pct` | Productivity growth over the period | % |
| `lp_level_base_pct_eu` | Productivity level in the base year | % of EU-27 average (PPS) |
| `lp_end_flag` | Eurostat flag on the end-year productivity value | `p` or empty |
| `ai_series_break` | A break in series is flagged in the AI data for this period | boolean |

Statistics computed by the app at run time from this file, using the 30 non-aggregate rows of the chosen period:

- **r** = Pearson correlation between `ai_change_pp` and `lp_growth_pct` (2021-2024: −0.30; 2021-2025: −0.42; 2023-2024: −0.01; 2023-2025: −0.10).
- **Catch-up r** = Pearson correlation between `lp_level_base_pct_eu` and `lp_growth_pct`.
- **Partial r** = correlation between the residuals of `ai_change_pp` and of `lp_growth_pct`, each regressed by least squares on `lp_level_base_pct_eu` (2021-2024: −0.20).

### 10. `ai_barriers.csv`

| Item | Value |
|---|---|
| Built from | `data/raw/isoc_eb_ai_barriers_sample.csv` (by `scripts/process_barriers.py`, called from `scripts/process.py`) |
| Rows | 2,877 (25 countries + EU-27; 4 size classes; 8 reasons; up to 4 years) |
| Primary key | `geo`, `year`, `size_class_code`, `barrier_code` |
| Time coverage | 2021, 2023, 2024, 2025 |
| Latest observation | 2025 |
| Transform | T1-T4 (the 55 empty `u` values drop out at T1); `size_emp` is kept as `size_class_code` with a readable `size_class`; `indic_is` is kept as `barrier_code` with a readable `barrier` label. |

| Column | Meaning | Unit |
|---|---|---|
| `geo`, `country`, `is_aggregate`, `year`, `size_class_code`, `size_class` | As in file 6 | |
| `barrier_code` | Eurostat indicator code | `E_AI_BLE` lack of relevant expertise; `E_AI_BLEG` unclear legal consequences; `E_AI_BCDP` data protection and privacy concerns; `E_AI_BDDT` data availability or quality; `E_AI_BINC` incompatible with existing systems; `E_AI_BCST` costs seem too high; `E_AI_BEC` ethical considerations; `E_AI_BNU` AI not useful for the enterprise |
| `barrier` | Readable reason | text |
| `pct_of_considering` | Enterprises giving this reason for not using AI | % of enterprises that had considered using AI |
| `obs_flag` | Eurostat flag | `b` or empty |

Firms could give several reasons, so values for one country, year and size class do not add up to 100%.

### 11. `refresh_info.csv`

| Item | Value |
|---|---|
| Built from | `data/raw/fetch_log.csv` and the `LAST UPDATE` column of each raw sample |
| Rows | one per raw sample |
| Primary key | `sample` |
| Time coverage / latest observation | Not applicable |
| Transform | `LAST UPDATE` (`dd/mm/yy`) becomes ISO date `source_last_update`; `fetched_utc` is truncated to the date `fetched_date`; a readable `title` is added per sample. |

| Column | Meaning | Unit |
|---|---|---|
| `sample` | Raw sample name | text |
| `dataset_code` | Eurostat dataset code | code |
| `title` | Dataset title | text |
| `source_last_update` | When Eurostat last updated the dataset | ISO date |
| `fetched_date` | When the raw sample was downloaded (UTC) | ISO date |
| `url` | API URL used | URL |
