"""The charts.

Every chart draws its colour and chrome from packages.theme, so the dashboard
reads as one system in both light and dark. Two rules worth knowing before
editing:

  * Carrier colour follows the carrier, not its current rank. Re-ranking or
    switching airport never repaints the survivors.
  * Labels are selective. The extremes get a direct label; the axis and the
    tooltip carry everything else.
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from packages import theme

DATA = 'delays_by_airport_month.parquet'

df_delays = pd.read_parquet(DATA)


# William's in-progress draft, kept as he left it (see PR #13).
# def plot_delay_rates(summary):
#     #working on the delay rates
#     lowest_rate = summary['delay_rate'].min()
#     lowest_airline = summary.loc[
#     summary['delay_rate'] == lowest_rate,
#     'carrier_label'
# ]


#     fig = px.bar(
#         summary,
#         x='delay_rate',
#         y='carrier_label',
#         orientation='h',
#         title='Delay Rate by Airline',
#         labels={
#             'carrier_label': 'Airline',
#             'delay_rate': 'Delay Rate'
#         }
#     )

#     fig.update_xaxes(tickformat='.0%')

#     fig.update_layout(
#         height=650,
#         yaxis={'autorange': 'reversed'},
#         margin=dict(l=300)
#     )

#     return fig


def short_label(name):
    """'Republic Airways (flies as United Express / ...)' -> 'Republic Airways'.

    The partner list runs to 87 characters, which no axis can hold. The full
    name stays in the tooltip, where there is room for it.
    """
    return name.split(' (')[0]


def plot_delay_rates(summary, mode='light'):
    """Delay rate by carrier. One hue for the field, status colour on the two
    extremes, direct labels only on those two."""
    p = theme.palette(mode)
    s = summary.sort_values('delay_rate', ascending=False).copy()

    base = theme.series(mode)[0]
    best, worst = s.delay_rate.min(), s.delay_rate.max()
    colors, labels = [], []
    for _, r in s.iterrows():
        if r.delay_rate == best:
            colors.append(p['good'])
            labels.append(f'✓ best · {r.delay_rate:.1%}')
        elif r.delay_rate == worst:
            colors.append(p['critical'])
            labels.append(f'△ worst · {r.delay_rate:.1%}')
        else:
            colors.append(base)
            labels.append('')

    fig = go.Figure(go.Bar(
        x=s.delay_rate, y=[short_label(c) for c in s.carrier_label],
        orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        text=labels, textposition='outside',
        textfont=dict(family=theme.FONT, size=12, color=p['ink2']),
        cliponaxis=False,
        customdata=s[['flights', 'avg_delay', 'carrier_label']].to_numpy(),
        hovertemplate=('<b>%{customdata[2]}</b><br>%{x:.1%} of arrivals 15+ min late'
                       '<br>%{customdata[0]:,.0f} arrivals'
                       '<br>%{customdata[1]:.0f} min average when late<extra></extra>'),
    ))
    theme.apply_layout(fig, mode, height=max(320, 34 * len(s) + 90),
                       showlegend=False)
    fig.update_xaxes(tickformat='.0%', range=[0, max(worst * 1.3, 0.01)],
                     title=None)
    fig.update_yaxes(title=None, ticksuffix='  ')
    # automargin (set in apply_layout) grows the left margin to fit the names;
    # the right margin is reserved for the two outside labels.
    fig.update_layout(bargap=0.34, margin=dict(r=140, t=8, b=8))
    return fig


def plot_delay_causes(shares, mode='light'):
    """What drives the delays. Nominal categories, so one colour for all of
    them -- bar length already carries the magnitude."""
    p = theme.palette(mode)
    data = shares.mean().reset_index()
    data.columns = ['cause', 'share']
    data = data.sort_values('share')

    fig = go.Figure(go.Bar(
        x=data.share, y=data.cause, orientation='h',
        marker=dict(color=theme.series(mode)[0], line=dict(width=0)),
        text=[f'{v:.0%}' for v in data.share], textposition='outside',
        textfont=dict(family=theme.FONT, size=12, color=p['ink2']),
        cliponaxis=False,
        hovertemplate='<b>%{y}</b><br>%{x:.1%} of delays<extra></extra>',
    ))
    theme.apply_layout(fig, mode, height=300, showlegend=False)
    fig.update_xaxes(tickformat='.0%', range=[0, data.share.max() * 1.22], title=None)
    fig.update_yaxes(title=None, ticksuffix='  ')
    fig.update_layout(bargap=0.42, margin=dict(r=70, t=8, b=8))
    return fig


def yearly_airline_delays(summary, mode='light', top_n=5):
    """Monthly 15+ min delays over the window, for the leading carriers in the
    current ranking. Colour is keyed to the carrier, so it survives a re-rank."""
    p = theme.palette(mode)

    dated = df_delays.copy()
    dated['date'] = pd.to_datetime(dated[['year', 'month']].assign(day=1))
    monthly = (dated.groupby(['date', 'carrier_label'])[['del15']]
                    .sum().reset_index())

    chosen = [c for c in summary['carrier_label'][:top_n]
              if not monthly[monthly.carrier_label == c].empty]
    # Every line on screen gets its own hue: a carrier keeps its preferred slot
    # where that slot is free, and takes the nearest free one where it is not.
    colors = theme.assign_colors(chosen, theme.carrier_slots(df_delays), mode)

    fig = go.Figure()
    for carrier in chosen:
        d = monthly[monthly.carrier_label == carrier]
        fig.add_trace(go.Scatter(
            x=d.date, y=d.del15, name=short_label(carrier), mode='lines',
            line=dict(color=colors[carrier], width=2),
            hovertemplate='%{y:,.0f} delays<extra>%{fullData.name}</extra>',
        ))
    theme.apply_layout(fig, mode, height=330)
    fig.update_xaxes(showgrid=False, title=None)
    fig.update_yaxes(showgrid=True, gridcolor=p['grid'], title=None,
                     tickformat=',.0f')
    fig.update_layout(hovermode='x unified', margin=dict(r=20, t=52, b=8))
    return fig


def month_delay_heatmap(summary):
    # This is a px figure for now, and has not been styled with the theme yet
    df = df_delays.copy()
    df['weather_ratio'] = df['weather_ct'] / df['del15']
    fig = px.density_heatmap(df, x='month',
                             y='year',
                             z='weather_ratio',
                             histfunc='avg',
                             color_continuous_scale='cividis')
    return fig