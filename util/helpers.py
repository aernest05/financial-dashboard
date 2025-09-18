import yfinance as yf
import pandas as pd
from fredapi import Fred
import streamlit as st
import datetime
from dotenv import load_dotenv
import os
load_dotenv()

fredapi_key = os.getenv("FREDAPI_KEY")

def check_date(latest_date):
    date = (pd.Timestamp.now() - latest_date).total_seconds() / 3600
    return date

@st.cache_data(ttl=3600)
def fetch_stock_history(ticker,period="max"):
    ticker_data = yf.Ticker(ticker)
    hist = ticker_data.history(period=period)
    df = hist.reset_index()
    df.insert(0, 'ticker', ticker)
    return df

def fetch_macro_history(id,method='as_of_date'):
    fred = Fred(api_key=fredapi_key)
    latest_time = datetime.datetime.now()

    if method == 'as_of_date':
        fred_data = fred.get_series_as_of_date(id,latest_time.strftime("%m/%d/%Y")).dropna()
        fred_data['realtime_start'] = pd.to_datetime(fred_data['realtime_start']).dt.date
        fred_data['date'] = pd.to_datetime(fred_data['date']).dt.date
        fred_data.insert(0,'indicator', id)
    elif method == 'get_series': 
        fred_data = fred.get_series(id,latest_time.strftime("%m/%d/%Y")).dropna()
    return fred_data  

def resampler(df,time_range):
    resampling_rules = {

        "3 Months": 'W',  # Weekly for 3 months
        "6 Months": '2W', # Bi-weekly for 6 months
        "1 Year": '2W',    # Monthly for 1 year
        "5 Year": '1M',   # Quarterly for 5 years
        "Max": '1M'
    }
    rule = resampling_rules.get(time_range)
    if rule:
        df = df.resample(rule,on='date',label='left').last()
        return df.reset_index()
    else:
        return df

