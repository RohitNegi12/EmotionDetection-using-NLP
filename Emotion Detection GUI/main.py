import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from streamlit.delta_generator import DeltaGenerator
import requests
import jsonpickle
import csv
from typing import List, Iterator

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


def getSentimentData(sent_dict: dict):
    with open("res_scores.csv", "r") as res_scores:
        reader = csv.DictReader(sent_dict)


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
) -> Iterator[dict[str, List[float]]]:
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


def checkToDisable(
    gen: Iterator[dict[str, List[float]]], btn_space_to_disable: DeltaGenerator
):
    try:
        print("Check Function", next(gen))
    except:
        btn_space_to_disable.empty()


# State Management

if "scores_set" not in st.session_state:
    st.session_state["scores_set"] = False

if "scores_val" not in st.session_state:
    st.session_state["scores_val"] = dict()

if "scores_segment" not in st.session_state:
    st.session_state["scores_segment"] = {"is_set": False, "segment": dict()}

if "scores_iterator" not in st.session_state:
    st.session_state["score_iterator"] = None

# Main Page

st.title("Review Analysis")

"Upload your data in .csv format"
st.markdown("Ensure columns are labelled: ```product_id, review```")

col_decision = st.empty()

with col_decision:
    no_of_columns = int(st.number_input("Enter no. of columns", 2, 6, 2, 1, "%d"))

data = st.file_uploader(label="Review Data", type=["csv"])

pie_chart_container = st.empty()

with pie_chart_container:
    pie_chart_columns = tuple(st.columns(no_of_columns))

btn_space = st.empty()
btn_get_analysis = btn_space.button("Get Analysis")

if btn_get_analysis and data is not None:
    # col_decision.write(f"No. of columns: {no_of_columns}")

    url = "http://localhost:5000/scores"
    files = {"review_data": ("something", data, "text/csv")}
    response = requests.get(url, files=files)
    scores: dict = jsonpickle.decode(response.text)  # type: ignore

    st.session_state["scores_set"] = True
    st.session_state["scores_val"] = scores

if data is None and st.session_state["scores_set"] == True:
    st.session_state["scores_set"] = False
    st.session_state["scores_val"] = st.session_state["scores_val"].clear()

if st.session_state["scores_set"] == True:
    scores = st.session_state["scores_val"]
    btn_space.empty()

    if not st.session_state["scores_segment"]["is_set"]:
        st.session_state["scores_iterator"] = getSentimentDictionarySegment(scores, 1)
        st.session_state["scores_segment"]["is_set"] = True

if st.session_state["scores_segment"]["is_set"]:
    with pie_chart_container:
        printCharts(st.session_state["scores_segment"]["segment"], pie_chart_columns)

    # printCharts(scores, tuple(st.columns(no_of_columns)))
    # printCharts(next(score_iterator), pie_chart_columns)
    btn_next_page = btn_space.button("Next page")

    if btn_next_page:
        try:
            printCharts(next(st.session_state["scores_iterator"]), pie_chart_columns)
        except:
            btn_space.empty()

st.write(st.session_state)