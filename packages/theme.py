"""The visual system: palette, carrier colors, Plotly chrome, page CSS.

Every colour the app draws lives here, so light and dark stay in step and the
charts read as one system. Dark is a *selected* set of steps validated against
the dark surface, not an automatic flip of the light values.

Palette validated with the data-viz six checks (categorical, 5 slots):
  light  worst adjacent CVD dE 9.1, normal-vision dE 19.6  -> pass
  dark   worst adjacent CVD dE 8.4, normal-vision dE 19.3  -> pass
Three light slots sit under 3:1 on the light surface, so the relief rule
applies: charts carry direct labels and the page keeps a table view.
"""

# --- surfaces, ink, chrome -------------------------------------------------
LIGHT = {
    'surface':   '#fcfcfb',   # chart surface
    'plane':     '#f9f9f7',   # page behind the cards
    'ink':       '#0b0b0b',
    'ink2':      '#52514e',
    'muted':     '#898781',   # axis + tick labels
    'grid':      '#e1e0d9',   # hairline
    'axis':      '#c3c2b7',
    'border':    'rgba(11,11,11,0.10)',
    'good':      '#0ca30c',
    'critical':  '#d03b3b',
    'other':     '#898781',   # carriers past the 8 largest
}

DARK = {
    'surface':   '#1a1a19',
    'plane':     '#0d0d0d',
    'ink':       '#ffffff',
    'ink2':      '#c3c2b7',
    'muted':     '#898781',
    'grid':      '#2c2c2a',
    'axis':      '#383835',
    'border':    'rgba(255,255,255,0.10)',
    'good':      '#0ca30c',
    'critical':  '#d03b3b',
    'other':     '#898781',
}

# Categorical slots in fixed order. Never cycled, never reordered: the order is
# what makes the palette colourblind-safe for adjacent pairs.
SERIES_LIGHT = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4',
                '#008300', '#4a3aa7', '#e34948']
SERIES_DARK = ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181',
               '#008300', '#9085e9', '#e66767']

# Sequential blue, light -> dark, for magnitude (one hue, never a rainbow).
SEQ_LIGHT = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95']
SEQ_DARK = ['#184f95', '#256abf', '#2a78d6', '#3987e5', '#6da7ec', '#9ec5f4']

FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'

# The eight largest carriers nationally get a permanent slot. This is a
# property of the carrier, not of the current filter, so a carrier keeps its
# colour when you change airport or re-rank -- survivors are never repainted.
# Everything past the eighth draws in the neutral "other" grey and is labelled.
MAX_SERIES = 8


def palette(mode='light'):
    return DARK if mode == 'dark' else LIGHT


def series(mode='light'):
    return SERIES_DARK if mode == 'dark' else SERIES_LIGHT


def sequential(mode='light'):
    return SEQ_DARK if mode == 'dark' else SEQ_LIGHT


def carrier_slots(df):
    """Each carrier's preferred palette slot, fixed by national arrival volume.

    There are 18 carriers and 8 validated hues, so the preference wraps. That is
    safe only because a chart never draws more than a handful at once and
    assign_colors() resolves any collision among the few actually on screen.
    """
    ranked = (df.groupby('carrier_label').flights.sum()
                .sort_values(ascending=False).index.tolist())
    return {c: i % MAX_SERIES for i, c in enumerate(ranked)}


def assign_colors(carriers, slot_pref, mode='light'):
    """Colour for each carrier on screen: its preferred slot where free, else
    the nearest unused one.

    The preference is a property of the carrier, not of its rank in the current
    view, so re-ranking leaves the common case untouched. The fallback only
    fires when two carriers that share a preferred slot appear together -- and
    it beats the alternative, which is two identical lines.
    """
    slots = series(mode)
    out, used = {}, set()
    for c in carriers:
        want = slot_pref.get(c, 0)
        if want in used:
            want = next((s for s in range(MAX_SERIES) if s not in used), want)
        used.add(want)
        out[c] = slots[want]
    return out


def apply_layout(fig, mode='light', height=None, showlegend=None, title=None):
    """One Plotly chrome for every chart: hairline grid, recessive axes, no
    toolbar clutter, text in ink tokens rather than series colour."""
    p = palette(mode)
    # Only set `title` when there is one: passing None serialises to a null
    # title and Plotly renders the literal string "undefined".
    layout = dict(
        template='none',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT, size=13, color=p['ink2']),
        margin=dict(l=8, r=20, t=44 if title else 12, b=8),
        hoverlabel=dict(bgcolor=p['surface'], bordercolor=p['border'],
                        font=dict(family=FONT, size=12, color=p['ink'])),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0,
                    bgcolor='rgba(0,0,0,0)', font=dict(size=12, color=p['ink2']),
                    title_text=''),
    )
    if title:
        layout['title'] = dict(text=title, font=dict(size=15, color=p['ink']),
                               x=0, xanchor='left', pad=dict(b=12))
    if height is not None:
        layout['height'] = height
    if showlegend is not None:
        layout['showlegend'] = showlegend
    fig.update_layout(**layout)
    fig.update_xaxes(showgrid=True, gridcolor=p['grid'], gridwidth=1, zeroline=False,
                     linecolor=p['axis'], tickfont=dict(color=p['muted'], size=12),
                     title_font=dict(color=p['muted'], size=12), automargin=True)
    fig.update_yaxes(showgrid=False, zeroline=False, linecolor=p['axis'],
                     tickfont=dict(color=p['muted'], size=12),
                     title_font=dict(color=p['muted'], size=12), automargin=True)
    return fig


def current_mode():
    """The viewer's theme, so dark uses its own validated steps."""
    try:
        import streamlit as st
        return 'dark' if st.context.theme.type == 'dark' else 'light'
    except Exception:
        return 'light'


def css(mode='light'):
    """Page chrome: card surfaces, KPI tiles, tighter default spacing."""
    p = palette(mode)
    return f"""
<style>
  .stApp {{ background: {p['plane']}; }}
  .block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1500px; }}
  h1, h2, h3, h4 {{ font-family: {FONT}; color: {p['ink']}; letter-spacing: -0.015em; }}
  h1 {{ font-size: 1.9rem !important; font-weight: 650 !important; margin-bottom: .1rem !important; }}

  /* cards */
  .card {{
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    height: 100%;
  }}

  /* KPI tile: the number IS the chart */
  .kpi {{
    background: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 14px;
    padding: .95rem 1.1rem 1rem;
    height: 100%;
  }}
  .kpi-label {{
    font: 500 .72rem/1.1 {FONT};
    letter-spacing: .07em; text-transform: uppercase;
    color: {p['muted']}; margin-bottom: .45rem;
  }}
  .kpi-value {{
    font: 650 1.95rem/1.05 {FONT};
    color: {p['ink']}; margin-bottom: .2rem;
  }}
  .kpi-sub {{ font: 400 .8rem/1.3 {FONT}; color: {p['ink2']}; }}
  .kpi-tag {{
    display: inline-flex; align-items: center; gap: .3rem;
    font: 600 .75rem/1 {FONT}; padding: .22rem .5rem;
    border-radius: 999px; margin-top: .5rem;
  }}
  .tag-good {{ color: {p['good']}; background: color-mix(in srgb, {p['good']} 12%, transparent); }}
  .tag-bad  {{ color: {p['critical']}; background: color-mix(in srgb, {p['critical']} 12%, transparent); }}

  .section {{
    font: 600 .74rem/1 {FONT}; letter-spacing: .09em;
    text-transform: uppercase; color: {p['muted']};
    margin: .4rem 0 .7rem;
  }}
  .legend-note {{ font: 400 .78rem/1.4 {FONT}; color: {p['muted']}; }}

  /* let the filter row breathe without a heavy container */
  div[data-testid="stHorizontalBlock"] {{ gap: .75rem; }}
  footer, #MainMenu {{ visibility: hidden; }}
</style>
"""
