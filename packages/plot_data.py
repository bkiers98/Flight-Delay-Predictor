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





def plot_delay_rates(summary):
    fig = px.bar(
        summary,
        x='delay_rate',
        y='carrier_label',
        orientation='h',
        title='Delay Rate by Airline',
        labels={
            'carrier_label': 'Airline',
            'delay_rate': 'Delay Rate'
        }
    )

    fig.update_xaxes(tickformat='.0%')

    fig.update_layout(
        height=650,
        yaxis={'autorange': 'reversed'},
        yaxis_tickangle=-45

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


def month_delay_heatmap(summary):
    df = df_delays.copy()
    carrier = summary['carrier_label'][0]
    
    mask = (df['carrier_label'] == carrier)
    df_masked = df[mask]
    df_masked['weather_ratio'] = df_masked['weather_ct'] / df_masked['del15']
    fig = px.density_heatmap(df_masked, x='month',
                             y='year',
                             z='weather_ratio',
                             histfunc='avg',
                             color_continuous_scale='cividis')
    return fig
  