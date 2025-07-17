import openai
import json
from utils.config_loader import OPENAI_API_KEY
from utils.file_loader import encode_image_to_base64
from utils.parser import clean_and_parse_openai_json

openai.api_key = OPENAI_API_KEY

def fill_image_values(agent2_output_json, image_data):
    # Encode image
    encoded_image = encode_image_to_base64(image_data)

    # Prepare prompt
    prompt = (
        "You are a visual data extractor. "
        "You will be given an image (chart, floorplan, or technical document) and a JSON structure. "
        "Your task is to find and fill in the `image_value` for each field based on the image only.\n\n"
        "Only update the 'image_value' — do not change the 'csv_value'. "
        "If a value is missing from the image, use null.\n\n"
        f"Here is the JSON structure:\n{json.dumps(agent2_output_json, indent=2)}"
    )

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You extract numeric or categorical values from images into structured JSON."},
            {"role": "user", "content": prompt},
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
    return clean_and_parse_openai_json(raw_response)
