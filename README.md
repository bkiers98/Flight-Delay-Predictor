# Flight Delay Predictor

A Streamlit app for comparing airline on-time performance at US airports, using
five years of US DOT arrival data (2021–2026).

**Current state: starter.** [app.py](app.py) loads the prepared dataset and shows a sample of it.


## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The data file is committed, so there is no setup step beyond installing dependencies
into whichever environment you use. You need `streamlit`, `pandas`, and `pyarrow`;
the pinned conda environment from the course starter template is gone.

## Repo layout

| File | What it does |
| --- | --- |
| `app.py` | The app. Currently: loads the parquet, shows row counts and a 50-row sample. |
| `carriers.py` | Carrier reference data, cause-code labels, month names, and the raw-data cleaning step. **Edit this file** when an airline changes regional partners or merges. |
| `prep_data.py` | Turns the raw BTS CSV into the parquet the app loads. |
| `delays_by_airport_month.parquet` | Precomputed aggregates: 26,145 rows, 385 airports, 18 carriers, all 12 months. |

Columns in the parquet: `airport`, `airport_name`, `carrier`, `carrier_label`,
`carrier_kind`, `month`, `flights`, `del15`, `cancelled`, `diverted`, `delay_min`,
and one count per delay cause (`carrier_ct`, `weather_ct`, `nas_ct`, `security_ct`,
`late_aircraft_ct`).

## Where the data comes from

The source is the BTS "Airline Delay Cause" table:
<https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp>

`delays_by_airport_month.parquet` was built from that download by `prep_data.py`, which drops carriers that stopped reporting in the most recent month, folds merged carriers into the surviving code (Hawaiian now reports under Alaska), and resolves each airport code to its current name. The `prep_data.py` was built from the Colab notebook that we worked on together. 



