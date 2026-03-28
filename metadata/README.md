# Module 5: Metadata Extraction
**Owner:** Saurabh Kumar

## Core Responsibility
To generate advanced lineage tracking across ML pipelines, we aggressively index statistical data (e.g., column distributions in a dataset blob). You write the raw analytical engine processing these unstructured static files into JSON data.

## Contracted Interface (`metadata/extractor.py`)

You are responsible for safely processing blobs immediately *after* they hit the server.

```python
def extract_metrics(file_path: str, mime_type: str) -> dict:
    """
    Accepts absolute storage paths for successfully committed Blobs.
    Returns structurally valid JSON mapping schema characteristics.
    """
    if mime_type == "text/csv":
        # Extract row count cleanly
        return {"row_count": 1052, "schema": {"id": "int", "value": "float"}}
        
    return {"row_count": 0, "schema": {}}
```

## Strict Constraints
1. **Crash Isolation:** You are dealing natively with user uploads. Datasets may be incredibly corrupted, maliciously engineered zip bombs, or violently misformatted. You must defensively `try...except` absolutely everything. If pandas raises a `ParserError`, you catch it internally, log a warning, and uniformly return `{}`. Your parser crashing cannot crash the overarching `POST /commit` API transaction!
2. **Read-Only Bound:** Do not open files utilizing "w" flags. You are accessing mathematically locked Blob shards.

## Execution
Execute mocked parsing checks locally simulating damaged CSV/Parquet files:
```bash
docker-compose run --rm dev-env pytest metadata/tests/test_extractor.py -v
```
