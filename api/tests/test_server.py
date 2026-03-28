from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)

def test_upload_blob():
    response = client.post("/blobs/", files={"file": ("hello.txt", b"hello world")})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "hash": "dummy_hash_from_api"}
