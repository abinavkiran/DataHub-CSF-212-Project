# Module 2: Storage Engine & Deduplication
**Contributer:** Aditya Khemka

## Overview
This module manages the immutable storage layer backing DataHub's Directed Acyclic Graph (DAG). It implements a high-efficiency **Content-Addressable Storage (CAS)** system that natively calculates SHA-256 hashes to prevent redundant disk writes and eliminate memory bloat.

## exported Operations

The following functions are exposed via `storage/engine.py` to be consumed by the API Gateway:

### `put_blob(data_stream: BinaryIO) -> str`
Writes an incoming data stream to disk while ensuring no data is ever duplicated.
- **Two-Pass Optimization:** It first hashes the stream chunk-by-chunk (`8192` bytes) without loading the entire stream into RAM.
- **Atomic Deduplication:** If the resulting SHA-256 hash already exists in the `BLOB_DIR`, it skips writing to the disk entirely, returning the hash instantly ($O(1)$).
- **Storage:** If the hash is completely new, it writes the chunks physically to `BLOB_DIR/<hash>`.
- **Returns:** The exact unique hex digest (e.g. `e3b0c44298fc1c...`) for the DAG pointer.

### `get_blob(blob_hash: str) -> Generator[bytes, None, None]`
Retrieves a previously stored file back to the network layer incrementally.
- Uses a Python `Generator` yielding safe `8192-byte` streaming chunks.
- Ensures massive machine-learning models can be pulled quickly without ram exhaustion.
- Immediately raises a `ValueError` if an invalid pointer is requested.

## Testing Execution
The storage engine limits side effects by containing everything into dockerized `pytest` generators.
```bash
docker-compose run --rm dev-env pytest storage/tests/test_engine.py -v
```
