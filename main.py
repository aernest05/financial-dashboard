import streamlit as st

st.set_page_config(
    page_title="Macro",  # This changes the browser tab title
    layout="wide"
)
st.sidebar.header("My Sidebar Header")  # Smaller than title but still prominent

# Sidebar content
st.sidebar.button("Click me")
st.sidebar.selectbox("Choose an option", ["A", "B", "C"])

st.title("Welcome to My Streamlit App")