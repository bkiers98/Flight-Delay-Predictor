import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.express as px


DATA = 'delays_by_airport_month.parquet'

df_delays = pd.read_parquet(DATA)



# def airline_delays():
#   sns.set_theme()

#   df_airport_airlines = df_delays.groupby(['airport_name', 'carrier_label']) \
#                                   [['flights', \
#                                     'del15', \
#                                       'cancelled', \
#                                       'diverted', \
#                                       'delay_min']] \
#                                       .sum()
#   df_airport_airlines.reset_index(inplace=True)
#   fig1, ax = plt.subplots()
#   sns.scatterplot(data=df_airport_airlines, \
#                                 x='flights', \
#                                   y='del15', \
#                                   hue='delay_min', \
#                                   ax=ax)

#   return fig1

# def delay_rate():
#     df_rate = (
#         df_delays
#         .groupby(['airport_name', 'carrier_label'])[['flights', 'del15']]
#         .sum()
#     )

#     df_rate['delay_rate'] = (df_rate['del15'] / df_rate['flights']) * 100

#     df_rate.reset_index(inplace=True)

#     fig2, ax = plt.subplots()

#     sns.scatterplot(
#         data=df_rate,
#         x='flights',
#         y='delay_rate',
#         hue='delay_rate',
#         ax=ax
#     )

#     return fig2





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



def plot_delay_rates(summary):
    summary = summary.copy()

    summary['chart_label'] = summary['carrier_label'].replace({
    'Alaska Airlines (includes Hawaiian)': 'Alaska Airlines',
    'SkyWest Airlines (flies as United Express / Delta Connection / American Eagle / Alaska)': 'SkyWest',
    'Republic Airways (flies as United Express / American Eagle / Delta Connection)': 'Republic Airways',
    'Envoy Air (flies as American Eagle)': 'Envoy Air',
    'PSA Airlines (flies as American Eagle)': 'PSA Airlines',
    'GoJet Airlines (flies as United Express)': 'GoJet',
'Endeavor Air (flies as Delta Connection)': 'Endeavor Air',
'Mesa Airlines (flies as United Express)': 'Mesa Airlines'
})

    lowest_rate = summary['delay_rate'].min()

    lowest_airline = summary.loc[
        summary['delay_rate'] == lowest_rate,
        'carrier_label'
    ]

    summary['color_group'] = summary['carrier_label'].apply(
        lambda airline: 'lowest_airline'
        if airline in lowest_airline.values
        else 'other'
    )

    fig = px.bar(
        summary,
        x='delay_rate',
        y='chart_label',
        orientation='h',
        title='Delay Rate by Airline',
        labels={
            'chart_label': 'Airline',
            'delay_rate': 'Delay Rate'
        },
        color='color_group',
        color_discrete_map={
            'lowest_airline': 'green',
            'other': 'gray'
        },
        text='delay_rate'
    )

    fig.update_traces(
    texttemplate='%{x:.0%}',
    textposition='outside',
    textfont=dict(size=12, color='black', family='Arial Black'),
    width=0.65
)

    fig.update_xaxes(
    tickformat='.0%',
    showgrid=True,
    gridcolor='lightgray',
    zeroline=False,
    range=[0, summary['delay_rate'].max() * 1.20]
)

    fig.update_layout(
    height=max(500, len(summary) * 42),
    autosize=True,
  margin=dict(l=10, r=100, t=55, b=55),
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=12)
)
    return fig



def plot_delay_causes(shares):
    cause_data = (
        shares
        .mean()
        .reset_index()
    )

    cause_data.columns = ["cause", "share"]

    fig = px.bar(
        cause_data,
        x="share",
        y="cause",
        orientation="h",
        title="Why Are Flights Delayed?",
        labels={
            "share": "Share of Delays",
            "cause": "Delay Cause"
        },
    )

    fig.update_xaxes(tickformat=".0%")
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=450,
    )

    return fig


def plot_delay_causes(shares):
    cause_data = shares.mean().reset_index()
    cause_data.columns = ["cause", "share"]

    fig = px.bar(
        cause_data,
        x="share",
        y="cause",
        orientation="h",
        title="Why Are Flights Delayed?",
        labels={
            "share": "Share of Delays",
            "cause": "Delay Cause"
        }
    )

    fig.update_xaxes(tickformat=".0%")

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=450
    )

    return fig

def yearly_airline_delays(summary):
  df_dated = df_delays.copy()
  df_dated['date'] = pd.to_datetime(df_dated[['year', 'month']] \
                                    .assign(day=1))

  df_date_sum = df_dated.groupby(['date', 'carrier_label'])[['del15']] \
                                    .sum() \
                                    .reset_index()

  carrier_list = [carrier for index, carrier in enumerate(
                      summary['carrier_label']
                      ) if index < 5]

  mask = (df_date_sum['carrier_label'].isin(carrier_list))
  fig = px.line(df_date_sum[mask], x='date', y='del15', color='carrier_label',
                title='Airline Performance over 5 Years',
                labels={
                   'date':'Date',
                   'del15':'Total delays',
                   'carrier_label':'Carrier'
                })
  fig.update_layout(legend=dict(
      yanchor='top',
      y=1.1,
      xanchor='left',
      x=0.01
  ))

  return fig
  
