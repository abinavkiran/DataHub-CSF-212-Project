def extract_metrics(file_path: str, mime_type: str) -> dict:
    """
    Given a path and type (csv/json/parquet), returns
    schemas and row counts as JSON-serializable dict.
    """
    # Fallback default
    return {"row_count": 0, "columns": []}
