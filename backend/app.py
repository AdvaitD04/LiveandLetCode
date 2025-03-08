from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from werkzeug.utils import secure_filename
import os
import mimetypes
from flask_cors import CORS
from pyAudioAnalysis import audioSegmentation as aS
import numpy as np

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"wav"}

def allowed_file(filename):
    """Check if the uploaded file is a WAV file."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files["audio"]

    if not allowed_file(audio_file.filename):
        return jsonify({"error": "Invalid file format. Please upload a WAV file."}), 400

    filename = secure_filename(audio_file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    audio_file.save(file_path)

    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type != "audio/wav":
        return jsonify({"error": "Invalid file format. Please upload a valid WAV file."}), 400

    # Speaker Diarization
    try:
        segments = aS.speaker_diarization(file_path, n_speakers=2)
        print("Segments:", segments)  # Debugging: Print the segments
    except Exception as e:
        return jsonify({"error": f"Speaker diarization failed: {str(e)}"}), 500

    # Check the structure of segments
    if not isinstance(segments, tuple) or len(segments) != 3:
        return jsonify({"error": "Unexpected output format from speaker diarization."}), 500

    speaker_labels = segments[0]  # Array of speaker labels
    segment_duration = 1.0  # Assume each label corresponds to 1 second (adjust as needed)

    recognizer = sr.Recognizer()
    results = []

    for i, label in enumerate(speaker_labels):
        start = i * segment_duration
        end = (i + 1) * segment_duration

        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source, duration=end - start, offset=start)
            try:
                text = recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                text = "Could not understand audio"
            except sr.RequestError:
                text = "Error with Speech Recognition API"

        analyzer = SentimentIntensityAnalyzer()
        sentiment_scores = analyzer.polarity_scores(text)
        sentiment_polarity = TextBlob(text).sentiment.polarity
        sentiment = (
            "Positive" if sentiment_polarity > 0 else "Sad" if sentiment_polarity < 0 else "Neutral"
        )

        results.append({
            "speaker": f"Speaker {int(label) + 1}",  # Convert label to int and add 1 for readability
            "transcription": text,
            "sentiment_analysis": {
                "sentiment_score": sentiment_scores,
                "polarity": sentiment_polarity,
                "overall_sentiment": sentiment
            }
        })

    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(debug=True)