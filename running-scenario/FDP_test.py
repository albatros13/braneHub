import pandas as pd
import json
from pathlib import Path

# ---------------- CONFIG ----------------
CLIENT_FILES = {
    "client_1": "../data/client1.csv",
    "client_2": "../data/client2.csv"
}
SCHEMA_FILE = "schema.json"  # expected schema: column names & types
OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------- HELPERS ----------------
def read_data(file_path):
    """Read CSV file"""
    df = pd.read_csv(file_path)
    return df

def match_to_schema(df, schema):
    """Validate DataFrame against expected schema"""
    expected_cols = schema["columns"]
    missing_cols = [c for c in expected_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")
    # Optionally, enforce types
    for col, col_type in schema["columns"].items():
        df[col] = df[col].astype(col_type)
    return df

def filter_data(df, filters=None):
    """Apply optional filters (example: drop rows with NaNs)"""
    if filters is None:
        filters = {}
    filtered = df.dropna()
    return filtered

def perform_stat_test(df):
    """Simple test: count number of rows"""
    row_count = len(df)
    return {"row_count": row_count}

# ---------------- MAIN PIPELINE ----------------
def run_pipeline(client_name, data_file, schema_file):
    print(f"Processing {client_name}...")

    # Step 1: readData
    raw_data = read_data(data_file)

    # Step 2: matchToSchema
    with open(schema_file, "r") as f:
        schema = json.load(f)
    matched_data = match_to_schema(raw_data, schema)

    # Step 3: filterData
    filtered_data = filter_data(matched_data)

    # Step 4: performTest
    test_result = perform_stat_test(filtered_data)

    # Save result
    output_file = OUTPUT_DIR / f"{client_name}_test_result.json"
    with open(output_file, "w") as f:
        json.dump(test_result, f, indent=2)

    print(f"{client_name} done. Result: {test_result}")
    return test_result

# ---------------- RUN TEST ----------------
if __name__ == "__main__":
    results = {}
    for client_name, data_file in CLIENT_FILES.items():
        try:
            result = run_pipeline(client_name, data_file, SCHEMA_FILE)
            results[client_name] = result
        except Exception as e:
            print(f"Pipeline failed for {client_name}: {e}")

    print("\nSummary of all clients:")
    print(json.dumps(results, indent=2))
