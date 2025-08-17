import streamlit as st
import pandas as pd
import sqlite3
from utility.util import *
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.title("Stock Price Viewer")

col1, col2 = st.columns(2)

with col1:
    ticker = st.text_input("Enter stock ticker:", value="BBCA")

with col2:
    period = st.selectbox(
        "Select Time Period:",
        ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year","5 Year"],
        index=1
    )

today = datetime.now()
period_dict = {
    "1 Week": today - timedelta(days=7),
    "1 Month": today - timedelta(days=30),
    "3 Months": today - timedelta(days=90),
    "6 Months": today - timedelta(days=180),
    "1 Year": today - timedelta(days=365),
    "5 Year": today - timedelta(days=365*5)
}
start_date = period_dict[period].strftime('%Y-%m-%d')

conn = sqlite3.connect('financial_data.db')
cursor = conn.cursor()

db_data = read_stocks_db(conn,ticker,start_date)

if db_data.empty:  # 1=1 placeholder for debugging
    new_data = fetch_stock_history(ticker,'5y')
    if not new_data.empty:
        new_data.to_sql("temp_stocks", conn, if_exists="replace", index=False)
        conn.execute("""
                INSERT INTO stocks
                SELECT * FROM temp_stocks
            """)
        conn.commit()
elif needs_update(db_data):
    new_data = fetch_stock_history(ticker,'5y')
    latest_date = pd.to_datetime(db_data['date']).max()
    if not new_data.empty:
        new_data.to_sql("temp_stocks", conn, if_exists="replace", index=False)
        conn.execute("""
            INSERT OR IGNORE INTO stocks
            SELECT * FROM temp_stocks
        """)
        conn.commit()
db_data = read_stocks_db(conn,ticker,start_date)
conn.close()


if not db_data.empty:
    db_data['date'] = pd.to_datetime(db_data['date'])
    db_data = resampler(db_data,period)

st.subheader(f"{ticker} Stock Price ({today.strftime("%b %Y")})")

if db_data is None:
    st.error("No data available - ticker may not exist or connection failed")
elif db_data.empty:
    st.warning("No data found for the selected time period")
elif not db_data.empty and all(col in db_data.columns for col in ['date', 'close']):
# Create a plotly figure with custom date format
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=db_data['date'], y=db_data['close'], mode='lines+markers'))

    fig.update_layout(
        xaxis=dict(
            title='Date',
            tickformat='%Y-%m-%d',  
            type='date'
        ),
        yaxis=dict(title='Close Price'),
        hovermode='x'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Waiting for data to load...")  # Show while loading
    st.stop()  # Pause script until data arrives
    

