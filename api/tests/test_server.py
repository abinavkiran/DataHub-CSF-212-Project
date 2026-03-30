from fastapi.testclient import TestClient
from api.server import app
import uuid

from infrastructure.db import Base, engine
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_upload_blob():
    response = client.post("/blobs/", files={"file": ("hello.txt", b"hello world")})
    assert response.status_code == 200
    assert "blob_hash" in response.json()

def test_create_commit():
    unique_hash = f"commit_{uuid.uuid4().hex[:8]}"
    payload = {
        "commit_hash": unique_hash,
        "tree_hash": f"tree_{unique_hash}",
        "parent_hash": None,
        "author": "Test Author",
        "message": "Initial commit"
    }
    response = client.post("/commit/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "commit_hash": unique_hash}
