import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from streamlit.delta_generator import DeltaGenerator
from typing import Generator
import math

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


def initializeStates():
    st.session_state["cloud_current_page"] = 1
    st.session_state["cloud_total_pages"] = math.ceil(
        len(st.session_state["word_clouds"]) / st.session_state["max_charts"]
    )
    st.session_state["cloud_iterator"] = getCloudDictionarySegment(
        st.session_state["word_clouds"], st.session_state["max_charts"]
    )
    st.session_state["wc_segment"] = next(st.session_state["cloud_iterator"])


# Session Management

if "first_time_in_cloud" not in st.session_state:
    st.session_state["first_time_in_cloud"] = True

if "cloud_iterator" not in st.session_state:
    st.session_state["cloud_iterator"] = None

if "cloud_current_page" not in st.session_state:
    st.session_state["cloud_current_page"] = 0

if "cloud_total_pages" not in st.session_state:
    st.session_state["cloud_total_pages"] = 0

if "word_clouds" not in st.session_state:
    st.session_state["word_clouds"] = None

if "wc_segment" not in st.session_state:
    st.session_state["wc_segment"] = None


st.title("Review Analysis")

if not st.session_state["word_clouds"]:
    "Please upload a file for analysis"
else:
    wc_columns = tuple(st.columns(st.session_state["no_of_columns"]))
    if st.session_state["first_time_in_cloud"]:
        initializeStates()
        st.session_state["first_time_in_cloud"] = False

    btn_space = st.empty()
    next_page = btn_space.button("Next page")
    if next_page:
        st.session_state["wc_segment"] = next(st.session_state["cloud_iterator"])
        st.session_state["cloud_current_page"] += 1

    printClouds(st.session_state["wc_segment"], wc_columns)

    if st.session_state["cloud_current_page"] == st.session_state["cloud_total_pages"]:
        btn_space.empty()

if st.session_state["cloud_current_page"] > 0:
    st.write("Page {}".format(st.session_state["cloud_current_page"]))
