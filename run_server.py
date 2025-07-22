import sys
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

    result = main()

    if isinstance(result, dict) and result.get("flag") == "error":
        print(f"⚠️ Main error: {result['error_message']}")
        return jsonify(result), 400
    
    try:
        with open(result, "r", encoding="utf-8") as f:
            data = f.read()
        return jsonify(yaml.safe_load(data))
    except Exception as e:
        print(f"❌ Failed to read result file: {e}")
        return jsonify({"flag": "error", "error_message": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask server...")
    port = int(sys.argv[-1]) if "--port" in sys.argv else 5000
    app.run(debug=True, host="0.0.0.0", port=port)
