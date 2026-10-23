"""Flight Delay Predictor.

Compares airline on-time performance at a chosen airport, using five years of
US DOT arrival data. Ranking lives in packages/rank.py, charts in
packages/plot_data.py, and every colour in packages/theme.py -- this file is
layout only. Run with:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

from carriers import MONTHS
from packages import theme
from packages.plot_data import (plot_delay_causes, plot_delay_rates,
                                yearly_airline_delays, month_delay_heatmap)
from packages.rank import (METRICS, MIN_FLIGHTS, airport_choices, cause_shares,
                           filter_flights, month_number, rank, summarize)

DATA = 'delays_by_airport_month.parquet'

st.set_page_config(page_title='Flight Delay Predictor', layout='wide',
                   page_icon='🛬')

MODE = theme.current_mode()
PAL = theme.palette(MODE)
st.markdown(theme.css(MODE), unsafe_allow_html=True)


@st.cache_data
def load():
    return pd.read_parquet(DATA)


def kpi(label, value, sub='', tag=None, tone='good'):
    """A stat tile. When the story is one number, the number is the chart."""
    tag_html = f'<div class="kpi-tag tag-{tone}">{tag}</div>' if tag else ''
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div>{tag_html}</div>',
        unsafe_allow_html=True)


def reading(col, value):
    """Format a metric the way its own units read."""
    if pd.isna(value):
        return '—'
    return {'delay_rate': f'{value:.1%}',
            'avg_delay': f'{value:.0f} min',
            'cancel_rate': f'{value:.2%}'}[col]


df = load()

st.markdown('# Flight Delay Predictor')
st.markdown(
    f'<p class="legend-note">Historical arrival performance by airline, '
    f'US DOT data {df.year.min()}–{df.year.max()}. '
    f'Past performance, not a forecast for any individual flight.</p>',
    unsafe_allow_html=True)

# ---- filters: one row, above everything they drive ------------------------
codes, labels = airport_choices(df)
f1, f2, f3, f4 = st.columns([3, 1.4, 1.4, 2.2])
with f1:
    airport = st.selectbox('Airport', options=codes,
                           format_func=lambda a: f'{a} — {labels[a]}',
                           index=codes.index('IND') if 'IND' in codes else 0)
with f2:
    month = st.selectbox('Month', options=['Any'] + MONTHS)
with f3:
    sort_by = st.selectbox('Rank by', list(METRICS))
with f4:
    st.write('')
    show_regional = st.toggle(
        'Include regional carriers', value=True,
        help='These airlines operate many flights sold under mainline brands. '
             'A ticket that says Delta may be flown by Endeavor.')

# ---- ranking --------------------------------------------------------------
sub = filter_flights(df, airport, month_number(month), show_regional)
# One month holds roughly a twelfth of the flights, so the floor drops with it.
floor = MIN_FLIGHTS if month == 'Any' else MIN_FLIGHTS // 10
summary = rank(summarize(sub, floor), sort_by)

scope = labels[airport] + ('' if month == 'Any' else f' · {month}')
col = METRICS[sort_by]

if summary.empty:
    st.markdown(f'<div class="section">{scope}</div>', unsafe_allow_html=True)
    st.warning('Not enough flights at this airport to compare carriers '
               'reliably. Try a larger airport, or set the month to Any.')
    st.stop()

# ---- the headline numbers -------------------------------------------------
best, worst = summary.iloc[0], summary.iloc[-1]
here_rate = sub.del15.sum() / sub.flights.sum()
national = df.del15.sum() / df.flights.sum()
gap = here_rate - national

st.markdown(f'<div class="section">{scope}</div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi(f'Best · {sort_by}', reading(col, best[col]),
        best.carrier_label, tag='✓ most reliable', tone='good')
with k2:
    kpi(f'Worst · {sort_by}', reading(col, worst[col]),
        worst.carrier_label, tag='△ least reliable', tone='bad')
with k3:
    near = abs(gap) <= 0.0005
    kpi('Delayed 15+ min', f'{here_rate:.1%}',
        'All carriers at this airport',
        tag=('at the national rate' if near else
             f'{abs(gap) * 100:.1f} pts {"above" if gap > 0 else "below"} national'),
        tone='bad' if gap > 0 and not near else 'good')
with k4:
    kpi('Arrivals compared', f'{sub.flights.sum():,.0f}',
        f'{len(summary)} carriers over the floor of {floor:,}')

tab1, tab2, tab3, tab4 = st.tabs(['Detail Charts', 'Table', 'Background Charts', 'Documentation'])

# ---- charts ---------------------------------------------------------------
with tab1:
# Visualizations related to the predictive model exist here

    left, right = st.columns([5, 4])

    with left:
        st.markdown('<div class="section">Delay rate by airline</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(plot_delay_rates(summary, MODE),
                        width='stretch', config={'displayModeBar': False})

    with right:
        st.markdown('<div class="section">Delays over time · top 5 here</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(yearly_airline_delays(summary, MODE),
                        width='stretch', config={'displayModeBar': False})

        st.markdown('<div class="section">Why flights are delayed</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(plot_delay_causes(cause_shares(summary), MODE),
                        width='stretch', config={'displayModeBar': False})

# ---- the table view -------------------------------------------------------
with tab2:
#The tabular output from the predictive model exists here

# Three light-mode series colours sit under 3:1 on the surface, so the palette
# carries a relief obligation: the exact numbers stay available as text.
    st.markdown('<div class="section">Every carrier, ranked</div>',
                unsafe_allow_html=True)
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
                'Delayed 15+ min', format='percent', min_value=0.0, max_value=0.5),
            'avg_delay': st.column_config.NumberColumn(
                'Avg delay when late', format='%.0f min'),
            'cancel_rate': st.column_config.NumberColumn(
                'Cancelled', format='percent'),
            'top_cause': st.column_config.TextColumn('Most common cause'),
        })

    st.markdown(
        '<p class="legend-note">Monthly totals, so this says nothing about day of '
        'week or time of day. Arrivals only, by airport rather than by route. '
        'Airline–airport pairs below the flight floor are hidden, because a handful '
        'of flights produces an unstable rate.</p>',
        unsafe_allow_html=True)

with tab3:
#Visualizations or other information relating to the DataFrame as a whole exist here

    left, right = st.columns(2)

    with left:
        st.plotly_chart(month_delay_heatmap(summary),
                                width='stretch', config={'displayModeBar': False})

with tab4:
# Documentation for the dataset exists here, maybe information about how we
# arrived at our recommendation as well?

    st.markdown('<div class="section">Documentation coming soon...</div>',
                unsafe_allow_html=True)
