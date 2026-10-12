import pandas as pd

from carriers import CAUSE_CT, CAUSE_LABELS, MONTHS

MIN_FLIGHTS = 500          # airline-airport pairs below this are hidden

# Display name -> column produced by summarize(). Every metric sorts ascending:
# lower is better for all three.
METRICS = {
    'Delay rate': 'delay_rate',
    'Average delay': 'avg_delay',
    'Cancellation rate': 'cancel_rate',
}


def month_number(name):
    return MONTHS.index(name) + 1 if name in MONTHS else None


def airport_choices(df):
    a = (df[['airport', 'airport_name']].drop_duplicates()
           .sort_values('airport_name'))
    return list(a.airport), dict(zip(a.airport, a.airport_name))


def filter_flights(df, airport, month=None, include_regional=True):
    sub = df[df.airport == airport]
    if month is not None:
        sub = sub[sub.month == month]
    if not include_regional:
        sub = sub[sub.carrier_kind == 'mainline']
    return sub


def summarize(df, min_flights=MIN_FLIGHTS):
    g = (df.groupby(['carrier_kind', 'carrier_label'], as_index=False)
           .agg(flights=('flights', 'sum'),
                del15=('del15', 'sum'),
                cancelled=('cancelled', 'sum'),
                delay_min=('delay_min', 'sum'),
                **{c: (c, 'sum') for c in CAUSE_CT}))

    g = g[g.flights >= min_flights].copy()
    g['delay_rate'] = g.del15 / g.flights
    # Undefined when a carrier had no late arrivals at all, rather than 0 min.
    g['avg_delay'] = (g.delay_min / g.del15).where(g.del15 > 0)
    g['cancel_rate'] = g.cancelled / g.flights
    g['top_cause'] = (g[CAUSE_CT].idxmax(axis=1)
                                 .map(CAUSE_LABELS)
                                 .where(g.del15 > 0, ''))
    return g


def rank(summary, by='delay_rate'):
    col = METRICS.get(by, by)
    # Carriers with no late arrivals have no avg_delay; they sort last rather
    # than appearing to be the best performer.
    return summary.sort_values(col, na_position='last')


def cause_shares(summary):
    shares = summary.set_index('carrier_label')[CAUSE_CT]
    return shares.div(shares.sum(axis=1), axis=0).rename(columns=CAUSE_LABELS)
