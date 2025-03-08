from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from werkzeug.utils import secure_filename
import os
import mimetypes
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"           
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"wav"}   


def allowed_file(filename):
    """ Check if the uploaded file is a WAV file """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files["audio"]

    # Check if file has a valid WAV extension
    if not allowed_file(audio_file.filename):
        return jsonify({"error": "Invalid file format. Please upload a WAV file."}), 400

    filename = secure_filename(audio_file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    audio_file.save(file_path)

    # Validate MIME Type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type != "audio/wav":
        return jsonify({"error": "Invalid file format. Please upload a valid WAV file."}), 400

    # Speech Recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            text = "Could not understand audio"
        except sr.RequestError:
            text = "Error with Speech Recognition API"

    # Sentiment Analysis
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)
    sentiment_polarity = TextBlob(text).sentiment.polarity
    sentiment = (
        "Positive" if sentiment_polarity > 0 else "Sad" if sentiment_polarity < 0 else "Neutral"
    )

    return jsonify({
        "transcription": text,
        "sentiment_analysis": {
            "sentiment_score": sentiment_scores,
            "polarity": sentiment_polarity,
            "overall_sentiment": sentiment
        }
    })


if __name__ == "__main__":
    app.run(debug=True)