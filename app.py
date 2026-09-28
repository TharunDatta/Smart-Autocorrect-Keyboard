from pathlib import Path

from flask import Flask, jsonify, render_template, request

from autocorrect import AutoCorrect
from evaluate import evaluate
from predictor import NGramPredictor


app = Flask(__name__)
CORPUS_PATH = Path(__file__).resolve().parent / "data" / "corpus.txt"
predictor = NGramPredictor(CORPUS_PATH)
autocorrect = AutoCorrect(CORPUS_PATH)
MAX_TEXT_LENGTH = 10000


def _text_payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("text"), str):
        return None, (jsonify({"error": "text must be a string"}), 400)
    text = data["text"]
    if len(text) > MAX_TEXT_LENGTH:
        return None, (jsonify({"error": "text is too long (10,000 characters max)"}), 413)
    return data, None


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/overview")
def overview():
    diagnostic = evaluate(CORPUS_PATH)
    return jsonify({
        "corpus_words": sum(predictor.unigrams.values()),
        "unique_words": len(predictor.unigrams),
        "bigrams": len(predictor.bigrams),
        "trigrams": len(predictor.trigrams),
        "evaluation": diagnostic,
    })


@app.post("/predict")
def predict():
    data, error = _text_payload()
    if error:
        return error
    return jsonify({"suggestions": predictor.predict(data["text"], 5)})


@app.post("/autocorrect")
def autocorrect_text():
    data, error = _text_payload()
    if error:
        return error
    text = data["text"]
    corrected = autocorrect.correct_sentence(text)
    cursor = data.get("cursor")
    if cursor is not None:
        if isinstance(cursor, bool) or not isinstance(cursor, int) or not 0 <= cursor <= len(text):
            return jsonify({"error": "cursor must be an integer within text"}), 400
        corrected_cursor = len(autocorrect.correct_sentence(text[:cursor]))
    else:
        corrected_cursor = None
    return jsonify({"corrected": corrected, "cursor": corrected_cursor})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
