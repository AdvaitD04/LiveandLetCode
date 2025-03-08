import React, { useState } from "react";
import axios from "axios";

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) {
      alert("Please select a WAV file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("audio", file);

    setLoading(true);
    setError(null);
    try {
      const response = await axios.post("http://127.0.0.1:5000/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setResult(response.data);
    } catch (error) {
      console.error("Error:", error);
      setError("An error occurred while analyzing the file. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl">
            Audio Sentiment Analysis
          </h1>
          <p className="mt-4 text-lg text-gray-600">
            Upload a WAV file to analyze its sentiment and get a transcription.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-2xl p-8 sm:p-10">
          <div className="text-center">
            <label
              htmlFor="audioFile"
              className="cursor-pointer inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-300"
            >
              <span>Choose a WAV File</span>
              <input
                type="file"
                id="audioFile"
                accept=".wav"
                onChange={handleFileUpload}
                className="sr-only"
              />
            </label>
            <p className="mt-2 text-sm text-gray-500">
              Supported format: .wav
            </p>
          </div>

          {loading && (
            <div className="mt-8 flex justify-center">
              <div className="animate-spin h-10 w-10 border-4 border-indigo-500 rounded-full border-t-transparent"></div>
            </div>
          )}

          {error && (
            <div className="mt-8 bg-red-50 p-4 rounded-lg text-red-700 text-center">
              {error}
            </div>
          )}

          {result && (
            <div className="mt-8 space-y-6">
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-900">
                  Transcription
                </h3>
                <p className="mt-2 text-gray-700">{result.transcription}</p>
              </div>

              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-900">
                  Sentiment Analysis
                </h3>
                <div className="mt-4 space-y-4">
                  <div>
                    <p className="text-gray-700">
                      Overall Sentiment:{" "}
                      <span className="font-semibold text-indigo-600">
                        {result.sentiment_analysis.overall_sentiment}
                      </span>
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-700">
                      Sentiment Score:{" "}
                      <span className="font-semibold text-indigo-600">
                        {JSON.stringify(
                          result.sentiment_analysis.sentiment_score
                        )}
                      </span>
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-700">
                      Polarity:{" "}
                      <span className="font-semibold text-indigo-600">
                        {result.sentiment_analysis.polarity}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;     