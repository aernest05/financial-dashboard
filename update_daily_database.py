from util.query import update_stock_database, update_macro_database
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase:Client = create_client(url,key) # type:ignore

def update_all_stocks_daily():
    response = (supabase.table("stocks")
                    .select("ticker, count()")
                    .execute()
                    )
    for data in response.data:
        ticker = data['ticker']
        update_stock_database(ticker)

def update_all_macro_monthly():
    response = (supabase.table("macro")
                    .select("indicator, count()")
                    .execute()
                    )
    for data in response.data:
        indicator = data['indicator']
        update_macro_database(indicator)

if __name__ == "__main__":
    update_all_stocks_daily()