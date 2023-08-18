import streamlit as st

st.set_page_config(page_title="Review Analysis", page_icon="🧪")
st.title("Review Analysis")

left_col, right_col = st.columns(2)

with left_col:
    st.write("This is the left column")

with right_col:
    st.write("This is the right column")