import streamlit as st
import pandas as pd
from util.helpers import *
from util import query
import plotly.graph_objects as go

st.set_page_config(
    page_title="Macroeconomics", # The page title, shown in the browser tab.
    layout="wide", # How the page content should be laid out.
)

def get_latest(series_id, name):
    db_data = query.read_macro_db_indicator(series_id)
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

for indicator in indicators:
    series_id = indicator['series_id']
    db_data = query
    data = [get_latest(ind["series_id"], ind["name"]) for ind in indicators]

cols = st.columns(3) 
for i, metric in enumerate(data):
    with cols[i % 3]:  # Cycle through columns (0,1,2,0,1,2)
        st.metric(
            label=f"{metric['name']} (as of {metric['date']})",
            value= f"{metric['value']:.2f}{'%' if abs(metric['value']) < 100 else ''}",
            help=f"FRED Series: {metric['series_id']}\n\nAnnounced: {metric['announcement_date']}"
        )
        
st.caption("Source: Federal Reserve Economic Data (FRED) | Updated daily")