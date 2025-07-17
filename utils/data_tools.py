import pandas as pd

def safe_eval_snippets(snippet_dict, csv_data):
    results = {}

    for field, code in snippet_dict.items():
        try:
            value = eval(code, {"csv_data": csv_data})
        except Exception as e:
            print(f"⚠️ Error running code for '{field}': {e}")
            value = None
        results[field] = value

    return results

def apply_extraction_expressions(extraction_expressions: dict, csv_data: pd.DataFrame) -> pd.DataFrame:
    """
    Runs each extraction expression on csv_data and returns a new DataFrame
    with one row per comparable field and one column: csv_value.
    """
    results = []

    for field, code in extraction_expressions.items():
        try:
            value = eval(code, {"csv_data": csv_data})
        except Exception as e:
            print(f"⚠️ Failed to evaluate expression for '{field}': {e}")
            value = None
        results.append({"field": field, "csv_value": value})

    return pd.DataFrame(results)

def add_differences_to_fields(data: dict, tolerance: float) -> dict:
    """
    Adds a 'diff' field to each entry in data['comparable_fields'] by:
    - identifying the first two numeric values per field
    - calculating their absolute difference (if possible)
    """
    for field, values in data.get("comparable_fields", {}).items():
        # Extract numeric values in order
        numeric_values = [
            float(v) for v in values.values()
            if isinstance(v, (int, float))
        ]

        if len(numeric_values) >= 2:
            diff = abs(numeric_values[0] - numeric_values[1])
            is_within_tolerance = diff <= tolerance
        else:
            diff = None
            is_within_tolerance = None
            print(f"Error: Could not calculate diff for field '{field}': {e}")

        values["diff"] = diff
        values["is_within_tolerance"] = is_within_tolerance

    return data

def apply_pass_fail_flag(data: dict, pass_criteria: str, tolerance: float) -> dict:
    fields = data.get("comparable_fields", {})
    diffs = []

    for field_data in fields.values():
        diff = field_data.get("diff")
        is_within = field_data.get("is_within_tolerance")
        if diff is not None:
            diffs.append(diff)

    if pass_criteria == "all_fields_within_tolerance":
        all_within = all(
            field.get("is_within_tolerance", False)
            for field in fields.values()
        )
        data["flag"] = "pass" if all_within else "fail"

    elif pass_criteria == "average_diff_below_tolerance":
        if not diffs:
            print("⚠️ No diffs computed — possible data issue (e.g., all fields missing or invalid).")
            avg_diff = float("inf")
        else:
            avg_diff = sum(diffs) / len(diffs)

        data["flag"] = "pass" if avg_diff <= tolerance else "fail"

    else:
        print(f"Error: Unknown pass_criteria: {pass_criteria}. Defaulting to fail.")
        data["flag"] = "fail"
    
    data["criteria_used"] = pass_criteria
    data["tolerance"] = tolerance

    return data
