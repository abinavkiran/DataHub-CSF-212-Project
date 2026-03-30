# Module 2 Update: Storage Engine & Deduplication

**Date:** March 30, 2026
**Owner:** Aditya Khemka 
**Status:** ✅ Complete & Verified

## Overview
The core implementation out of `storage/engine.py` meant to gracefully handle binary streams and SHA-256 deduplication for DataHub is now complete and verified. As mandated in the architecture spec, this module prevents large, duplicated sets of bytes from ballooning local network space.

## Implementation Details
We adopted a highly-efficient **Two-Pass Approach** for the Storage Engine to adhere to the strict `8192-byte` chunking constraint (zero RAM explosion):

1. **`put_blob` (Upload/Hash Phase):** 
   - Dynamically hashes the live byte stream chunk-by-chunk using `hashlib.sha256`.
   - Cross-references the generated SHA-256 Hex Hash against the physical filesystem `BLOB_DIR`.
   - If a duplicate blob is detected, the process instantly terminates and returns the hash $O(1)$ without rewriting bytes to disk.
   - If unique, the stream safely seeks back to `0`, streams into a new binary file, and formally locks the new blob to the index.
2. **`get_blob` (Download Phase):** 
   - Uses Python's native `Generator` yielding safely typed chunks.
   - Will immediately block/raise `ValueError` if corrupt or missing hashes are requested.

## Testing & Stability
Module 2 is fully containerized inside the Docker `dev-env` isolated network. 

Run the testing shell via:
```bash
docker-compose run --rm dev-env pytest storage/tests/test_engine.py -v
```

**Results:**
- `test_put_blob_new`: **Pass**
- `test_put_blob_duplicate`: **Pass** (Validation against `mtime` strictly confirms no disk IO overrides)
- `test_get_blob_success`: **Pass** 
- `test_get_blob_not_found`: **Pass**

**Coverage:** 4/4 Tests Passing (Execution time: <0.70s).
**Ready for integration by Module 4 (API Router).**
