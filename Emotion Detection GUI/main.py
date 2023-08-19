import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Review Analysis", page_icon="🧪")

# Functions


def getHighestSentimentLabel(df):
    explode = [0.0] * 3
    explode[df.argsort()[-1]] = 0.1
    return explode


def drawChart(df):
    labels = ("Negative", "Neutral", "Positive")
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


st.title("Review Analysis")

left_col, right_col = st.columns(2)

with left_col:
    st.write("This is the left column")
    st.write("Product 1")
    testFrame = pd.DataFrame(
        data=((0.6, 0.3, 0.1), (0.6, 0.3, 0.1)),
        columns=("roberta_neg", "roberta_neu", "roberta_pos"),
    )
    drawChart(testFrame)

with right_col:
    st.write("This is the right column")
    st.write("Product 2")
    testFrame = pd.DataFrame(
        data=((0.3, 0.1, 0.6), (0.3, 0.1, 0.6)),
        columns=("roberta_neg", "roberta_neu", "roberta_pos"),
    )
    drawChart(testFrame)
