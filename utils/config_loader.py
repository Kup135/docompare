import os
from dotenv import load_dotenv
import yaml

# Load .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Load YAML
def load_config(path="config/config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

# Example usage:
if __name__ == "__main__":
    config = load_config()
    print("Tolerance:", config["tolerance"])
    print("Output directory:", config["output_dir"])
    print("API key loaded:", OPENAI_API_KEY is not None)

if __name__ == "__main__":
    config = load_config()
    print(config)