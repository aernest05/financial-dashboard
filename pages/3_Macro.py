import streamlit as st
import sqlite3
import pandas as pd
from utiliy.util import *
import plotly.graph_objects as go


def get_latest(conn,series_id, name):
    db_data = read_macro_db_indicator(conn,series_id)
    latest_data = db_data.iloc[0]
    latest_value = latest_data.loc['value']
    latest_date = latest_data.loc['start_date']
    latest_date_announcement = latest_data.loc['announcement_date']
    return {
            "name": name,
            "value": latest_value,
            "date": latest_date,
            "series_id": series_id,
            'announcement_date': latest_date_announcement
        }


indicators = [
    {"series_id": "FEDFUNDS", "name": "Federal Funds Rate"},
    {"series_id": "UNRATE", "name": "Unemployment Rate"},
    {"series_id": "CPIAUCSL", "name": "CPI Inflation (YoY)"},
    {"series_id": "RSXFS", "name": "Retail Sales"},  
    {"series_id": "GDPC1", "name": "Real GDP (YoY)"},  
    {"series_id": "TB3MS", "name": "3-Month Treasury Bill Rate"}  
]

st.set_page_config(layout="wide")
st.title("📊 U.S. Economic Dashboard")
st.markdown("Latest macroeconomic indicators from FRED.")

with sqlite3.connect('financial_data.db') as conn:
    data = [get_latest(conn,ind["series_id"], ind["name"]) for ind in indicators]
    print(data)
# st.write(read_macro_db(conn,indicator))

cols = st.columns(3) 
for i, metric in enumerate(data):
    with cols[i % 3]:  # Cycle through columns (0,1,2,0,1,2)
        st.metric(
            label=f"{metric['name']} (as of {metric['date']})",
            value= f"{metric['value']:.2f}{'%' if abs(metric['value']) < 100 else ''}",
            help=f"FRED Series: {metric['series_id']}\n\nAnnounced: {metric['announcement_date']}"
        )
        # # Optional: Mini trend chart
        # trend_data = fred.get_series(metric["series_id"]).tail(12)
        # fig = px.line(trend_data, title=f"{metric['name']} Trend")
        # st.plotly_chart(fig, use_container_width=True)

# Add a disclaimer
st.caption("Source: Federal Reserve Economic Data (FRED) | Updated daily")