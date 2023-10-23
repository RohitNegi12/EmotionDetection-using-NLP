import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from streamlit.delta_generator import DeltaGenerator
import requests
import jsonpickle
import csv
from typing import List, Generator
from itertools import tee
import math

# Debug
import sys
import logging

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
    fig1, ax1 = plt.subplots(figsize=(4, 4), layout="constrained")
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


def printCharts(data: dict[str, list[float]], stContainers: tuple[DeltaGenerator, ...]):
    logging.info(data)
    width = len(stContainers)
    keys = list(data.keys())
    for i in range(len(data)):
        with stContainers[i % width]:
            st.write(f"Product ID: {keys[i]}")
            drawChart(data[keys[i]])


def getSentimentDictionarySegment(
    scores: dict[str, List[float]], max_charts: int
) -> Generator[dict[str, List[float]], None, None]:
    segment = {}
    i = 0
    for key, row in scores.items():
        segment[key] = row
        i += 1
        if i == max_charts:
            i = 0
            yield segment
            segment.clear()

    if len(segment) > 0:
        yield segment


def analysisHanlder(data, max_charts):
    url = "http://localhost:5000/scores"
    files = {"review_data": ("something", data, "text/csv")}
    response = requests.get(url, files=files)
    scores: dict = jsonpickle.decode(response.text)  # type: ignore
    st.session_state["current_page"] = 1
    st.session_state["total_pages"] = math.ceil(len(scores) / max_charts)
    st.session_state["scores_iterator"] = getSentimentDictionarySegment(
        scores, max_charts
    )


# State Management

if "first_time" not in st.session_state:
    st.session_state["first_time"] = True

if "scores_iterator" not in st.session_state:
    st.session_state["scores_iterator"] = None

if "scores" not in st.session_state:
    st.session_state["scores"] = None

if "current_page" not in st.session_state:
    st.session_state["current_page"] = 0

if "total_pages" not in st.session_state:
    st.session_state["total_pages"] = 0

# Main Page

st.title("Review Analysis")

"Upload your data in .csv format"
st.markdown("Ensure columns are labelled: ```product_id, review```")

col_decision = st.empty()

no_of_columns = int(col_decision.number_input("Enter no. of columns", 2, 6, 2, 1, "%d"))

data = st.file_uploader(label="Review Data", type=["csv"])

pie_chart_columns = tuple(st.columns(no_of_columns))

btn_space = st.empty()

btn_get_analysis = btn_space.button("Get Analysis")

if btn_get_analysis and data is not None:
    col_decision.empty()
    col_decision.write(f"No. of columns: {no_of_columns}")
    analysisHanlder(data, 20)


if st.session_state["scores_iterator"] is not None:
    btn_space.empty()
    if st.session_state["first_time"]:
        try:
            st.session_state["scores"] = next(st.session_state["scores_iterator"])
            printCharts(st.session_state["scores"], pie_chart_columns)
        except:
            logging.warning("No data received")
        st.session_state["first_time"] = False
        # printCharts(next(st.session_state["scores_iterator"]), pie_chart_columns)

    next_page = btn_space.button("Next page")
    if next_page:
        try:
            st.session_state["scores"] = next(st.session_state["scores_iterator"])
            st.session_state["current_page"] += 1
            printCharts(st.session_state["scores"], pie_chart_columns)
        except:
            pass

    if st.session_state["current_page"] == st.session_state["total_pages"]:
        btn_space.empty()

if st.session_state["current_page"] > 0:
    st.write("Page {}".format(st.session_state["current_page"]))

st.write(st.session_state)
