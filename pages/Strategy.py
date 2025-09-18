import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.title("Strategy Tester")

# Input section
col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input("Enter stock ticker:", value="BBCA")

with col2:
    ma_short = st.number_input("Short MA Period", min_value=1, value=5)

with col3:
    ma_long = st.number_input("Long MA Period", min_value=1, value=20)

# Get data
conn = sqlite3.connect('financial_data.db')
df = pd.read_sql(f"""
    SELECT date, close FROM stocks 
    WHERE ticker = ? 
    ORDER BY date ASC
""", conn, params=(f'{ticker}.JK',))
conn.close()

if not df.empty:
    # Calculate moving averages
    df['MA_short'] = df['close'].rolling(window=ma_short).mean()
    df['MA_long'] = df['close'].rolling(window=ma_long).mean()
    
    # Generate signals
    df['Signal'] = 0
    df['Signal'] = np.where(df['MA_short'] > df['MA_long'], 1, 0)
    df['Position'] = df['Signal'].diff()
    
    # Calculate returns
    df['Returns'] = df['close'].pct_change()
    df['Strategy_Returns'] = df['Signal'] * df['Returns']
    
    # Calculate cumulative returns
    df['Cum_Market_Returns'] = (1 + df['Returns']).cumprod()
    df['Cum_Strategy_Returns'] = (1 + df['Strategy_Returns']).cumprod()

    st.write(df)
    
    # Plotting
    fig = go.Figure()
    
    # Price and MA lines
    fig.add_trace(go.Scatter(x=df['date'], y=df['close'], name='Price'))
    fig.add_trace(go.Scatter(x=df['date'], y=df['MA_short'], name=f'MA{ma_short}'))
    fig.add_trace(go.Scatter(x=df['date'], y=df['MA_long'], name=f'MA{ma_long}'))
    
    # Buy/Sell signals
    buy_signals = df[df['Position'] == 1]
    sell_signals = df[df['Position'] == -1]
    
    fig.add_trace(go.Scatter(
        x=buy_signals['date'],
        y=buy_signals['close'],
        mode='markers',
        name='Buy Signal',
        marker=dict(symbol='triangle-up', size=10, color='green')
    ))
    
    fig.add_trace(go.Scatter(
        x=sell_signals['date'],
        y=sell_signals['close'],
        mode='markers',
        name='Sell Signal',
        marker=dict(symbol='triangle-down', size=10, color='red')
    ))
    
    fig.update_layout(
        title=f"{ticker} Price and Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_trades = len(buy_signals) + len(sell_signals)
        st.metric("Total Trades", total_trades)
    
    with col2:
        market_return = (df['Cum_Market_Returns'].iloc[-1] - 1) * 100
        st.metric("Market Return", f"{market_return:.2f}%")
    
    with col3:
        strategy_return = (df['Cum_Strategy_Returns'].iloc[-1] - 1) * 100
        st.metric("Strategy Return", f"{strategy_return:.2f}%")
    
else:
    st.error("No data available for the selected ticker")