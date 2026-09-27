"""Flight Delay Predictor.

Compares airline on-time performance at a chosen airport, using five years of
US DOT arrival data. Run with:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

from carriers import CAUSE_CT, CAUSE_LABELS, MONTHS

DATA = 'delays_by_airport_month.parquet'
MIN_FLIGHTS = 500          # airline-airport pairs below this are hidden

st.set_page_config(page_title='Flight Delay Predictor', layout='wide')


@st.cache_data
def load():
    return pd.read_parquet(DATA)


def summarize(df, min_flights):
    """Collapse to one row per carrier and add the display metrics."""
    g = (df.groupby(['carrier_kind', 'carrier_label'], as_index=False)
           .agg(flights=('flights', 'sum'),
                del15=('del15', 'sum'),
                cancelled=('cancelled', 'sum'),
                delay_min=('delay_min', 'sum'),
                **{c: (c, 'sum') for c in CAUSE_CT}))

    g = g[g.flights >= min_flights].copy()
    g['delay_rate'] = g.del15 / g.flights
    g['avg_delay'] = (g.delay_min / g.del15).where(g.del15 > 0)
    g['cancel_rate'] = g.cancelled / g.flights
    g['top_cause'] = (g[CAUSE_CT].idxmax(axis=1)
                                 .map(CAUSE_LABELS)
                                 .where(g.del15 > 0, ''))
    return g


df = load()

st.title('Flight Delay Predictor')
st.caption('Historical arrival performance by airline, US DOT data, 2021 to 2026. '
           'Past performance, not a forecast for any individual flight.')

# ---- inputs ----------------------------------------------------------------
col1, col2, col3 = st.columns([2, 1, 1])

airports = (df[['airport', 'airport_name']].drop_duplicates()
              .sort_values('airport_name'))
labels = dict(zip(airports.airport, airports.airport_name))

with col1:
    airport = st.selectbox('Airport', options=airports.airport,
                           format_func=lambda a: f'{a} — {labels[a]}',
                           index=int((airports.airport == 'IND').argmax()))
with col2:
    month = st.selectbox('Month of travel', options=['Any'] + MONTHS)
with col3:
    sort_by = st.selectbox('Rank by',
                           ['Delay rate', 'Average delay', 'Cancellation rate'])

show_regional = st.checkbox(
    'Include regional carriers (Republic, SkyWest, Endeavor and similar)',
    value=True,
    help='These airlines operate many flights sold under mainline brands. '
         'A ticket that says Delta may be flown by Endeavor.')

# ---- filter ----------------------------------------------------------------
sub = df[df.airport == airport]
if month != 'Any':
    sub = sub[sub.month == MONTHS.index(month) + 1]
if not show_regional:
    sub = sub[sub.carrier_kind == 'mainline']

summary = summarize(sub, MIN_FLIGHTS if month == 'Any' else MIN_FLIGHTS // 10)

if summary.empty:
    st.warning('Not enough flights at this airport to compare carriers reliably. '
               'Try a larger airport, or set the month to Any.')
    st.stop()

SORT_COL = {'Delay rate': 'delay_rate',
            'Average delay': 'avg_delay',
            'Cancellation rate': 'cancel_rate'}
summary = summary.sort_values(SORT_COL[sort_by])

# ---- output ----------------------------------------------------------------
best = summary.iloc[0]
st.subheader(f'{labels[airport]}' + ('' if month == 'Any' else f' in {month}'))
st.markdown(f'Best on **{sort_by.lower()}**: **{best.carrier_label}** '
            f'({best.delay_rate:.0%} of arrivals delayed 15 minutes or more)')

st.dataframe(
    summary[['carrier_label', 'carrier_kind', 'flights', 'delay_rate',
             'avg_delay', 'cancel_rate', 'top_cause']],
    hide_index=True,
    use_container_width=True,
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

# ---- cause breakdown -------------------------------------------------------
st.subheader('What drives the delays')
shares = summary.set_index('carrier_label')[CAUSE_CT]
shares = shares.div(shares.sum(axis=1), axis=0).rename(columns=CAUSE_LABELS)
st.bar_chart(shares, horizontal=True, height=40 * len(shares) + 80)

with st.expander('Notes and limitations'):
    st.markdown(f"""
- Data is monthly totals, so this cannot say anything about day of week or time of day.
- Arrivals only, and by airport rather than by route.
- Airline-airport pairs with fewer than {MIN_FLIGHTS:,} flights in the window are hidden,
  because a handful of flights produces an unstable rate.
- Spirit ceased operations in May 2026 and is excluded. Hawaiian now reports
  under Alaska.
- Regional carriers fly under mainline brands. The ticket may say United while
  the operating carrier is SkyWest or Republic.
""")
