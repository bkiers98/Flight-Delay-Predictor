"""Carrier reference data and the cleaning step.

Edit CARRIERS if a regional changes mainline partners. Everything else in the
app reads from here, so this is the only file that needs updating.
"""
import pandas as pd

# code -> (display name, kind, mainline brands it flies under)
CARRIERS = {
    'AA': ('American Airlines',  'mainline', []),
    'DL': ('Delta Air Lines',    'mainline', []),
    'UA': ('United Airlines',    'mainline', []),
    'WN': ('Southwest Airlines', 'mainline', []),
    'AS': ('Alaska Airlines',    'mainline', []),
    'B6': ('JetBlue Airways',    'mainline', []),
    'F9': ('Frontier Airlines',  'mainline', []),
    'G4': ('Allegiant Air',      'mainline', []),
    # wholly owned regionals, one partner each
    '9E': ('Endeavor Air',      'regional', ['Delta Connection']),
    'MQ': ('Envoy Air',         'regional', ['American Eagle']),
    'OH': ('PSA Airlines',      'regional', ['American Eagle']),
    'PT': ('Piedmont Airlines', 'regional', ['American Eagle']),
    'QX': ('Horizon Air',       'regional', ['Alaska']),
    # independent regionals, fly for several mainlines
    'OO': ('SkyWest Airlines',  'regional', ['United Express', 'Delta Connection',
                                             'American Eagle', 'Alaska']),
    'YX': ('Republic Airways',  'regional', ['United Express', 'American Eagle',
                                             'Delta Connection']),
    'YV': ('Mesa Airlines',     'regional', ['United Express']),
    'G7': ('GoJet Airlines',    'regional', ['United Express']),
    'C5': ('CommuteAir',        'regional', ['United Express']),
    'ZW': ('Air Wisconsin',     'regional', ['United Express']),
}

# carriers whose flights now report under another code
MERGED_INTO = {'HA': 'AS'}   # Hawaiian folded into Alaska, Jan 2026

CAUSE_CT = ['carrier_ct', 'weather_ct', 'nas_ct', 'security_ct', 'late_aircraft_ct']
CAUSE_LABELS = {
    'carrier_ct': 'Carrier',
    'weather_ct': 'Weather',
    'nas_ct': 'Air system',
    'security_ct': 'Security',
    'late_aircraft_ct': 'Late aircraft',
}
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']


def make_label(code):
    name, kind, partners = CARRIERS[code]
    if kind == 'mainline':
        return name + (' (includes Hawaiian)' if code == 'AS' else '')
    return f"{name} (flies as {' / '.join(partners)})"


def prepare(df):
    """Clean the raw BTS extract. Run on the raw frame only, not twice."""
    df = df.dropna(subset=['arr_flights']).copy()

    counts = ['arr_del15'] + CAUSE_CT + ['arr_cancelled', 'arr_diverted']
    df[counts] = df[counts].fillna(0)
    df = df.sort_values(['year', 'month'])

    # fold merged carriers into their surviving code
    df['carrier'] = df.carrier.replace(MERGED_INTO)

    # keep only carriers still reporting in the latest month
    ym = df.year * 100 + df.month
    still_active = ym.groupby(df.carrier).max() == ym.max()
    df = df[df.carrier.isin(still_active[still_active].index)]
    df = df[df.carrier.isin(CARRIERS)]

    # codes are stable, names drift: resolve each code to its current name
    df['airport_name']  = df.airport.map(df.groupby('airport').airport_name.last())
    df['carrier_label'] = df.carrier.map(make_label)
    df['carrier_kind']  = df.carrier.map(lambda c: CARRIERS[c][1])
    return df
