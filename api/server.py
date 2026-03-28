from fastapi import FastAPI, UploadFile, File
import os

app = FastAPI(title="DataHub Node API")

@app.post("/blobs/")
async def upload_blob(file: UploadFile = File(...)):
    """Streams uploaded file directly to Module 2."""
    # To be integrated with storage.engine.put_blob
    return {"status": "success", "hash": "dummy_hash_from_api"}
