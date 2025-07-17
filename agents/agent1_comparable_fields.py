import openai
import io
import pandas as pd
import base64
import re
import json

from utils.file_loader import encode_image_to_base64
from utils.parser import clean_and_parse_openai_json
from utils.config_loader import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_comparable_fields(csv_data, image_data):
    csv_text = csv_data.to_csv(index=False)

    encoded_image = encode_image_to_base64(image_data)

    # prompt = (
    #     "You are a document comparison assistant, specialized in comparing tabular data and the way it is documented in image, for the construction industry. "
    #     "Given a CSV file and an image, your job is to find fields that appear in both. Use reasoning to identify comparable fields, even if they'd require some simple data analytics processes like filtering, grouping, or aggregating data.\n\n"
    #     "Return a JSON with two fields:\n"
    #     "- 'comparable_fields': a list of the matching items (like 'room name', 'area', 'cost')\n"
    #     "- 'flag': set to null for now.\n\n"
    #     "Be specific, structured, and helpful."
    # )

    prompt = ( "You are a document comparison assistant specialized in the AEC industry. "
    "Given two documents — one structured (like a CSV) and one unstructured (like an image with charts or technical drawings) — "
    "your job is to determine what pieces of information appear in both and can be compared.\n\n"

    "Your output must be a JSON object with:\n"
    "- 'comparable_fields': a list of field descriptions that match between the two documents. "
    "Include nested categories or groupings if present (per field - e.g., per category, per section, per column, per row). "
    "Structure the field names to reflect this hierarchy if it exists.\n"
    "- 'flag': leave this as null.\n\n"

    "Think carefully about the structure in both files. Identify if there are repeated patterns, categories, or sections that can be aligned." \
    )

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for comparing document contents."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": "Here is the CSV:"},
            {"role": "user", "content": csv_text},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Here is the image file:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
                ]
            }
        ],
        temperature=0.2
    )

    raw_response = response.choices[0].message.content
    print("DEBUG: OpenAI response:\n", raw_response)
    clean_response = clean_and_parse_openai_json(raw_response)
    print("DEBUG: clean response:", (clean_response))

    return clean_response