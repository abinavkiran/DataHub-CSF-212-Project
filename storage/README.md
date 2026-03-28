# Module 2: Storage Engine & Deduplication
**Owner:** Aditya Khemka

## Core Responsibility
This module manages the immutable physical storage layer (the Blobs directory) backing DataHub's DAG. Your code handles all deduplication mathematics using SHA-256 natively in Python.

## Contracted Interface (`storage/engine.py`)

You are required to export these precise python operations, which will be blindly trusted and consumed by Romir (Module 4: API).

```python
from typing import BinaryIO, Generator

def put_blob(data_stream: BinaryIO) -> str:
    """
    Reads a raw byte stream, computes its SHA-256 hash progressively,
    and writes the payload locally. If the hash already exists, it skips writing entirely!
    Returns the absolute blob_hash (e.g. 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855').
    """
    pass

def get_blob(blob_hash: str) -> Generator[bytes, None, None]:
    """
    Returns an iterator streaming chunks of the stored file payload securely.
    Throws a ValueError if the hash does not exist.
    """
    pass
```

## Strict Constraints
1. **Memory Efficiency:** Datasets can be GiB in size. You **must not** buffer `data_stream.read()` completely into RAM. Use `chunk_size = 8192` iterating loops.
2. **Immutability:** Once a blob is written, its contents are geometrically locked. You must never expose an "update_blob" method.

## Execution
Run your isolated tests leveraging the root docker instance:
```bash
docker-compose run --rm dev-env pytest storage/tests/test_engine.py -v
```
