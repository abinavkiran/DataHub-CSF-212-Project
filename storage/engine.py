import hashlib
import os
from typing import BinaryIO, Generator

BLOB_DIR = os.getenv("BLOB_DIR", "blobs/")
CHUNK_SIZE = 8192

# Ensure the BLOB_DIR exists
os.makedirs(BLOB_DIR, exist_ok=True)

def put_blob(data_stream: BinaryIO) -> str:
    """Reads a data stream, hashes via SHA-256 in 2 passes, writes locally, returns the hash."""
    hasher = hashlib.sha256()
    
    # Pass 1: Read the stream chunk by chunk to compute the SHA-256 hash without loading into RAM
    while True:
        chunk = data_stream.read(CHUNK_SIZE)
        if not chunk:
            break
        hasher.update(chunk)
        
    final_hash = hasher.hexdigest()
    blob_path = os.path.join(BLOB_DIR, final_hash)
    
    # If the blob already exists, simply return the hash (Deduplication)
    if os.path.exists(blob_path):
        return final_hash
        
    # Pass 2: Reset the stream and write the payload to disk
    data_stream.seek(0)
    with open(blob_path, "wb") as f:
        while True:
            chunk = data_stream.read(CHUNK_SIZE)
            if not chunk:
                break
            f.write(chunk)
            
    return final_hash

def get_blob(blob_hash: str) -> Generator[bytes, None, None]:
    """Returns an iterator streaming chunks of the stored file payload securely."""
    blob_path = os.path.join(BLOB_DIR, blob_hash)
    
    if not os.path.exists(blob_path):
        raise ValueError(f"Blob with hash {blob_hash} does not exist.")
        
    # Open file and yield chunks as a generator
    with open(blob_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk
