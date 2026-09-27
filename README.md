# Flight Delay Predictor

A Streamlit app that compares airline on-time performance at a chosen US airport,
using five years of US DOT arrival data (2021–2026).

Pick an airport, optionally narrow to a month of travel, and the app ranks every
airline serving that airport by delay rate, average delay when late, or
cancellation rate — then breaks down what causes the delays.

It reports **historical performance, not a forecast for an individual flight.**

**Live app:** <!-- TODO: paste the streamlit.app URL for main here -->

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

That's it — the data file is committed, so there is no setup step beyond installing
dependencies.

If you use conda, note that the pinned template environment from the course starter
is gone; this app only needs `streamlit`, `pandas`, and `pyarrow`.

## Repo layout

| File | What it does |
| --- | --- |
| `app.py` | The whole UI: inputs, ranking table, cause breakdown. |
| `carriers.py` | Carrier reference data and the raw-data cleaning step. **Edit this file** when an airline changes regional partners or merges. |
| `prep_data.py` | Turns the raw BTS CSV into the parquet the app loads. |
| `delays_by_airport_month.parquet` | Precomputed aggregates: 26,145 rows, 385 airports, 18 carriers. |

The app never reads the raw CSV. It loads only the parquet, which keeps startup
fast on Streamlit Cloud.

## Refreshing the data

The source is the BTS "Airline Delay Cause" table:
<https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp>

Download the CSV, then:

```bash
python prep_data.py Airline_Delay_Cause.csv
```

This rewrites `delays_by_airport_month.parquet`. The raw CSV is gitignored — only the
parquet gets committed. Commit the regenerated parquet so the deployed apps pick it up.

`prep_data.py` drops carriers that stopped reporting in the most recent month, folds
merged carriers into the surviving code (Hawaiian now reports under Alaska), and
resolves each airport code to its current name.

## Working on a feature

Each of us has a branch named after us (`Ben-Noetzel-Kiers`, `Evanka-Amin`,
`Faezeh-Rezaee`, `William-Kosso`). Work on your own branch, not on `main`.

```bash
git checkout your-branch
git merge main          # pick up the current app before you start
# ...make your changes...
streamlit run app.py    # check it locally first
git push origin your-branch
```

### Get a live preview of your own branch

Streamlit Community Cloud deploys one app per repo + branch + file, so you can have
your own running copy without touching the shared one:

1. Go to <https://share.streamlit.io> and sign in with GitHub.
2. Click **Create app** and choose this repo.
3. Set **Branch** to your branch and **Main file path** to `app.py`.
4. Deploy. Your branch name becomes part of the app's URL, so it won't collide with
   the app deployed from `main`.

After that, every push to your branch redeploys your preview automatically — no need
to click anything again. Share that URL when you want someone to look at your work in
progress.

The app needs no secrets, so there is nothing to configure in Secrets Management.

## Things worth testing before we meet

- Airports other than the IND default, including small ones where carriers fall below
  the flight minimum and the warning appears.
- The month filter — it drops the flight minimum to 50, so thin months get noisier.
- Toggling regional carriers off, which should leave only mainline brands.
- All three ranking options.

## Notes and limitations

- Monthly totals only, so the data says nothing about day of week or time of day.
- Arrivals only, and by airport rather than by route.
- Airline-airport pairs under 500 flights in the window are hidden, because a handful
  of flights produces an unstable rate.
- Regional carriers fly under mainline brands: a ticket saying United may be operated
  by SkyWest or Republic. That's why they're labeled "flies as ...".
- The course template told us to keep data off GitHub. We commit the parquet anyway
  because it is 695 KB of public aggregates and it lets the app deploy with no
  database or Google Sheets dependency. If that becomes a problem for grading, the
  alternative is hosting the parquet externally and reading it by URL in `load()`.
