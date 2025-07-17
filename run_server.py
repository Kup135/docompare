from flask import Flask, request, jsonify, send_from_directory
import os
import yaml
from main import main

app = Flask(__name__, static_folder="frontend", static_url_path="")

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/run", methods=["POST"])
def run_comparison():
    config = request.json
    os.makedirs("config", exist_ok=True)
    with open("config/config.yaml", "w") as f:
        yaml.dump(config, f)

    result_path = main()
    with open(result_path, "r", encoding="utf-8") as f:
        data = f.read()

    return jsonify(yaml.safe_load(data))

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True)
