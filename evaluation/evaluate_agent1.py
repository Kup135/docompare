import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import yaml
import shutil
from main import main as run_main
from datetime import datetime
import pandas as pd


def prompt_choice(prompt, min_val, max_val):
    while True:
        try:
            choice = int(input(prompt).strip())
            if min_val <= choice <= max_val:
                return choice
            print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Enter a number.")


def main():
    # Step 1: User input
    folder_num = input("Enter folder number (e.g., 2 for data/2): ").strip()
    data_dir = f"data/{folder_num}"
    criteria = input("Enter comparison criteria [all_fields_within_tolerance]: ").strip() or "all_fields_within_tolerance"
    tolerance = input("Enter tolerance [1.0]: ").strip() or "1.0"

    # Step 2: Run main.py with temporary config
    config = {
        "data_dir": data_dir,
        "pass_criteria": criteria,
        "tolerance": float(tolerance),
        "output_subdir": "results",
        "clearCache": True
    }
    os.makedirs("config", exist_ok=True)
    with open("config/temp_eval_config.yaml", "w") as f:
        yaml.dump(config, f)

    os.environ["CONFIG_PATH"] = "config/temp_eval_config.yaml"  # 👈 ADD THIS LINE

    print("\n🔁 Running main.py...")
    output_path = run_main()

    # Step 3: Copy cache to timestamped evaluation folder
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    eval_dir = f"evaluation/eval_{folder_num}_{ts}"
    os.makedirs(eval_dir, exist_ok=True)
    shutil.copytree(os.path.join(data_dir, "cache"), os.path.join(eval_dir, "cache"))

    # Step 4: Manual mapping of Agent 1 fields to GT
    print("\n🔍 Starting manual evaluation of Agent 1 (field matching)...")

    cached_fields_path = os.path.join(eval_dir, "cache", "comparable_fields.json")
    gt_path = os.path.join(data_dir, "GT", "comparable_fields.csv")

    with open(cached_fields_path) as f:
        model_fields = list(json.load(f)["comparable_fields"])

    gt_fields = pd.read_csv(gt_path)["field"].tolist()
    gt_used = set()
    matches = {}

    for i, field in enumerate(model_fields):
        print(f"\nModel Field {i+1}: {field}")
        print("GT Fields:")
        for j, gt in enumerate(gt_fields, start=1):
            used = " (used)" if j in gt_used else ""
            print(f"  {j}. {gt}{used}")
        print("  0. ❌ No match in GT")

        choice = prompt_choice("Your choice [number]: ", 0, len(gt_fields))
        if choice == 0:
            matches[field] = None
        elif choice not in gt_used:
            matches[field] = gt_fields[choice - 1]
            gt_used.add(choice)
        else:
            print("⚠️ GT field already matched. Skipping...")
            matches[field] = None

    matched_fields = [f for f, m in matches.items() if m is not None]
    recall = len(matched_fields) / len(gt_fields) if gt_fields else 0.0

    print(f"\n✅ Agent 1 Recall: {recall:.2f} ({len(matched_fields)} / {len(gt_fields)})")

    # Step 5: Save results
    with open(os.path.join(eval_dir, "agent1_matches.json"), "w") as f:
        json.dump(matches, f, indent=2)
    with open(os.path.join(eval_dir, "agent1_recall.txt"), "w") as f:
        f.write(f"Agent 1 Recall: {recall:.2f}\n")
        f.write(f"Matched {len(matched_fields)} out of {len(gt_fields)} GT fields\n")

    print(f"\n📝 Evaluation saved to: {eval_dir}")

    if output_path and os.path.exists(output_path):
        shutil.copy(output_path, os.path.join(eval_dir, os.path.basename(output_path)))
        print(f"📄 Copied result JSON to {eval_dir}")
    else:
        print("⚠️ Could not locate result file to copy.")

if __name__ == "__main__":
    main()
