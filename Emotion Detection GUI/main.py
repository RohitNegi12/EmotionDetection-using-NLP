import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from streamlit.delta_generator import DeltaGenerator

st.set_page_config(page_title="Review Analysis", page_icon="🧪")

# Functions


def getHighestSentimentLabel(df):
    explode = [0.0] * 3
    explode[df.argsort()[-1]] = 0.1
    return explode


def drawChart(df: pd.DataFrame):
    labels = ["Negative", "Neutral", "Positive"]
    test = df[["roberta_neg", "roberta_neu", "roberta_pos"]].mean()  # Pandas Series
    avg_sentiments = [i for i in test]

    # Pie Chart
    fig1, ax1 = plt.subplots()
    ax1.pie(
        avg_sentiments,
        labels=labels,
        colors=("#D23245", "#2E8FBB", "#3EAE45"),
        autopct="%.1f%%",
        explode=getHighestSentimentLabel(test),
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


def printCharts(frames: list[pd.DataFrame], stContainers: tuple[DeltaGenerator, ...]):
    width = len(stContainers)
    for i in range(len(frames)):
        with stContainers[i % width]:
            st.write(f"Product {i+1}")
            drawChart(frames[i])


def updateNumberOfFrames(num: int) -> None:
    st.session_state.numberOfFrames = num


# Session States
if "numberOfFrames" not in st.session_state:
    st.session_state.numberOfFrames = None

# Main Page

st.title("Review Analysis")


inputArea = st.empty()

left_col, right_col = st.columns(2)

with inputArea.container():
    numberOfFrames: int = int(
        st.number_input(
            "Enter number of dummy products (2 - 10)", 2, 10, 2, 1, "%d", "test_input"
        )
    )
    if st.button("Get Analysis", "test_button"):
        st.session_state.numberOfFrames = numberOfFrames

if st.session_state.numberOfFrames is not None:
    printCharts(getDataFrames(st.session_state.numberOfFrames), (left_col, right_col))
