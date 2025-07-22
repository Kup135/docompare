import os
import json
import pandas as pd

def evaluate_agents_2_and_3_auto():
    eval_dir = input("Enter evaluation folder path (e.g., evaluation/eval_1_20250717_152715): ").strip()

    if not os.path.exists(eval_dir):
        print(f"❌ Folder not found: {eval_dir}")
        return

    result_path = next((os.path.join(eval_dir, f) for f in os.listdir(eval_dir)
                        if f.startswith("comparison_result") and f.endswith(".json")), None)
    gt_path = next((os.path.join(eval_dir, f) for f in os.listdir(eval_dir)
                    if f.startswith("GT_") and f.endswith(".json")), None)

    if not result_path:
        print("❌ comparison_result_*.json file not found.")
        return
    if not gt_path:
        print("❌ GT_*.json file not found.")
        return

    with open(result_path) as f:
        result_data = json.load(f)
    with open(gt_path) as f:
        gt_data = json.load(f)

    tolerance = result_data.get("tolerance", 1.0)
    gt_fields = gt_data["comparable_fields"]
    pred_fields = result_data["comparable_fields"]

    records = []
    for field, gt_vals in gt_fields.items():
        if field not in pred_fields:
            continue
        pred_vals = pred_fields[field]
        gt_csv = gt_vals.get("csv_value")
        gt_img = gt_vals.get("image_value")
        pred_csv = pred_vals.get("csv_value")
        pred_img = pred_vals.get("image_value")

        csv_ok = abs(gt_csv - pred_csv) <= tolerance if None not in (gt_csv, pred_csv) else False
        img_ok = abs(gt_img - pred_img) <= tolerance if None not in (gt_img, pred_img) else False
        csv_error = abs(gt_csv - pred_csv) if None not in (gt_csv, pred_csv) else None
        img_error = abs(gt_img - pred_img) if None not in (gt_img, pred_img) else None

        records.append({
            "field": field,
            "gt_csv": gt_csv,
            "pred_csv": pred_csv,
            "csv_within_tolerance": csv_ok,
            "csv_abs_error": csv_error,
            "gt_img": gt_img,
            "pred_img": pred_img,
            "img_within_tolerance": img_ok,
            "img_abs_error": img_error
        })

    df = pd.DataFrame(records)

    summary = {
        "agent2_accuracy": df["csv_within_tolerance"].mean(),
        "agent2_mae": df["csv_abs_error"].mean(),
        "agent3_accuracy": df["img_within_tolerance"].mean(),
        "agent3_mae": df["img_abs_error"].mean(),
    }

    summary_path = os.path.join(eval_dir, "agent2_3_summary.txt")
    csv_path = os.path.join(eval_dir, "agent2_3_detailed.csv")

    df.to_csv(csv_path, index=False)
    with open(summary_path, "w") as f:
        for k, v in summary.items():
            f.write(f"{k}: {v:.3f}\n")

    print(f"\n✅ Agent 2 & 3 evaluation saved to:\n- {csv_path}\n- {summary_path}")

if __name__ == "__main__":
    evaluate_agents_2_and_3_auto()
