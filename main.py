import streamlit as st

# --- PAGE SETUP ---
page_price = st.Page(
    "pages/Price Viewer.py",
    title="Stock Market",# from Material Design by Google
    default=True,
)

page_strategy = st.Page(
    "pages/Strategy.py",
    title="Strategy", # from Material Design by Google
)


page_financials = st.Page(
    "pages/Macro.py",
    title="Macro", # from https://fonts.google.com/icons
)

pg = st.navigation(pages=[page_price,page_strategy,page_financials])


# --- RUN NAVIGATION ---
pg.run()