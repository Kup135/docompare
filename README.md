# Docompare: Multimodal Document Comparison Engine

A generic comparison engine that verifies whether two documents — one structured (e.g., CSV) and one unstructured (e.g., image) — contain equivalent information. Designed for use cases in construction submittal validation.

## Features:
Fields Matching (Agent 1) — identifies comparable fields using LLM-based reasoning.
CSV Parsing (Agent 2) — generates and runs Python expressions to extract values from the comparable fields in the tabular data.
Image Values Extraction (Agent 3) — extracts values from the images' comparable fields using OpenAI multimodal LLM vision capabilities.
Diff + Evaluation — computes deltas per each field and flags them tolerance-based pass/fail.

Lightweight UI —input fields and configuration, shows a visual summary of comparison output

### Getting Started
This section walks you through installing dependencies, configuring the project, and running the comparison system. You can either use Git Clone or install with Docker.

1. Clone the repo
Run in terminal:
git clone https://github.com/your-username/docompare.git

2. Set up you OpenAI API Key
Create an .env file at the project root and add in it your API key from OpenAI
OPENAI_API_KEY=sk-...

    To learn more about getting an API key check out OpenAI documentation:
    https://platform.openai.com/api-keys

3. *optional* Configure Default Comparison Parameters:
If you'd like to configure the default comparison parameters, edit config/config.yaml to set:

```
data_dir: data/1               # Folder with input files
output_subdir: results         # Where outputs go
tolerance: 1.0                 # Max diff allowed per field
pass_criteria: all_fields_within_tolerance # can be changed to average_diff_below_tolerance or defined in another way in the utils/data_tools.py apply_pass_fail_flag()
clearCache: true               # (Optional) Force fresh run
```

4. Add Your Files
Inside data/<n>, place:
One .csv file (e.g., structured table)
One .png file (e.g., image or diagram)

Only one of each is supported per run at this point.

5. Choose How to Run
#### Option A: Run with Python (local virtualenv)
in terminal:
```bash 
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
``` 

Then:
`python main.py`  # for CLI
`python run_server.py`  # for UI


#### Option B: Run with Docker (recommended)
Make sure Docker Desktop is running, then:
Build the image (once):

```bash 
docker build -t docompare .
```

To run the comparison engine (main.py):
```bash 
docker run --rm -it \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/results:/app/results \
  --env-file .env \
  docompare
```

To run the UI (Flask):
``` bash
docker run --rm -it -p 5051:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/results:/app/results \
  --env-file .env \
  docompare python run_server.py
```
Then open: http://localhost:5051
You can configure data directory, criteria, and tolerance from the form.


Result after each run are saved to:
data/<n>/results/comparison_result_<timestamp>.json


<details> <summary>📁 <strong>Project Structure</strong> (click to expand)</summary>

🔧 Core Code
├── main.py                      # Pipeline entry point
├── run_server.py               # Flask server for the UI
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker config for containerized use
├── agents/
│   ├── agent1_comparable_fields.py
│   ├── agent2_data_analytics.py
│   └── agent3_fill_Fields.py
├── utils/
│   ├── cache_tools.py
│   ├── config_loader.py
│   ├── data_tools.py
│   ├── file_loader.py
│   ├── json_build.py
│   └── parser.py

🧪 Evaluation
├── evaluation/
│   ├── evaluate_agent1.py
│   ├── evaluate_agents2_3.py
│   └── gen_GT_comparable_fields.py

⚙️ Configuration & Frontend
├── config/
│   ├── config.yaml
│   └── temp_eval_config.*
├── frontend/                   # Static index.html + assets

📂 Input & Output Data
├── data/
│   ├── 1/, 2/, 3/, ...
│   └── Synthetic Source/

📝 Docs & Reports
├── README.md
├── HomeAssignment.pdf
└── system_flow_diagram.pdf
</details>

### Evaluation Tools
To assess system correctness and agent performance, this project includes both manual and automatic evaluation tools. The agents are evaluated each on its own performance, agents 2 and 3 are contigent with the results of agent 1. 

#### Agent 1 (Comparable Field Matching)
A manual script prompts the user to match model-generated fields with ground truth (GT), and computes recall to determine the success in identifying correctly the comparable fields. To run in terminal:

python evaluate_agent1.py

#### Agent 2 (CSV Values) and agent 3 (Image values)
A second script automatically compares predicted vs. GT values for both csv_value (Agent 2 and image_value (Agent 3).

To run in terminal:

python evaluate_agents2_3.py

Evaluates:
Accuracy (within tolerance)
Mean Absolute Error (MAE)

### Assumptions & Notes
- CSV is treated as the primary source of truth; the image is used for validation.
- OpenAI’s multimodal GPT-4o is used for both text and image understanding.
- The system does not perform local visual parsing — the raw image and CSV text are sent directly to the OpenAI API.
- Token limitations are assumed to be negligible for the scope of current document sizes.
- File loading:
    - The system supports comparison between exactly two files per run: one tabular file and one image file.
    - It does not perform automatic file pairing — files are assumed to be placed in matching pairs within each data/<n>/ folder.
    - It assumes files have valid extensions (.png, .csv, etc.) and have not been manually corrupted or renamed inconsistently.
- Comparison Logic:
    - Only fields detected in both files are compared; fields missing in one document are not flagged or handled specially.
    - It assumes all comparable fields in the image are explicitly annotated (e.g., as labels or tags) — it does not infer hidden geometric fields from visual measurement.
- Pass/Fail criteria:
 - Tolerance and criteria can vary by document set and contractual context. They are exposed as user-configurable inputs to support flexibility.
 - Default values reflect the strictest thresholds currently observed in the assignment, but users can override with looser or stricter values as needed.

### Future Work
- Add support for matching and grouping related documents from a large pool using RAG (Retrieval-Augmented Generation) to identify candidate pairs.
- Implement a strategy to detect and handle missing fields or values in one document but not the other.
- Automatically suggest fallback tolerance values based on statistical properties of the dataset (e.g., percentiles and/or interquartile ranges).
- Extend support to additional file types beyond CSV and PNG/JPG/WEBP.
- Enable multi-file comparison, e.g., comparing multiple tables or diagrams and aggregating results (e.g., by standard deviation?).
- Explore extraction of geometric quantities from drawings using computer vision (e.g., pixel counting + annotation-based scaling).
- Add error-handling paths for failures in vision model outputs, including:
    - User feedback mechanisms (e.g., “captcha-style” manual confirmation when fields overlap or are ambiguous).
    - LLM-generated confidence scores per field, triggering user review for low-confidence extractions.
- Consider preprocessing with OCR to improve field detection and reduce hallucination, especially before Agent 1.
- Refactor utility codes for better structure and maintainability.
- Reduce latency by refactoring how JSON structures are passed to the agents (e.g., outside-agent JSON injection).
- Redesign agent architecture to support parallel execution of Agent 2 and Agent 3, eliminating sequential dependency and enabling future extension to additional file types.



