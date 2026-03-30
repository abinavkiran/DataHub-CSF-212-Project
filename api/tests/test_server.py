from fastapi.testclient import TestClient
from api.server import app
import uuid
import os

from infrastructure.db import Base, engine, SessionLocal, TreeEntry
from storage.engine import BLOB_DIR
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_upload_blob():
    response = client.post("/blobs/", files={"file": ("hello.txt", b"hello world")})
    assert response.status_code == 200
    assert "blob_hash" in response.json()

def test_check_hash_contract():
    upload_response = client.post("/blobs/", files={"file": ("exists.txt", b"dedupe-check")})
    blob_hash = upload_response.json()["blob_hash"]

    response_exists = client.get(f"/check_hash/{blob_hash}")
    assert response_exists.status_code == 200
    assert response_exists.json() == {"exists": True}

    response_missing = client.get("/check_hash/not_a_real_hash")
    assert response_missing.status_code == 200
    assert response_missing.json() == {"exists": False}

    assert os.path.exists(os.path.join(BLOB_DIR, blob_hash))

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

def test_create_commit_with_tree_entries():
    unique_hash = f"commit_{uuid.uuid4().hex[:8]}"
    tree_hash = f"tree_{unique_hash}"
    payload = {
        "commit_hash": unique_hash,
        "tree_hash": tree_hash,
        "parent_hash": None,
        "author": "Test Author",
        "message": "Commit with entries",
        "entries": [
            {"name": "data.csv", "object_hash": "blob_hash_1", "object_type": "blob"},
            {"name": "subdir", "object_hash": "tree_hash_2", "object_type": "tree"}
        ]
    }

    response = client.post("/commit/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "commit_hash": unique_hash}

    session = SessionLocal()
    try:
        rows = session.query(TreeEntry).filter(TreeEntry.tree_hash == tree_hash).all()
        assert len(rows) == 2
        names = {row.name for row in rows}
        assert names == {"data.csv", "subdir"}
    finally:
        session.close()
