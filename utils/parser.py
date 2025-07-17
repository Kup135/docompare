import json
import re
import ast


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
    
def fallback_extract_dict_from_code(raw_response):
    """
    Attempts to extract a dictionary assignment from a Python code snippet
    (e.g., 'extraction_expressions = { ... }') and parse it safely using ast.literal_eval.
    """
    try:
        # Extract the last dict literal in the response
        matches = re.findall(r"(\{[\s\S]+?\})", raw_response)
        for match in reversed(matches):
            try:
                parsed = ast.literal_eval(match)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                continue
    except Exception as e:
        print(f"⚠️ Fallback parsing failed: {e}")
    
    return None
