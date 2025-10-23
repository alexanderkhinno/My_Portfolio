from flask import Flask, jsonify
from parser import parse_test_profile, parse_best_solution, parse_profiler_summary
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../dstrut/output")

@app.route("/api/time-profile")
def time_profile():
    path = os.path.join(OUTPUT_PATH, "test_profile.txt")
    data = parse_test_profile(path)
    return jsonify(data)

@app.route("/api/final-results")
def final_results():
    path = os.path.join(OUTPUT_PATH, "best_solution.txt")
    data = parse_best_solution(path)
    return jsonify(data)

@app.route("/api/call-counts")
def call_counts():
    path = os.path.join(OUTPUT_PATH, "profiler_summary.txt")
    data = parse_profiler_summary(path)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
