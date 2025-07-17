import openai
import json
from utils.config_loader import OPENAI_API_KEY
from utils.parser import clean_and_parse_openai_json

openai.api_key = OPENAI_API_KEY

def generate_csv_extraction_code(csv_data, comparable_fields_json):
    csv_text = csv_data.to_csv(index=False)

    prompt = (
        "You are an expert Python data analyst. Your job is to write code snippets "
        "that extract values from a pandas DataFrame (`csv_data`) for a set of comparison fields.\n\n"
        "Input:\n"
        "- A CSV file as text (you can assume it has already been read into `csv_data` as a pandas DataFrame)\n"
        "- A JSON object with a list of field names (keys) that describe the values to extract\n\n"
        "Output:\n"
        "Return a JSON object where each key is the field name, and the value is a one-line Python expression "
        "that would extract the matching value from `csv_data`. "
        "Use pandas filtering, indexing, or aggregation as needed.\n\n"
        "Here is the field list:\n"
        f"{json.dumps(comparable_fields_json, indent=2)}"
    )

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You generate Python code to extract specific values from a pandas DataFrame."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": f"Here is the CSV data:\n{csv_text}"}
        ],
        temperature=0.2
    )

    raw_response = response.choices[0].message.content
    return clean_and_parse_openai_json(raw_response)
