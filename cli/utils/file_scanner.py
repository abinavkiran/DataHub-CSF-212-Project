import os

def scan_files():
    files = []

    for root, dirs, filenames in os.walk("."):
        if ".datahub" in root:
            continue

        for file in filenames:
            files.append(os.path.join(root, file))

    return files