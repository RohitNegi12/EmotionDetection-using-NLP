import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from streamlit.delta_generator import DeltaGenerator
import requests
import json

st.set_page_config(page_title="Review Analysis", page_icon="🧪", layout="wide")

# Hiding Streamlit watermarks
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Functions


def drawChart(scores: list[float]):
    labels = ["Negative", "Neutral", "Positive"]

    # Pie Chart
    fig1, ax1 = plt.subplots()
    ax1.pie(
        scores,
        labels=labels,
        colors=("#D23245", "#2E8FBB", "#3EAE45"),
        autopct="%.1f%%",
        shadow=True,
        startangle=90,
    )
    ax1.axis("equal")
    st.pyplot(fig1)


@st.cache_data
def getDataFrames(numberOfFrames: int = 2):
    testFrames = []
    for _ in range(numberOfFrames):
        dummyData = np.random.rand(10, 3)
        # Normalize the dummy data so that each row adds up to 1.0
        dummyData = dummyData / dummyData.sum(axis=1, keepdims=True)
        testFrame = pd.DataFrame(
            data=dummyData, columns=["roberta_neg", "roberta_neu", "roberta_pos"]
        )
        testFrames.append(testFrame)
    return testFrames


def printCharts(data: dict[str, list[float]], stContainers: tuple[DeltaGenerator, ...]):
    width = len(stContainers)
    keys = list(data.keys())
    for i in range(len(data)):
        with stContainers[i % width]:
            st.write(f"Product ID: {keys[i]}")
            drawChart(data[keys[i]])


# Main Page

st.title("Review Analysis")

inputArea = st.empty()

left_col, right_col = st.columns(2)

with inputArea.container():
    "Upload your data in .csv format"
    st.markdown("Ensure columns are labelled: ```product_id, review```")
    data = st.file_uploader(label="Review Data", type=["csv"])
    if st.button("Get Analysis", "test_button") and data is not None:
        url = "http://localhost:5000/scores"
        files = {"review_data": ("something", data, "text/csv")}
        response = requests.get(url, files=files)
        results = json.loads(response.text)
        printCharts(results, (left_col, right_col))
