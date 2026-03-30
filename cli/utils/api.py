import requests

def check_hash(remote_url, file_hash):
    response = requests.get(f"{remote_url}/check_hash/{file_hash}")
    return response.json()


def upload_file(remote_url, file_hash, filepath):
    with open(filepath, "rb") as f:
        files = {"file": f}
        data = {"hash": file_hash}

        response = requests.post(
            f"{remote_url}/blobs",
            files=files,
            data=data
        )

    return response.json()


def create_commit(remote_url, payload):
    response = requests.post(
        f"{remote_url}/commit",
        json=payload
    )
    return response.json()