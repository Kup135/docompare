import os
import mimetypes
import pandas as pd
from PIL import Image
import base64
import io

def detect_file_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        return "unknown"
    if mime_type.startswith("image"):
        return "image"
    elif mime_type == "text/csv":
        return "csv"
    else:
        return "unsupported"

def encode_image_to_base64(image_data):
    """
    Convert a PIL Image to a base64 string using its native format if available.
    Falls back to PNG if unknown.
    """
    image_bytes = io.BytesIO()
    image_format = image_data.format if image_data.format else "PNG"
    image_data.save(image_bytes, format=image_format)
    image_bytes.seek(0)
    return base64.b64encode(image_bytes.read()).decode("utf-8")

def load_all_valid_files(data_dir):
    result = {}
    errors = []
    seen_types = set()

    for filename in os.listdir(data_dir):
        path = os.path.join(data_dir, filename)
        if not os.path.isfile(path):
            continue

        file_type = detect_file_type(path)
        if file_type == "unsupported":
            errors.append(f"Unsupported file type: {filename}")
            continue

        if file_type in seen_types:
            errors.append(f"Duplicate file type detected: {file_type} already loaded.")
            continue

        seen_types.add(file_type)

        try:
            if file_type == "csv":
                result["csv_data"] = pd.read_csv(path)
            elif file_type == "image":
                result["image_data"] = Image.open(path)
            print(f"DEBUG: file {path} is loaded as {file_type}_data")
        except Exception as e:
            errors.append(f"Failed to load {filename}: {str(e)}")

    result["errors"] = errors
    return result
