import yfinance as yf
import pandas as pd


def needs_update(db_data, max_age_hours=24):
    """
    Check if database records are too old and need refreshing.
    
    Args:
        db_data (DataFrame): Data loaded from your database
        max_age_hours (int): Maximum allowed age of data in hours
        
    Returns:
        bool: True if data needs update, False otherwise
    """
    if db_data.empty:
        return True
        
    # Get most recent date in your database
    latest_date = pd.to_datetime(db_data['date']).max()
    
    # Compare with current time
    data_age_hours = (pd.Timestamp.now(tz='Asia/Jakarta') - latest_date).total_seconds() / 3600
    
    return data_age_hours > max_age_hours


def fetch_stock_history(ticker,period):
    ticker_data = yf.Ticker(f"{ticker}.JK")
    hist = ticker_data.history(period=period)
    df = hist.reset_index()
    df.insert(0, 'ticker', f'{ticker}.JK')
    return df

# def fetch_macro_history():



def resampler(df,time_range):
    resampling_rules = {
        "3 Months": 'W',  # Weekly for 3 months
        "6 Months": '2W', # Bi-weekly for 6 months
        "1 Year": 'M',    # Monthly for 1 year
        "5 Year": '3M'    # Quarterly for 5 years
    }
    rule = resampling_rules.get(time_range)
    if rule:
        df = df.resample(rule,on='date',label='left').last()
        print(df.index)
        return df.reset_index()
    else:
        return df

def read_stocks_db(conn,ticker,start_date):
    db_data = pd.read_sql(f"""
    SELECT * FROM stocks
    WHERE ticker = ? AND date >= ?
    ORDER BY date ASC
""",conn,params=(f'{ticker}.JK', f'{start_date}'))
    return db_data

def read_macro_db(conn):
    db_data = pd.read_sql("""
    SELECT indicator, 
    MAX(start_date) AS latest_date
    FROM macro;
    GROUP BY indicator
    """,conn)
    db_data 
    return db_data

def read_macro_db_indicator(conn,indicator):
    db_data = pd.read_sql("""
    WITH Ranked AS (
    SELECT 
        indicator,
        start_date,
        value,
        announcement_date,
        ROW_NUMBER() OVER (
            PARTITION BY start_date 
            ORDER BY announcement_date DESC
        ) AS rn
    FROM macro
    WHERE indicator = ?
)
SELECT 
    indicator,
    start_date,
    value,
    announcement_date
FROM Ranked
WHERE rn = 1
ORDER BY start_date DESC;
    """,conn,params=(indicator,))
        
    return db_data
    

#         period_dict = {
#     "1 Week": today - timedelta(days=7),
#     "1 Month": today - timedelta(days=30),
#     "3 Months": today - timedelta(days=90),
#     "6 Months": today - timedelta(days=180),
#     "1 Year": today - timedelta(days=365),
#     "5 Year": today - timedelta(days=365*5)
# }