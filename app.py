"""Flight Delay Predictor.

Compares airline on-time performance at a chosen airport, using five years of
US DOT arrival data.
"""
import pandas as pd
import streamlit as st


from carriers import MONTHS

from packages.plot_data import *

from packages.rank import (
    METRICS,
    MIN_FLIGHTS,
    airport_choices,
    filter_flights,
    month_number,
    rank,
    summarize,
    cause_shares,
)
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

cols = st.columns([2, 3])

top_left_cell = cols[0].container(
    border=True, height='stretch'
)

with top_left_cell:
    flex = st.container(horizontal=True)
    airport = flex.selectbox('Airport', options=codes,
                           format_func=lambda a: f'{a} — {labels[a]}',
                           index=codes.index('IND') if 'IND' in codes else 0, 
                           width=500)
    month = flex.selectbox('Month of travel', options=['Any'] + MONTHS, width=130)
    sort_by = flex.selectbox('Rank by', list(METRICS), width=170)
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

with top_left_cell:
    if summary.empty:
        st.warning('Not enough flights at this airport to compare carriers reliably. '
                'Try a larger airport, or set the month to Any.')
    else:
        st.subheader(best_line(summary.iloc[0], sort_by).split(' (')[0])

mid_left_cell_1 = cols[0].container(
    border=True, height='stretch', horizontal_alignment='left'
)
with mid_left_cell_1:
    st.markdown(
        f"<h3>Airline Delay Rates at "
        f"<span style='color: #FF4B4B;'>{labels[airport]}</span></h3>",
        unsafe_allow_html=True
    )

    fig = plot_delay_rates(summary)
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

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

top_right_cell = cols[1].container(
    border=True, height='stretch'
)

with top_right_cell:
    fig1 = yearly_airline_delays(summary)
    st.plotly_chart(fig1)

mid_right_cell_1 = cols[1].container(
    border=True, height='stretch'
)

# ---- fleet-wide charts -----------------------------------------------------
# These read the parquet directly, so they cover all airports regardless of the
# filters above.

with mid_right_cell_1:
    st.subheader("Why are flights delayed?")
    st.caption('General performance across airlines')

    if month == "Any":
        cause_data = filter_flights(
            df,
            airport,
            month=None
        )
    else:
        cause_data = filter_flights(
            df,
            airport,
            month_number(month),
            include_regional=show_regional
        )

    cause_summary = summarize(cause_data)

    if not cause_summary.empty:
        cause_shares_df = cause_shares(cause_summary)
        fig_causes = plot_delay_causes(cause_shares_df)
        st.plotly_chart(fig_causes, width="stretch")
    else:
        st.info("No delay-cause data available for this selection.")