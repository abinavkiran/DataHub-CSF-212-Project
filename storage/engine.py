import hashlib
import os

BLOB_DIR = os.getenv("BLOB_DIR", "blobs/")

def put_blob(data_stream) -> str:
    """Reads a data stream, hashes via SHA-256, writes locally, returns the hash."""
    hasher = hashlib.sha256()
    # Read chunk by chunk...
    # Write to BLOB_DIR/hash...
    return "dummy_hash_to_implement"

def get_blob(blob_hash: str):
    """Returns a file stream for a given hash."""
    pass
