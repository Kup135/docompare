import os
import json
import shutil
from utils.config_loader import load_config, OPENAI_API_KEY
from utils.file_loader import load_all_valid_files
from agents.agent1_comparable_fields import generate_comparable_fields
from agents.agent2_data_analytics import generate_csv_extraction_code
from agents.agent3_fill_Fields import fill_image_values
from utils.data_tools import safe_eval_snippets, apply_extraction_expressions, add_differences_to_fields, apply_pass_fail_flag
from utils.json_build import build_agent3_input_json, wrap_final, save_output_json
from utils.cache_tools import load_or_cache


def main():
    # Load config (e.g., tolerance, data_dir)
    config = load_config()
    # Optional: clear cache for temporary run
    if config.get("clearCache", False):
        temp_cache_dir = os.path.join(config.get("data_dir", "data"), "cache")
        if os.path.exists(temp_cache_dir):
            print("DEBUG: Removing cached agent outputs")
            shutil.rmtree(temp_cache_dir)
    tolerance = config.get("tolerance", 1.0)
    data_dir = config.get("data_dir", "data")  # fallback to "data" if not set
    output_subdir = config.get("output_subdir", "results")
    output_dir = os.path.join(data_dir, output_subdir)
    criteria = config.get("pass_criteria", "all_fields_within_tolerance")

    print(f"DEBUG: Loaded tolerance = {tolerance}")
    print(f"DEBUG: Using data directory = {data_dir}")

    # Define cache path
    cache_dir = os.path.join(data_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    comparable_fields_path = os.path.join(cache_dir, "comparable_fields.json")
    csv_snippets_path = os.path.join(cache_dir, "csv_snippets.json")
    image_values_path = os.path.join(cache_dir, "image_values.json")

    # Load files from data directory
    loaded_files = load_all_valid_files(data_dir)

    if loaded_files["errors"]:
        print("\nERRORS during file loading:")
        for err in loaded_files["errors"]:
            print("-", err)
        print("Aborting Agent 1...")
        return

    # Run Agent 1 - find comparable fields

    #legacy:
    # comparable_fields = generate_comparable_fields(
    #     loaded_files["csv_data"], loaded_files["image_data"]
    # )

    # Check for cached comparable fields
    comparable_fields = load_or_cache(
        comparable_fields_path,
        generate_comparable_fields,
        loaded_files["csv_data"],
        loaded_files["image_data"]
    )

    print("\nDEBUG: the comparable fields are:")
    print(comparable_fields)

    # Run Agent 2 - Generate code snippets
    code_snippets = load_or_cache(
        csv_snippets_path,
        generate_csv_extraction_code,
        loaded_files["csv_data"],
        comparable_fields
    )
    if code_snippets is None:
        raise ValueError("❌ Agent 2 returned invalid JSON. Cannot continue.")
    
    # Run expressions and get new structured CSV
    csv_results_df = apply_extraction_expressions(code_snippets, loaded_files["csv_data"])
    csv_results_df.to_csv(f"{data_dir}/results/csv_extracted_values.csv", index=False)
    print("DEBUG: Extracted values saved to 'results/csv_extracted_values.csv'")

    # Assume `agent3_input_json` is the dict with csv/image values
    agent3_input_json = build_agent3_input_json(csv_results_df)
    wrapped_input = wrap_final(agent3_input_json)

    print("DEBUG: Agent 3 input JSON:", wrapped_input)

    # Send to Agent 3
    final_output = load_or_cache(
        image_values_path,
        fill_image_values,
        wrapped_input,
        loaded_files["image_data"]
    )
    print("DEBUG: Agent 3 final output:", final_output)

    # calculate differences
    final_output_with_diffs = add_differences_to_fields(final_output, tolerance)
    print("DEBUG: Final output with differences:", final_output_with_diffs)

    # Apply pass/fail criteria
    final_output_with_flags = apply_pass_fail_flag(final_output_with_diffs, criteria, tolerance)
    print("DEBUG: Final output with flags:", final_output_with_flags)

    #save final output
    output = save_output_json(final_output_with_flags, output_dir, base_name="comparison_result")
    
    return output

if __name__ == "__main__":
    main()
