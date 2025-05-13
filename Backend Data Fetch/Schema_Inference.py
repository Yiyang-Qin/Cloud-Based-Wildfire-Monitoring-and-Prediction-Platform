import os
import pandas as pd
from collections import defaultdict

# ===== Configuration =====
DATA_DIR = "/path/to/your/noaa_data_2023"  # update this to your actual directory
SAMPLE_ROWS = 100  # number of rows to sample from each file

# ===== Inference Structures =====
all_columns = set()
column_type_counts = defaultdict(lambda: defaultdict(int))

# ===== Scan CSV Files =====
for file_name in os.listdir(DATA_DIR):
    if file_name.endswith(".csv"):
        file_path = os.path.join(DATA_DIR, file_name)
        try:
            df = pd.read_csv(file_path, nrows=SAMPLE_ROWS)
            all_columns.update(df.columns)
            for col in df.columns:
                dtype = pd.api.types.infer_dtype(df[col], skipna=True)
                column_type_counts[col][dtype] += 1
        except Exception as e:
            print(f"❌ Error in file {file_name}: {e}")

# ===== Print Summary =====
print("\n=== Inferred Schema Summary ===\n")
for col, type_counts in column_type_counts.items():
    total = sum(type_counts.values())
    top_type = max(type_counts.items(), key=lambda x: x[1])[0]
    print(f"{col}: {top_type} (dominant over {dict(type_counts)})")

# ===== Optional: Export to CSV for review =====
summary_df = pd.DataFrame(column_type_counts).fillna(0).astype(int).T
summary_df.to_csv("inferred_schema_summary.csv")
