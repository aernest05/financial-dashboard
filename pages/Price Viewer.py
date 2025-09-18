import streamlit as st
import pandas as pd
from util.helpers import *
from util import query
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Stock Price", # The page title, shown in the browser tab.
    layout="wide", # How the page content should be laid out.
)
st.title("Price Viewer")

col1, col2, col3= st.columns(3)

with col1:
    selected_category = st.selectbox(
    "Select Market Category:",
    ["Indonesian Stocks", "US Stocks", "Market Indexes","Cryptocurrencies"],
    index=0  # Default selection: "US Stocks"
)

with col2:
    if selected_category == "Indonesian Stocks":
        ticker = st.text_input("Enter stock ticker:", value="BBCA")
        ticker += '.JK'
    elif selected_category == "US Stocks":
        pass
        # ticker = st.text_input("Enter stock ticker:", value="AAPL")
    elif selected_category == "Market Indexes":
        index_option = st.selectbox(
            "Select an Index:",
            ["IHSG (Jakarta Composite)", "IDX30 (LQ45 might be ^JKSE70)", "S&P 500", "NASDAQ", "Dow Jones"],
            index=0
        )
        
        if index_option == "IHSG (Jakarta Composite)":
            ticker = "^JKSE"
        elif index_option == "S&P 500":
            ticker = "^GSPC"
        elif index_option == "NASDAQ":
            ticker = "^IXIC"
        elif index_option == "Dow Jones":
            ticker = "^DJI"
    elif selected_category == "Cryptocurrencies":
        option = st.selectbox(
            "Select Cryptocurrencies",
            ["Bitcoin (BTC-USD)", "Ethereum (ETH-USD)", "Binance Coin (BNB-USD)"],
            index=0
        )
        ticker_map = {
        "Bitcoin (BTC-USD)": "BTC-USD",
        "Ethereum (ETH-USD)": "ETH-USD",
        "Binance Coin (BNB-USD)": "BNB-USD",
        }
        ticker = ticker_map[option]
        
with col3:
    period = st.selectbox(
        "Select Time Period:",
        ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year","5 Year","Max"],
        index=1
    )

today = datetime.now()
period_dict = {
    "1 Week": today - timedelta(days=7),
    "1 Month": today - timedelta(days=30),
    "3 Months": today - timedelta(days=90),
    "6 Months": today - timedelta(days=180),
    "1 Year": today - timedelta(days=365),
    "5 Year": today - timedelta(days=365*5),
    "Max":None
}
if period == "Max":
    start_date = None
else:
    start_date = period_dict[period].strftime('%Y-%m-%d')

db_data = query.read_stock_database(ticker)

if db_data.empty:  # 1=1 placeholder for debugging
    new_data = fetch_stock_history(ticker)
    
    if not new_data.empty:
        query.insert_new_stock_to_database(new_data)
        db_data = query.prepare_dataframe_for_supabase(new_data)

if not db_data.empty:
    db_data['date'] = pd.to_datetime(db_data['date'])
    if start_date:
        db_data = db_data[db_data['date'] >= pd.to_datetime(start_date)]
    db_data = resampler(db_data,period)

ticker_header = ticker.strip('^')
st.subheader(f"{ticker_header} Stock Price ({today.strftime("%b %Y")})")

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
    

