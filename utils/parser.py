import json
import re

def clean_and_parse_openai_json(raw_response):
    """
    Removes markdown-style code blocks (e.g., ```json ... ```) from OpenAI output
    and parses it into a Python dict.
    """
    if not isinstance(raw_response, str):
        return None

    # Remove surrounding triple backticks and optional 'json' hint
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_response.strip())
    cleaned = match.group(1).strip() if match else raw_response.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("⚠️ Could not parse JSON from cleaned response.")
        print(cleaned)
        return None