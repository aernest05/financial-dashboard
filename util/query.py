import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase import create_client, Client
from dotenv import load_dotenv
from util import helpers
import pandas as pd
import datetime
import streamlit as st

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase:Client = create_client(url,key) # type: ignore

def prepare_dataframe_for_supabase(df:pd.DataFrame):
    """Clean and prepare DataFrame for Supabase insertion"""

    df_clean = df.copy()
    df_clean.columns = df_clean.columns.str.lower()
    df_clean = df_clean.rename({"stock splits":"stock_splits"},axis=1)

    df_clean = df_clean.reset_index(drop=True)
    df_clean['date'] = pd.to_datetime(df_clean['date']).dt.strftime("%Y-%m-%d")
    df_clean['volume'] = df_clean['volume'].astype('int64')
    
    numeric_cols = ['open', 'high', 'low', 'close', 'dividends']
    for col in numeric_cols:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    df_clean['stock_splits'] = df_clean['stock_splits'].fillna(0).astype('int64')

    
    return df_clean

def insert_new_stock_to_database(df):
    df_clean = prepare_dataframe_for_supabase(df)
    records = df_clean.to_dict('records')
    supabase.table("stocks").upsert(records).execute()

def update_stock_database(ticker,max_hours=24):
    response = (supabase.table("stocks")
                .select("date")
                .order("date",desc=True)
                .limit(1)
                .execute()
                )
    date = response.data[0]['date']
    date = datetime.datetime.strptime(date,"%Y-%m-%d")
    hours_since_last_update = helpers.check_date(date)

    if hours_since_last_update > max_hours:
        df = helpers.fetch_stock_history(ticker,"5d")

        df_clean = prepare_dataframe_for_supabase(df)

        records = df_clean.to_dict('records')
        response = supabase.table("stocks").upsert(records).execute()

@st.cache_data(ttl=3600)
def read_stock_database(ticker,batch_size=1000) -> pd.DataFrame:
    all_data = []
    offset = 0
    while True:
        response = (supabase.table("stocks")
                    .select("*")
                    .eq("ticker", ticker)
                    .range(offset, offset + batch_size - 1)
                    .execute())

        batch = response.data
        if not batch:  
            break

        all_data.extend(batch)
        print(len(all_data))
        offset += batch_size
    return pd.DataFrame(all_data)

def prepare_fed_for_supabase(df):
    df = df.rename({'realtime_start':'start_date','date':'announcement_date'},axis=1)
    df['start_date'] = pd.to_datetime(df['start_date']).dt.strftime("%Y-%m-%d")
    df['announcement_date'] = pd.to_datetime(df['announcement_date']).dt.strftime("%Y-%m-%d")
    df = df.reset_index(drop=True)
    return df

def insert_fed_to_macro_database(id):
    data = helpers.fetch_macro_history(id)
    df = prepare_fed_for_supabase(data)
    records = df.to_dict('records') # type: ignore
    supabase.table("macro").upsert(records).execute()

def update_macro_database(id,max_hours=24*30):
    response = (supabase.table("macro")
                .select("start_date")
                .order("start_date",desc=True)
                .limit(1)
                .execute()
                )
    date = response.data[0]['start_date']
    date = datetime.datetime.strptime(date,"%Y-%m-%d")
    hours_since_last_update = helpers.check_date(date)

    if hours_since_last_update > max_hours:
        df = helpers.fetch_macro_history(id)
        df_clean = prepare_fed_for_supabase(df)
        records = df_clean.to_dict('records') # type: ignore
        response = supabase.table("macro").upsert(records).execute()

@st.cache_data(ttl=3600)
def read_macro_db_indicator(indicator: str) -> pd.DataFrame:
    response = supabase.rpc("get_latest_macro_by_indicator", {
        "target_indicator": indicator
    }).execute()
    
    return pd.DataFrame(response.data)


