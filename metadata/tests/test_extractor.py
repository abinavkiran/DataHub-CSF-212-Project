import os
import pytest
import pandas as pd
import json
import pyarrow as pa
import pyarrow.parquet as pq
from metadata.extractor import extract_metrics

def test_extract_metrics_csv(tmp_path):
    # Create sample CSV
    csv_file = tmp_path / "test.csv"
    df = pd.DataFrame({"age": [25, 30], "name": ["Alice", "Bob"]})
    df.to_csv(csv_file, index=False)

    result = extract_metrics(str(csv_file), "text/csv")
    assert result["row_count"] == 2
    assert len(result["columns"]) == 2
    assert result["columns"][0]["name"] == "age"
    assert result["format"] == "csv"

def test_extract_metrics_json(tmp_path):
    # Create sample JSON
    json_file = tmp_path / "test.json"
    data = {"id": [1, 2], "value": [10.5, 20.1]}
    with open(json_file, "w") as f:
        json.dump(data, f)

    result = extract_metrics(str(json_file), "application/json")
    assert result["row_count"] == 2
    assert result["columns"][1]["name"] == "value"
    assert result["format"] == "json"

def test_extract_metrics_parquet(tmp_path):
    # Create sample Parquet
    parquet_file = tmp_path / "test.parquet"
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["x", "y", "z"]})
    df.to_parquet(parquet_file)

    result = extract_metrics(str(parquet_file), "application/octet-stream")
    assert result["row_count"] == 3
    assert result["format"] == "parquet"

def test_extract_metrics_file_not_found():
    result = extract_metrics("non_existent.csv", "text/csv")
    assert "error" in result
    assert result["row_count"] == 0

def test_extract_metrics_invalid_format(tmp_path):
    # Create dummy text file
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("just some text")

    result = extract_metrics(str(txt_file), "text/plain")
    assert result["status"] == "unknown_format"
