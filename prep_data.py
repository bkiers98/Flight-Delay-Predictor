"""Precompute the aggregates the app needs.

Run this once whenever new BTS data is downloaded:

    python prep_data.py Airline_Delay_Cause.csv

It writes delays_by_airport_month.parquet, which the app loads instead of the
raw 110k-row file. Keeps Streamlit fast and the repo small.
"""
import sys
import pandas as pd
from carriers import prepare, CAUSE_CT

OUT = 'delays_by_airport_month.parquet'


def build(path):
    df = prepare(pd.read_csv(path))

    keys = ['airport', 'airport_name', 'carrier', 'carrier_label',
            'carrier_kind', 'month']
    agg = (df.groupby(keys, as_index=False)
             .agg(flights=('arr_flights', 'sum'),
                  del15=('arr_del15', 'sum'),
                  cancelled=('arr_cancelled', 'sum'),
                  diverted=('arr_diverted', 'sum'),
                  delay_min=('arr_delay', 'sum'),
                  **{c: (c, 'sum') for c in CAUSE_CT}))

    years = sorted(df.year.unique())
    agg.attrs['coverage'] = f'{years[0]} to {years[-1]}'
    return agg


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'Airline_Delay_Cause.csv'
    out = build(path)
    out.to_parquet(OUT, index=False)
    print(f'wrote {OUT}: {len(out):,} rows, '
          f'{out.airport.nunique()} airports, {out.carrier.nunique()} carriers')
