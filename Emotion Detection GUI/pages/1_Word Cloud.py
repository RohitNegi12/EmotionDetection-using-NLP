import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from streamlit.delta_generator import DeltaGenerator
from typing import List, Generator

# Hiding Streamlit watermarks
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Utility Functions


def drawCloud(wc: WordCloud):
    fig, ax = plt.subplots(figsize=(1, 1))
    ax.imshow(wc)
    plt.axis("off")
    st.pyplot(fig)


def printClouds(data: dict[str, WordCloud], stContainers: tuple[DeltaGenerator, ...]):
    width = len(stContainers)
    keys = list(data.keys())
    for i in range(len(data)):
        with stContainers[i % width]:
            st.write(f"Product ID: {keys[i]}")
            drawCloud(data[keys[i]])


def getCloudDictionarySegment(
    clouds: dict[str, WordCloud], max_charts: int
) -> Generator[dict[str, list[float]], None, None]:
    segment = {}
    i = 0
    for key, row in clouds.items():
        segment[key] = row
        i += 1
        if i == max_charts:
            i = 0
            yield segment
            segment.clear()

    if len(segment) > 0:
        yield segment


# Session Management

if "first_time_in_cloud" not in st.session_state:
    st.session_state["first_time_in_cloud"] = True


st.title("Review Analysis")

if not st.session_state["Word Cloud"]:
    "Please upload a file for analysis"
else:
    pie_chart_columns = tuple(st.columns(st.session_state["no_of_columns"]))
    # Incomplete
