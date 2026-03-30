import pandas as pd
import pyarrow.parquet as pq
import os
from typing import Dict, Any

def extract_metrics(file_path: str, mime_type: str) -> Dict[str, Any]:
    """
    Given a path and MIME type (text/csv, application/json, or application/octet-stream for Parquet),
    returns schemas (column names and types) and row counts as a JSON-serializable dict.
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found at {file_path}", "row_count": 0, "columns": []}

    try:
        # Handle CSV
        if mime_type == "text/csv" or file_path.endswith(".csv"):
            df = pd.read_csv(file_path, nrows=100) # Only read a sample for schema
            # Get total row count separately to avoid loading huge files into RAM
            row_count = sum(1 for _ in open(file_path)) - 1 # approximate for CSV
            return {
                "row_count": max(0, row_count),
                "columns": [{"name": col, "type": str(dtype)} for col, dtype in df.dtypes.items()],
                "format": "csv"
            }

        # Handle JSON
        elif mime_type == "application/json" or file_path.endswith(".json"):
            df = pd.read_json(file_path)
            return {
                "row_count": len(df),
                "columns": [{"name": col, "type": str(dtype)} for col, dtype in df.dtypes.items()],
                "format": "json"
            }

        elif "parquet" in mime_type or file_path.endswith(".parquet"):
            table = pq.read_table(file_path)
            return {
                "row_count": table.num_rows,
                "columns": [{"name": field.name, "type": str(field.type)} for field in table.schema],
                "format": "parquet"
            }

    except Exception as e:
        return {
            "error": str(e),
            "row_count": 0, 
            "columns": [],
            "status": "failed"
        }

    # Fallback default for unknown types
    return {"row_count": 0, "columns": [], "status": "unknown_format"}
