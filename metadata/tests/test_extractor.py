from metadata.extractor import extract_metrics

def test_extract_metrics_fallback():
    result = extract_metrics("dummy.csv", "text/csv")
    assert result == {"row_count": 0, "columns": []}
