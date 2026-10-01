import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

DATA = 'delays_by_airport_month.parquet'

df_delays = pd.read_parquet(DATA)

def airline_delays():
  sns.set_theme()

  df_airport_airlines = df_delays.groupby(['airport_name', 'carrier_label']) \
                                  [['flights', \
                                    'del15', \
                                      'cancelled', \
                                      'diverted', \
                                      'delay_min']] \
                                      .sum()
  df_airport_airlines.reset_index(inplace=True)
  fig1, ax = plt.subplots()
  sns.scatterplot(data=df_airport_airlines, \
                                x='flights', \
                                  y='del15', \
                                  hue='delay_min', \
                                  ax=ax)

  return fig1

def delay_rate():
    df_rate = (
        df_delays
        .groupby(['airport_name', 'carrier_label'])[['flights', 'del15']]
        .sum()
    )

    df_rate['delay_rate'] = (df_rate['del15'] / df_rate['flights']) * 100

    df_rate.reset_index(inplace=True)

    fig2, ax = plt.subplots()

    sns.scatterplot(
        data=df_rate,
        x='flights',
        y='delay_rate',
        hue='delay_rate',
        ax=ax
    )

    return fig2