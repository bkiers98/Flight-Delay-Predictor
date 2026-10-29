
import pandas as pd
import plotly.express as px


def airport_delay_map(flights, airports):

    # 1. Summarize flight performance by airport
    summary = (
        flights.groupby(["airport", "airport_name"], as_index=False)
        .agg(
            flights=("flights", "sum"),
            delayed=("del15", "sum")
        )
    )

    # 2. Calculate delay rate as a percentage
    summary["delay_rate"] = (
        summary["delayed"] / summary["flights"] * 100
    )

    # 3. Assign airports to distinct delay-rate categories
    def delay_category(rate):
        if rate < 10:
            return "Below 10%"
        elif rate < 20:
            return "10%–20%"
        elif rate < 30:
            return "20%–30%"
        elif rate < 40:
            return "30%–40%"
        else:
            return "40% or higher"

    summary["delay_category"] = summary["delay_rate"].apply(
        delay_category
    )

    # 4. Make airport markers visible without allowing
    # large airports to dominate the map
    summary["marker_size"] = (
        summary["flights"].clip(lower=1000) ** 0.5
    )

    # 5. Prepare airport coordinates
    # Try IATA codes first, then local codes for unmatched airports
    iata = (
        airports.dropna(
            subset=["iata_code", "latitude_deg", "longitude_deg"]
        )
        .drop_duplicates("iata_code")
        .set_index("iata_code")
    )

    local = (
        airports.dropna(
            subset=["local_code", "latitude_deg", "longitude_deg"]
        )
        .drop_duplicates("local_code")
        .set_index("local_code")
    )

    map_data = summary.copy()

    map_data["latitude_deg"] = (
        map_data["airport"].map(iata["latitude_deg"])
        .fillna(map_data["airport"].map(local["latitude_deg"]))
    )

    map_data["longitude_deg"] = (
        map_data["airport"].map(iata["longitude_deg"])
        .fillna(map_data["airport"].map(local["longitude_deg"]))
    )

    map_data = map_data.dropna(
        subset=["latitude_deg", "longitude_deg"]
    )

    # 6. Define distinct colors
    category_colors = {
        "Below 10%": "#16A34A",       # Green
        "10%–20%": "#2563EB",         # Blue
        "20%–30%": "#F59E0B",         # Yellow-orange
        "30%–40%": "#EA580C",         # Orange
        "40% or higher": "#DC2626"    # Red
    }

    category_order = list(category_colors.keys())

    # 7. Create the interactive map
    fig = px.scatter_geo(
        map_data,
        lat="latitude_deg",
        lon="longitude_deg",
        size="marker_size",
        size_max=22,
        color="delay_category",
        color_discrete_map=category_colors,
        category_orders={
            "delay_category": category_order
        },
        hover_name="airport_name",
        hover_data={
            "airport": True,
            "flights": ":,",
            "delay_rate": ":.1f",
            "marker_size": False,
            "delay_category": False,
            "latitude_deg": False,
            "longitude_deg": False
        },
        scope="usa",
        title="Historical Flight Delay Rates by Airport",
        labels={
            "delay_category": "Delay rate",
            "delay_rate": "Delay rate (%)",
            "flights": "Total flights",
            "airport": "Airport code"
        }
    )

    # 8. Improve marker visibility
    fig.update_traces(
        marker=dict(
            line=dict(width=0.8, color="#334155"),
            opacity=0.9
        )
    )

    # 9. Improve map appearance
    fig.update_layout(
        height=650,
        margin=dict(l=0, r=0, t=60, b=0),
        legend=dict(
            title="Delay Rate",
            orientation="v",
            x=1.02,
            y=1,
            yanchor="top"
        )
    )

    return fig
