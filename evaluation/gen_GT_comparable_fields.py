import pandas as pd
import os
from datetime import datetime

def main():
    base_data_dir = "data"
    folder = input("Enter folder name under 'data/': ").strip()
    folder_path = os.path.join(base_data_dir, folder)
    assert os.path.exists(folder_path), f"Folder '{folder_path}' not found."

    # Create evaluation folder
    eval_dir = os.path.join(folder_path, f"GT")
    os.makedirs(eval_dir, exist_ok=True)
    csv_path = os.path.join(eval_dir, "comparable_fields.csv")

    print("\nEnter comparable fields one by one. Type 'done' when finished.")
    fields = []
    while True:
        field = input("Field name: ").strip()
        if field.lower() == "done":
            break
        if field:
            fields.append(field)

    df = pd.DataFrame(fields, columns=["field_name"])
    df.to_csv(csv_path, index=False)
    print(f"\n✅ Comparable fields saved to: {csv_path}")

if __name__ == "__main__":
    main()
