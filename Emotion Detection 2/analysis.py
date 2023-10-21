from typing import TextIO
import pandas as pd
import numpy as np
import json

from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax

# Server

from flask import Flask, request
from markupsafe import escape

# Pretrained Model

MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)


def preprocess(text: str) -> str:
    new_text = []

    for t in text.split(" "):
        t = "@user" if t.startswith("@") and len(t) > 1 else t
        t = "http" if t.startswith("http") else t
        new_text.append(t)
    return " ".join(new_text)


def roberta_analyze(sentence: str) -> np.ndarray:
    processed_sentence = preprocess(sentence)
    encoded_text = tokenizer(
        processed_sentence, return_tensors="pt", truncation=True, max_length=50
    )
    output = model(**encoded_text)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores).tolist()
    return scores


def getScores(data_file: TextIO) -> dict[str, list[float]]:
    df = pd.read_csv(data_file, escapechar="\\", skipinitialspace=True)
    df.sort_values(by="product_id", inplace=True)
    df.set_index(keys=["product_id"], drop=False, inplace=True)
    products = df["product_id"].unique().tolist()
    result: dict[str, list[float]] = {}
    for product in products:
        prod_df = df.loc[df["product_id"] == product]
        scores = []
        for _, row in prod_df.iterrows():
            scores.append(roberta_analyze(row["review"]))
        scores = np.average(scores, axis=0)
        result[product] = scores.tolist()
    return result


# with open("./dummy_data.csv") as data_file:
#     final_result = getScores(data_file=data_file)
#     for key, val in final_result.items():
#         print(key)
#         print(val)
#         print()

# Server Code
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/scores", methods=["GET"])
def greet():
    uploaded_file = request.files["review_data"]
    data_file = uploaded_file.read()  # Bytes
    with open("test_file.csv", "wb") as test_file:
        test_file.write(data_file)
    with open("test_file.csv", "r") as test_file:
        scores = json.dumps(getScores(test_file))
        return scores

if __name__ == "__main__":
    app.run()