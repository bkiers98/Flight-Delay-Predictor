"""Flight Delay Predictor.

Compares airline on-time performance at a chosen airport, using five years of
US DOT arrival data.
"""
import pandas as pd
import streamlit as st

from carriers import MONTHS
from packages.plot_data import *
from packages.rank import (METRICS, MIN_FLIGHTS, airport_choices,
                           filter_flights, month_number, rank, summarize)

DATA = 'delays_by_airport_month.parquet'

st.set_page_config(page_title='Flight Delay Predictor', layout='wide')


@st.cache_data
def load():
    return pd.read_parquet(DATA)


def best_line(row, sort_by):
    """One-line summary of the top carrier, phrased for the metric ranked on."""
    col = METRICS[sort_by]
    value = row[col]
    if pd.isna(value):
        return f'Best on **{sort_by.lower()}**: **{row.carrier_label}**'
    reading = {
        'delay_rate': f'{value:.0%} of arrivals delayed 15 minutes or more',
        'avg_delay': f'{value:.0f} min average delay when late',
        'cancel_rate': f'{value:.1%} of arrivals cancelled',
    }[col]
    return f'Best on **{sort_by.lower()}**: **{row.carrier_label}** ({reading})'


df = load()

st.title('Flight Delay Predictor')
st.caption('Historical arrival performance by airline, US DOT data, 2021 to 2026. '
           'Past performance, not a forecast for any individual flight.')

# ---- inputs ----------------------------------------------------------------
codes, labels = airport_choices(df)

col1, col2 = st.columns([2, 1])
with col1:
    flex = st.container(horizontal=True)
    airport = flex.selectbox('Airport', options=codes,
                           format_func=lambda a: f'{a} — {labels[a]}',
                           index=codes.index('IND') if 'IND' in codes else 0)
    month = flex.selectbox('Month of travel', options=['Any'] + MONTHS, width=130)
    sort_by = flex.selectbox('Rank by', list(METRICS), width=170)
# with col1:
#     airport = st.selectbox('Airport', options=codes,
#                            format_func=lambda a: f'{a} — {labels[a]}',
#                            index=codes.index('IND') if 'IND' in codes else 0)
# with col2:
#     month = st.selectbox('Month of travel', options=['Any'] + MONTHS)
# with col3:
#     sort_by = st.selectbox('Rank by', list(METRICS))

show_regional = st.checkbox(
    'Include regional carriers (Republic, SkyWest, Endeavor and similar)',
    value=True,
    help='These airlines operate many flights sold under mainline brands. '
         'A ticket that says Delta may be flown by Endeavor.')

# ---- ranking ---------------------------------------------------------------
sub = filter_flights(df, airport, month_number(month), show_regional)
# One month holds roughly a twelfth of the flights, so the floor drops with it.
floor = MIN_FLIGHTS if month == 'Any' else MIN_FLIGHTS // 10
summary = rank(summarize(sub, floor), sort_by)

st.subheader(labels[airport] + ('' if month == 'Any' else f' in {month}'))

if summary.empty:
    st.warning('Not enough flights at this airport to compare carriers reliably. '
               'Try a larger airport, or set the month to Any.')
else:
    st.markdown(best_line(summary.iloc[0], sort_by))
    st.dataframe(
        summary[['carrier_label', 'carrier_kind', 'flights', 'delay_rate',
                 'avg_delay', 'cancel_rate', 'top_cause']],
        hide_index=True,
        width='stretch',
        column_config={
            'carrier_label': st.column_config.TextColumn('Airline', width='large'),
            'carrier_kind': st.column_config.TextColumn('Type'),
            'flights': st.column_config.NumberColumn('Arrivals', format='%d'),
            'delay_rate': st.column_config.ProgressColumn(
                'Delayed 15+ min', format='%.1f%%', min_value=0.0, max_value=0.5),
            'avg_delay': st.column_config.NumberColumn(
                'Avg delay when late', format='%.0f min'),
            'cancel_rate': st.column_config.NumberColumn(
                'Cancelled', format='%.1f%%'),
            'top_cause': st.column_config.TextColumn('Most common cause'),
        })

# ---- fleet-wide charts -----------------------------------------------------
# These read the parquet directly, so they cover all airports regardless of the
# filters above.
st.subheader('Across all airports')

st.caption('General performance across airlines')
fig1 = yearly_airline_delays()
st.pyplot(fig1)

st.caption('Delay rate across airlines')
fig2 = delay_rate()
st.pyplot(fig2)
