import openai
import json
from utils.config_loader import OPENAI_API_KEY
from utils.parser import clean_and_parse_openai_json, fallback_extract_dict_from_code

openai.api_key = OPENAI_API_KEY

def generate_csv_extraction_code(csv_data, comparable_fields_json):
    csv_text = csv_data.to_csv(index=False)

    prompt = (
        "You are an expert Python data analyst."
        "Your task is to generate a JSON object that maps field names to one-line Python expressions "
        "for extracting values from a pandas DataFrame called `csv_data`.\n\n"
        "Input:\n"
        "- `csv_data`: A DataFrame (already loaded)\n"
        "- A JSON object listing field names to extract\n\n"
        "Output:\n"
        "Return ONLY a raw JSON object — **not a Python script**, **not inside triple backticks**, and with **no explanations**.\n"
        "Each key in the JSON should be a field name, and each value should be a one-line expression "
        "that extracts the value from `csv_data`.\n\n"
        "Example (format only):\n"
        "{\n"
        '  "Room.Living.Area_m2": "csv_data.loc[csv_data[\'Room\'] == \'Living\', \'Area_m2\'].values[0]",\n'
        '  "Room.Kitchen.Area_m2": "csv_data.loc[csv_data[\'Room\'] == \'Kitchen\', \'Area_m2\'].values[0]"\n'
        "}\n\n"
        f"Here is the field list:\n{json.dumps(comparable_fields_json, indent=2)}"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You generate Python code to extract specific values from a pandas DataFrame."},
                {"role": "user", "content": prompt},
                {"role": "user", "content": f"Here is the CSV data:\n{csv_text}"}
            ],
            temperature=0.2
        )
    except openai.error.OpenAIError as e:
        raise RuntimeError(f"OpenAI API call failed in Agent 2: {e}")

    raw_response = response.choices[0].message.content
    parsed = clean_and_parse_openai_json(raw_response)
    if parsed is None:
        print("⚠️ Trying fallback parsing...")
        parsed = fallback_extract_dict_from_code(raw_response)
    
    if parsed is None:
        raise ValueError("Agent 2 returned invalid or unparsable JSON.")

    return parsed
