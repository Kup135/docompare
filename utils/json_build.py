import pandas as pd
import json
import os
import numpy as np
from datetime import datetime


def build_agent3_input_json(df: pd.DataFrame) -> dict:
    return {
        row["field"]: {
            "csv_value": row["csv_value"],
            "image_value": None
        }
        for _, row in df.iterrows()
    }

def wrap_final(fields_dict: dict) -> dict:
    return {
        "comparable_fields": fields_dict,
        "flag": None
    }

def convert_numpy(obj):
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def save_output_json(data: dict, output_dir: str, base_name: str = "comparison") -> str:
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}.json"
    path = os.path.join(output_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=convert_numpy)

    print(f"✅ Output saved to {path}")
    return path