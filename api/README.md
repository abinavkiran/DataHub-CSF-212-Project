# Module 4: High-Performance API Gateway
**Owner:** Romir Shetty

## Core Responsibility
Your logic governs the gateway mapping external HTTP payloads natively into DataHub's rigid database components. You act as the absolute integration boundary protecting Abinav's Database (Module 1) and Aditya's Storage bounds (Module 2).

## Contracted Interface (`api/server.py`)

You will construct async routes binding the physical payloads. Note how your implementation bridges directly outward:

```python
from fastapi import FastAPI, UploadFile, File, Depends
from infrastructure.db import get_db_session  # Abinav's DB session
from storage.engine import put_blob           # Aditya's chunk mechanism

app = FastAPI()

@app.post("/blobs/")
async def upload_blob(file: UploadFile = File(...)):
    """
    Routs Python's UploadFile StreamingBody straight into the put_blob logic
    without stopping in RAM. Returns the inserted hash locally.
    """
    hash_str = put_blob(file.file) 
    return {"blob_hash": hash_str}

@app.post("/commit/")
async def create_commit(payload: dict, session=Depends(get_db_session)):
    """
    Accepts rigid Tree Entry JSON payloads representing the newest snapshot.
    Leverages Abinav's Schema directly injecting Commits logically.
    """
    pass
```

## Strict Constraints
1. **Streaming Proxies:** Fast API's `UploadFile.file` exposes a generator byte-stream natively mirroring standard python FileIO. You must stream this seamlessly into `put_blob` without ever running `file.read()` which crashes containers encountering 50GB CSVs.

## Execution
Run Endpoint API checks spoofing concurrent connections cleanly:
```bash
docker-compose run --rm dev-env pytest api/tests/test_server.py -v
```
