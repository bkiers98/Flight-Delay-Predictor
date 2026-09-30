"""Flight Delay Predictor — starter.

Run with:  streamlit run app.py

The full version is saved in git at commit f94b42d. To get it back:
    git show f94b42d:app.py > app.py
"""
import pandas as pd
import streamlit as st
from packages.plot_data import *

DATA = 'delays_by_airport_month.parquet'

st.set_page_config(page_title='Flight Delay Predictor', layout='wide')


@st.cache_data
def load():
    return pd.read_parquet(DATA)


df = load()

st.title('Flight Delay Predictor')
st.caption('Historical arrival performance by airline, US DOT data, 2021 to 2026.')

st.write(f'{len(df):,} rows · {df.airport.nunique()} airports · '
         f'{df.carrier.nunique()} carriers')

st.dataframe(df.head(50), use_container_width=True)

st.caption('General performance across airlines')
fig1 = airline_delays()
st.pyplot(fig1)
